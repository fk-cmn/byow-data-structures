#!/usr/bin/env python3
"""使用 JDK 官方 jlink/jpackage 生成可双击的 BYOW.app，内含精简运行时。"""
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import run


def main():
    if platform.system() != 'Darwin':
        raise SystemExit('此脚本用于 macOS；其他系统请使用 python3 run.py。')
    run.build()
    java_home = Path(subprocess.check_output(['/usr/libexec/java_home'], text=True).strip())
    inputs = run.BUILD / 'package-input'
    (inputs / 'build').mkdir(parents=True, exist_ok=True)
    shutil.copy2(run.JAR, inputs / 'byow.jar')
    shutil.copy2(run.ENGINE, inputs / 'build' / run.ENGINE.name)
    runtime = run.BUILD / 'runtime'
    if not runtime.exists():
        subprocess.run([str(java_home / 'bin/jlink'), '--add-modules', 'java.desktop', '--strip-debug',
                        '--no-header-files', '--no-man-pages', '--compress=zip-6', '--output', str(runtime)], check=True)
    output = run.ROOT / 'platforms' / 'macOS' / 'BYOW.app'
    output.parent.mkdir(parents=True, exist_ok=True)
    # 只替换本脚本产生、且包含已知主类配置的应用，防止误删同名文件。
    if output.exists():
        config = output / 'Contents/app/BYOW.cfg'
        if not config.is_file() or 'core.Main' not in config.read_text():
            raise SystemExit('已有同名应用，无法识别，未覆盖。')
        shutil.rmtree(output)
    # 在临时目录完成签名，避免 Finder 在桌面生成的元数据干扰 codesign。
    with tempfile.TemporaryDirectory(prefix='byow-package-') as staging:
        subprocess.run([str(java_home / 'bin/jpackage'), '--type', 'app-image', '--name', 'BYOW',
                        '--dest', staging, '--input', str(inputs), '--main-jar', 'byow.jar',
                        '--main-class', 'core.Main', '--runtime-image', str(runtime),
                        '--app-version', '1.0', '--mac-package-identifier', 'edu.byow.game',
                        '--java-options', '-Dbyow.root=$APPDIR',
                        '--java-options', '-Dfile.encoding=UTF-8'], check=True)
        shutil.move(str(Path(staging) / 'BYOW.app'), str(output))
    print(f'已生成：{output}')


if __name__ == '__main__':
    main()
