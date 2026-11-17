#!/usr/bin/env python3
"""编译并执行独立算法校验和 Java/C++ 桥接校验；无需启动 GUI。"""
import importlib.util
from pathlib import Path
import platform
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('byow_runner', ROOT / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def main():
    start = time.monotonic()
    runner.build()
    compiler = next(shutil.which(c) for c in ['clang++','g++','c++'] if shutil.which(c))
    test = ROOT / 'build' / ('core_tests.exe' if platform.system() == 'Windows' else 'core_tests')
    subprocess.run([compiler, '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic',
                    str(ROOT / 'tests/core_tests.cpp'), '-o', str(test)], check=True)
    subprocess.run([str(test)], check=True)
    subprocess.run(['javac', '--release', '17', '-encoding', 'UTF-8', '-cp', str(ROOT / 'build/byow.jar'),
                    '-d', str(ROOT / 'build/test-classes'), str(ROOT / 'tests/BridgeTests.java')], check=True)
    separator = ';' if platform.system() == 'Windows' else ':'
    subprocess.run(['java', '-cp', separator.join(map(str,[ROOT/'build/byow.jar',ROOT/'build/test-classes'])),
                    'BridgeTests', str(ROOT)], check=True)
    for seed in ['-1','4294967296','not-a-seed']:
        result = subprocess.run([str(runner.ENGINE),seed], capture_output=True)
        if result.returncode == 0:
            raise AssertionError(f'Invalid seed accepted: {seed}')
    print(f'All checks passed in {time.monotonic()-start:.2f}s.')


if __name__ == '__main__':
    main()
