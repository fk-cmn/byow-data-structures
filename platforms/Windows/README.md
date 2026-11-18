# Windows

如果本机目录中已有 Windows 免安装包，可双击 `BYOW.exe` 运行；包内含 Java runtime 和 Windows C++ 引擎，无须另装 Java 或 Python。发行包不纳入 Git，因此新克隆的仓库默认没有该 exe。

从源码启动时，双击 `启动游戏.bat`。首次运行需要 Python 3.10+、JDK 17+ 和 C++17 编译器；若目录中存在 `BYOW.exe`，启动脚本优先运行免安装版，否则会调用仓库根目录的源码启动器。

免安装包是 Windows x86_64 构建产物。重新生成或更新包时，应在 Windows 上使用 JDK 17 的 `jpackage`，并将整个应用目录放在此处；大型 runtime 和二进制不纳入 Git。
