"""Exercise the actual workflow scripts against disposable local Git remotes."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
GIT = shutil.which("git")
BASH = str(Path(GIT).parent.parent / "bin/bash.exe") if os.name == "nt" else shutil.which("bash")


def script(component, step):
    workflow = (ROOT / "workflows" / f"{component}-ci.yml").read_text(encoding="utf-8")
    section = workflow.split(f"      - name: {step}\n", 1)[1]
    block = section.split("        run: |\n", 1)[1].split("\n      - name:", 1)[0]
    return textwrap.dedent(block)


@unittest.skipUnless(GIT and BASH and Path(BASH).is_file(), "Git and Bash required")
class GitOpsTests(unittest.TestCase):
    def test_dev_commit_and_image_only_promotion_leave_main_unchanged(self):
        for component in ("backend", "frontend"):
            with self.subTest(component=component), tempfile.TemporaryDirectory(prefix="gitops-") as directory:
                root = Path(directory)
                env = dict(os.environ, GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.autocrlf", GIT_CONFIG_VALUE_0="false")

                def git(cwd, *args):
                    return subprocess.run([GIT, *args], cwd=cwd, env=env, check=True,
                                          capture_output=True, text=True).stdout.strip()

                remote, seed, runner = root / "remote.git", root / "seed", root / "runner"
                git(root, "init", "--bare", str(remote))
                git(root, "init", "-b", "main", str(seed))
                git(seed, "config", "user.name", "Test")
                git(seed, "config", "user.email", "test@example.com")
                paths = {}
                for environment in ("dev", "prod"):
                    relative = f"helm/hcm-flood-{component}/environments/{environment}/values.yaml"
                    paths[environment] = relative
                    file = seed / relative
                    file.parent.mkdir(parents=True)
                    file.write_text(f'image:\n  repository: ghcr.io/tranduyloc895/hcm-flood-{component}\n  tag: old\n  digest: old\n', encoding="utf-8")
                git(seed, "add", ".")
                git(seed, "commit", "-m", "baseline")
                baseline = git(seed, "rev-parse", "HEAD")
                git(seed, "remote", "add", "origin", str(remote))
                git(seed, "push", "origin", "main", "main:dev")
                git(root, "clone", "--branch", "dev", str(remote), str(runner))
                output, summary = root / "output", root / "summary"
                env.update(IMAGE_TAG=baseline, IMAGE_DIGEST="sha256:" + "a" * 64,
                           GITHUB_OUTPUT=output.as_posix(), GITHUB_STEP_SUMMARY=summary.as_posix(),
                           GITHUB_RUN_ID="123", GITHUB_RUN_ATTEMPT="1", GITHUB_SERVER_URL="https://github.com",
                           GITHUB_REPOSITORY="example/test", SECURITY_GATE_MODE="report-only")
                subprocess.run([BASH, "-e", "-c", script(component, "Update dev image only")],
                               cwd=runner, env=env, check=True, capture_output=True, text=True)
                revision = output.read_text().strip().split("=", 1)[1]
                self.assertEqual(git(remote, "rev-parse", "dev"), revision)
                self.assertEqual(git(remote, "rev-parse", "main"), baseline)
                self.assertEqual(git(remote, "diff", "--name-only", baseline, revision), paths["dev"])
                # A concurrent update to dev must survive the promotion as well.
                (runner / "unrelated.txt").write_text("new dev code")
                git(runner, "add", "unrelated.txt")
                git(runner, "commit", "-m", "later dev change")
                git(runner, "push", "origin", "dev")
                fakebin = root / "bin"
                fakebin.mkdir()
                gh = fakebin / "gh"
                gh.write_text('#!/usr/bin/env bash\nprintf "https://github.com/example/test/pull/1\\n"\n', encoding="utf-8")
                gh.chmod(0o755)
                env.update(DEV_CONFIG_REVISION=revision, PATH=str(fakebin) + os.pathsep + env["PATH"])
                subprocess.run([BASH, "-e", "-c", script(component, "Open production promotion PR")],
                               cwd=runner, env=env, check=True, capture_output=True, text=True)
                candidate = f"codex/promote-{component}-123-1"
                self.assertEqual(git(remote, "rev-parse", "main"), baseline)
                self.assertEqual(git(remote, "diff", "--name-only", "main", candidate), paths["prod"])
                prod = git(remote, "show", f"{candidate}:{paths['prod']}")
                self.assertIn(env["IMAGE_TAG"], prod)
                self.assertIn(env["IMAGE_DIGEST"], prod)
                self.assertNotEqual(git(remote, "rev-parse", "dev"), baseline)
                self.assertEqual(git(remote, "show", f"dev:{paths['prod']}"), git(remote, "show", f"main:{paths['prod']}"))


if __name__ == "__main__":
    unittest.main()
