"""Validate rendered notification configs using Helm, promtool and amtool (no deployment/network sends)."""
import argparse
from pathlib import Path
import subprocess
import tempfile

import yaml


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--promtool", default="promtool")
    parser.add_argument("--amtool", default="amtool")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    rendered = subprocess.check_output(["helm", "template", "validation", str(root / "helm/infra-alerts"),
        "--set", "notifications.enabled=true", "--show-only", "templates/notifications-config.yaml"], text=True)
    data = yaml.safe_load(rendered)["data"]
    with tempfile.TemporaryDirectory(prefix="validate-discord-alerts-") as directory:
        path = Path(directory)
        rules = path / "notification-rules.rendered.yaml"
        rules.write_text(data["rules.yml"], encoding="utf-8")
        prometheus = yaml.safe_load(data["prometheus.yml"])
        prometheus["rule_files"] = [rules.as_posix()]
        (path / "prometheus.yml").write_text(yaml.safe_dump(prometheus), encoding="utf-8")
        # Validation-only URL; no receiver request is sent by check-config.
        (path / "webhook-url").write_text("https://discord.com/api/webhooks/123/test", encoding="utf-8")
        (path / "alertmanager.yml").write_text(data["alertmanager.yml"].replace(
            "/etc/discord/webhook-url", (path / "webhook-url").as_posix()), encoding="utf-8")
        tests = yaml.safe_load((root / "helm/infra-alerts/tests/notifications.test.yaml").read_text(encoding="utf-8"))
        tests["rule_files"] = [rules.as_posix()]
        (path / "tests.yml").write_text(yaml.safe_dump(tests), encoding="utf-8")
        for command in ([args.promtool, "check", "config", str(path / "prometheus.yml")],
                        [args.promtool, "test", "rules", str(path / "tests.yml")],
                        [args.amtool, "check-config", str(path / "alertmanager.yml")]):
            subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
