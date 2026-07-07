#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${FLUENT_DIALOGUE_DORA_ROS2_DOCKER_IMAGE:-ros:jazzy-ros-base}"

if ! command -v docker >/dev/null; then
  echo "missing required command: docker" >&2
  exit 127
fi

docker run --rm \
  --network host \
  -e "FLUENT_DIALOGUE_DORA_ROS2_SMOKE_ROOT=/tmp/fluent_dialogue_dora_ros2_bridge_sidecar_smoke" \
  -v "${REPO_ROOT}:/work/fluent-dialogue-dora:ro" \
  "${IMAGE}" \
  bash -lc '
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y --no-install-recommends \
  python3-colcon-common-extensions \
  python3-pip \
  python3-venv

python3 -m venv --system-site-packages /tmp/fluent_dialogue_dora_ros2_smoke_venv
source /tmp/fluent_dialogue_dora_ros2_smoke_venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "/work/fluent-dialogue-dora/contracts/python"
python -m pip install "/work/fluent-dialogue-dora[dora]"

set +u
source "/opt/ros/${ROS_DISTRO}/setup.bash"
set -u
cd /work/fluent-dialogue-dora
scripts/run_ros2_bridge_sidecar_smoke.sh
'
