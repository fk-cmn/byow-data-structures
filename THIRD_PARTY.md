# 框架与代码来源

本项目参考 [CS61B Spring 2025 Project 3](https://sp25.datastructur.es/projects/proj3/) 的世界生成与交互要求，在其原版界面上实现适用于数据结构课程的大作业。新增代码在本次开发中使用了 AI 辅助，不应将整个工程声称为完全手写。

## 直接复用的官方源码

来自 [Berkeley-CS61B/proj3-skeleton-sp25](https://github.com/Berkeley-CS61B/proj3-skeleton-sp25)，版本 `39942fc637f707cbcbb6391694c91cf8ffe5d6cb`：

- `java/vendor/tileengine/TERenderer.java`
- `java/vendor/tileengine/TETile.java`
- `java/vendor/tileengine/Tileset.java`
- `java/vendor/utils/RandomUtils.java`

以上文件保留官方源码原样，用途是砖块、字体、调色和绘制，不包含本项目的地图生成、寻路或战斗算法。主菜单依据 [3B Gameplay 的菜单示例](https://sp25.datastructur.es/projects/proj3/proj3b/#task-4-main-menu) 实现。

`java/vendor/edu/princeton/cs/algs4/StdDraw.java` 来自 [Princeton algs4 官方源码仓库](https://github.com/kevin-wayne/algs4/blob/master/src/main/java/edu/princeton/cs/algs4/StdDraw.java)，保留原文件的作者声明与 GPL v3+ 许可，许可全文位于 `licenses/algs4-GPL-3.0.txt`。配套精简 OpenJDK 运行时的法律文件保留于 `BYOW.app/Contents/runtime/Contents/Home/legal/`。

每个第三方文件的本地 SHA-256 见 `java/vendor/SOURCES.json`，可用于确认没有改写官方界面库。

## 本项目实现

- `src/`：自实现循环队列、二叉最小堆、并查集，以及房间图 Kruskal、格子图 BFS/Dijkstra/A*、巡逻追踪、碰撞、战斗、收集、光线遮挡和确定性重放。
- `java/core/`：调用本地 C++ 可执行文件、读取其 JSON 状态，交给官方 TileEngine 绘制，并处理菜单和存档。
- `tests/`、启动与打包脚本：本项目的复现和验证材料。

没有使用往届学生的游戏解答源码；没有使用远程 API 代替本地数据结构算法。
