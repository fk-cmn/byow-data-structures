#!/usr/bin/env python3
"""首次运行编译 C++ 核心与官方 Java TileEngine；之后直接启动桌面窗口。"""
import argparse
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / 'build'
PLATFORM = platform.system() + '-' + platform.machine()
ENGINE = BUILD / ('relic_engine.exe' if platform.system() == 'Windows' else 'relic_engine')
JAR = BUILD / 'byow.jar'


def needs_build(output, inputs):
    return not output.exists() or any(p.stat().st_mtime > output.stat().st_mtime for p in inputs)


def build():
    BUILD.mkdir(exist_ok=True)
    tag = BUILD / 'platform.txt'
    correct_platform = tag.exists() and tag.read_text() == PLATFORM
    cpp = list((ROOT / 'src').glob('*'))
    if not correct_platform or needs_build(ENGINE, cpp):
        compiler = next((shutil.which(c) for c in ('clang++', 'g++', 'c++') if shutil.which(c)), None)
        if not compiler:
            raise RuntimeError('需要 C++17 编译器 clang++ 或 g++。Windows 可安装 MinGW-w64。')
        print('编译 C++ 数据结构核心……', flush=True)
        subprocess.run([compiler, '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic',
                        str(ROOT / 'src/main.cpp'), '-o', str(ENGINE)], check=True)
        tag.write_text(PLATFORM)
    java_sources = sorted((ROOT / 'java').rglob('*.java'))
    if needs_build(JAR, java_sources):
        javac, jar = shutil.which('javac'), shutil.which('jar')
        if not javac or not jar:
            raise RuntimeError('需要 JDK 17 或更高版本（须包含 java、javac、jar）。')
        classes = BUILD / 'classes'
        classes.mkdir(exist_ok=True)
        print('编译官方 TileEngine 与桌面入口……', flush=True)
        subprocess.run([javac, '--release', '17', '-encoding', 'UTF-8', '-d', str(classes),
                        *map(str, java_sources)], check=True)
        subprocess.run([jar, '--create', '--file', str(JAR), '--main-class', 'core.Main',
                        '-C', str(classes), '.'], check=True)


def main():
    parser = argparse.ArgumentParser(description='CS61B BYOW · C++ 数据结构大作业')
    parser.add_argument('--build-only', action='store_true')
    args = parser.parse_args()
    try:
        build()
        if args.build_only:
            print('编译完成。')
            return 0
        java = shutil.which('java')
        if not java:
            raise RuntimeError('需要 Java 17 或更高版本。')
        print('启动原版 TileEngine 桌面界面：N 新游戏，输入种子，S 开始。', flush=True)
        return subprocess.call([java, '-Dfile.encoding=UTF-8', f'-Dbyow.root={ROOT}',
                                '-jar', str(JAR)], cwd=ROOT)
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f'启动失败：{error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
