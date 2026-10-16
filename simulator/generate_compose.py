"""Generate an explicit 50-station Compose fleet, independent of container IDs."""
from pathlib import Path


def generate():
    lines = ["services:"]
    for index in range(50):
        lines += [f"  station-{index + 1:03d}:",
                  "    build: .", "    image: hcm-station-simulator:local",
                  "    restart: unless-stopped", "    volumes:",
                  "      - simulator-state:/state", "    environment:",
                  "      PYTHONUNBUFFERED: '1'", f"      NODE_INDEX: '{index}'",
                  f"      DEVICE_NAME: VN-HCM-{index + 1:03d}",
                  "      STATE_DIR: /state",
                  "      THINGSBOARD_HOST: ${THINGSBOARD_HOST:-10.0.1.200}",
                  "      PORT: ${PORT:-1883}",
                  "      PROVISION_KEY: ${PROVISION_KEY:-}",
                  "      PROVISION_SECRET: ${PROVISION_SECRET:-}"]
    return "\n".join(lines + ["volumes:", "  simulator-state:", ""])


if __name__ == "__main__":
    target = Path(__file__).with_name("compose.fleet.yml")
    target.write_text(generate(), encoding="utf-8")
    print(f"Generated {target.name}: 50 unique stations, persistent credentials")
