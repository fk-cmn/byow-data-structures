#!/bin/zsh
cd -- "${0:A:h}/../.." || exit 1
if [[ ! -x build/byow_native ]]; then
    if ! command -v cmake >/dev/null; then
        print '首次构建原生版需要 CMake 3.24 或更新版本。'
        read -r '?按回车关闭。'
        exit 1
    fi
    cmake -S . -B build/flower-native -DCMAKE_BUILD_TYPE=Release &&
        cmake --build build/flower-native --target byow_native || exit 1
    exec ./build/flower-native/byow_native
fi
exec ./build/byow_native
