#!/bin/zsh
cd -- "$(dirname -- "$0")" || exit 1
python3 run.py
if [ $? -ne 0 ]; then
    read -r "?启动失败，按回车关闭。"
fi
