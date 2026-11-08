#!/bin/zsh
# 双击即清空本项目当前配置的本地业务数据。
PROJECT_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"
cd "$PROJECT_DIR" || exit 1
if [[ -x "$PROJECT_DIR/.venv/bin/python" ]]; then
  "$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/scripts/reset_demo_data.py" --yes
else
  python3 "$PROJECT_DIR/scripts/reset_demo_data.py" --yes
fi
RESET_RESULT=$?
echo
read '?按回车关闭窗口…'
exit "$RESET_RESULT"
