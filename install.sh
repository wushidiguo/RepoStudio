#!/usr/bin/env bash
#
# RepoStudio - one-click installer for the `repo-to-video` Codex skill.
#
# Default: copies skills/repo-to-video into $CODEX_HOME/skills (or ~/.codex/skills)
#          and checks prerequisites.
# Flags:
#   --install-deps       install missing core tools via brew (macOS) / apt (Debian)
#   --install-tts        pip install edge-tts
#   --install-render     npm install the bundled Remotion template
#   --install-analysis   install codebase-memory-mcp
#   --full               all of the above
#   --target DIR         install into a custom skills directory
#
set -euo pipefail

SKILL_NAME="repo-to-video"
SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills"
TARGET=""
INSTALL_DEPS=0
INSTALL_TTS=0
INSTALL_RENDER=0
INSTALL_ANALYSIS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-deps) INSTALL_DEPS=1; shift ;;
    --install-tts) INSTALL_TTS=1; shift ;;
    --install-render) INSTALL_RENDER=1; shift ;;
    --install-analysis) INSTALL_ANALYSIS=1; shift ;;
    --full) INSTALL_DEPS=1; INSTALL_TTS=1; INSTALL_RENDER=1; INSTALL_ANALYSIS=1; shift ;;
    --target) TARGET="$2"; shift 2 ;;
    *) echo "Unknown flag: $1"; exit 1 ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
  TARGET="$CODEX_HOME/skills"
fi

SRC_DIR="$SOURCE/$SKILL_NAME"
DST_DIR="$TARGET/$SKILL_NAME"

if [[ ! -d "$SRC_DIR" ]]; then
  echo "[ERROR] Skill source not found: $SRC_DIR" >&2
  exit 1
fi

echo "==> Installing skill '$SKILL_NAME' into $TARGET"
mkdir -p "$TARGET"
rm -rf "$DST_DIR"
cp -R "$SRC_DIR" "$DST_DIR"
echo "    Copied -> $DST_DIR"

has() { command -v "$1" >/dev/null 2>&1; }

echo "==> Checking prerequisites"
for tool in git node npm python3 ffmpeg gh codebase-memory-mcp; do
  if has "$tool"; then
    echo "    $tool OK"
  else
    echo "    $tool MISSING"
  fi
done

if [[ "$INSTALL_DEPS" == "1" ]]; then
  echo "==> Installing missing core tools"
  if has brew; then
    for tool in git node ffmpeg gh; do
      has "$tool" || brew install "$tool"
    done
    has python3 || brew install python
  elif has apt-get; then
    sudo apt-get update
    sudo apt-get install -y git nodejs npm ffmpeg gh python3 python3-pip
  else
    echo "    No brew/apt found; install tools manually." >&2
  fi
fi

if [[ "$INSTALL_TTS" == "1" ]]; then
  echo "==> Installing edge-tts (CPU TTS fallback)"
  python3 -m pip install --upgrade edge-tts
fi

if [[ "$INSTALL_RENDER" == "1" ]]; then
  echo "==> Installing Remotion template dependencies"
  (cd "$DST_DIR/assets/remotion-template" && npm install)
fi

if [[ "$INSTALL_ANALYSIS" == "1" ]]; then
  echo "==> Installing codebase-memory-mcp"
  curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash
fi

echo "==> Install complete"
cat <<EOF

  Skill installed at: $DST_DIR

  Next steps:
  1. Restart your Codex session so the skill is discovered.
  2. Ask:
       Use \$repo-to-video to turn https://github.com/owner/repo into a 2-minute explainer video.

  Optional extras (per video job, on demand):
    - Deep analysis: codebase-memory-mcp (--install-analysis)
    - Best TTS:      Qwen3-TTS (needs GPU) - see skills/repo-to-video/references/tts.md
    - Diagrams:      codex plugin marketplace add cathrynlavery/diagram-design
EOF
