#!/usr/bin/env python3
"""打包源码、运行应用和验证材料，排除编译中间文件与个人存档。"""
from pathlib import Path
import os
import stat
import zipfile

ROOT = Path(__file__).resolve().parent


def main():
    destination = ROOT.parent / 'BYOW数据结构大作业_程序与源码.zip'
    keep_build = {'build/byow.jar', 'build/relic_engine', 'build/relic_engine.exe', 'build/platform.txt'}
    count = 0
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(ROOT.rglob('*')):
            relative = path.relative_to(ROOT)
            name = relative.as_posix()
            if '__pycache__' in relative.parts or path.name == '.DS_Store':
                continue
            if name.startswith('build/') and name not in keep_build:
                continue
            if name.startswith('saves/'):
                continue
            if not path.is_file() and not path.is_symlink():
                continue
            member = ROOT.name + '/' + name
            if path.is_symlink():
                info = zipfile.ZipInfo(member)
                info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
                archive.writestr(info, os.readlink(path))
            else:
                archive.write(path, member)
            count += 1
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('压缩包校验失败')
    size = destination.stat().st_size / 1024 / 1024
    if size >= 100:
        raise RuntimeError(f'超过 100 MiB：{size:.1f}')
    print(f'已打包并校验：{destination}\n{count} 个文件，{size:.1f} MiB')


if __name__ == '__main__':
    main()
