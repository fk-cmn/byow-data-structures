#include "../src/json_protocol.hpp"
#include <deque>
#include <functional>
#include <queue>
#include <random>
#include <sstream>
#include <stdexcept>

using namespace relic;
int checks = 0;
void require(bool condition, const std::string& name) {
    ++checks;
    if (!condition) throw std::runtime_error(name);
}

// 参照实现使用标准库队列/优先队列，独立验证自实现容器及算法。
std::array<int, CELLS> referenceDistances(const World& w, int source, bool weighted) {
    std::array<int, CELLS> d; d.fill(INF); d[source] = 0;
    using Entry = std::pair<int, int>;
    std::priority_queue<Entry, std::vector<Entry>, std::greater<Entry>> q;
    q.push({0, source});
    while (!q.empty()) {
        auto [distance, u] = q.top(); q.pop();
        if (distance != d[u]) continue;
        auto p = point(u);
        for (auto delta : std::vector<Point>{{0,1},{0,-1},{1,0},{-1,0}}) {
            int x = p.x + delta.x, y = p.y + delta.y, v = y * WIDTH + x;
            if (x < 0 || x >= WIDTH || y < 0 || y >= HEIGHT || !w.walkable(v)) continue;
            int next = distance + (weighted ? w.cost(v) : 1);
            if (next < d[v]) { d[v] = next; q.push({next,v}); }
        }
    }
    return d;
}

int primWeight(const World& w) {
    int n = int(w.rooms.size()), total = 0;
    std::vector<int> best(n, INF); std::vector<bool> used(n); best[0] = 0;
    for (int i = 0; i < n; ++i) {
        int u = -1;
        for (int j = 0; j < n; ++j) if (!used[j] && (u < 0 || best[j] < best[u])) u = j;
        used[u] = true; total += best[u];
        for (int v = 0; v < n; ++v) if (!used[v]) {
            best[v] = std::min(best[v], manhattan(w.rooms[u].center(), w.rooms[v].center()));
        }
    }
    return total;
}

void validatePath(const World& w, int source, int target, const SearchResult& r) {
    require(!r.path.empty() && r.path.front() == source && r.path.back() == target, "path endpoints");
    int cost = 0;
    for (size_t i = 1; i < r.path.size(); ++i) {
        require(w.walkable(r.path[i]) && manhattan(r.path[i-1], r.path[i]) == 1, "path uses valid grid edge");
        cost += w.cost(r.path[i]);
    }
    require(cost == r.cost, "path cost is sum of entering costs");
    std::vector<int> unique = r.order;
    std::sort(unique.begin(), unique.end());
    require(std::adjacent_find(unique.begin(), unique.end()) == unique.end(), "no duplicated settled node");
}

void containers() {
    RingQueue<int> q(2); std::deque<int> reference;
    std::mt19937 random(61);
    for (int i = 0; i < 20000; ++i) {
        if (reference.empty() || random() % 3) { int v = int(random()); reference.push_back(v); q.push(v); }
        else { require(q.pop() == reference.front(), "ring queue FIFO after wrap/grow"); reference.pop_front(); }
    }
    while (!reference.empty()) { require(q.pop() == reference.front(), "queue drain"); reference.pop_front(); }
    require(q.empty(), "queue empty");
    bool threw = false; try { q.pop(); } catch (const std::logic_error&) { threw = true; }
    require(threw, "empty queue error");
    MinHeap<int, std::less<int>> heap;
    std::priority_queue<int, std::vector<int>, std::greater<int>> expected;
    for (int i = 0; i < 20000; ++i) {
        if (expected.empty() || random() % 2) { int v = int(random() % 100); heap.push(v); expected.push(v); }
        else { require(heap.pop() == expected.top(), "heap matches independent priority queue"); expected.pop(); }
    }
    while (!expected.empty()) { require(heap.pop() == expected.top(), "heap drain"); expected.pop(); }
    require(heap.empty(), "heap empty");
    threw = false; try { heap.pop(); } catch (const std::logic_error&) { threw = true; }
    require(threw, "empty heap error");
    DisjointSet sets(100);
    for (int i = 1; i < 100; ++i) require(sets.unite(i, i-1), "DSU joins distinct sets");
    for (int i = 0; i < 100; ++i) require(sets.find(i) == sets.find(0), "DSU compression");
    require(!sets.unite(2, 90), "DSU rejects cycle");
}

void worlds() {
    int differing = 0;
    for (uint32_t seed = 0; seed < 200; ++seed) {
        World w(seed), again(seed);
        require(w.tile == again.tile, "same seed generates same tiles");
        require(w.edges.size() == 14, "11 MST edges and 3 extra edges");
        require(w.treeWeight == primWeight(w), "Kruskal weight matches independent Prim");
        DisjointSet roomSets(12); int treeCount = 0;
        for (auto e : w.edges) if (e.tree) { ++treeCount; require(roomSets.unite(e.a,e.b), "MST is acyclic"); }
        require(treeCount == 11, "MST edge count");
        auto bfs = referenceDistances(w,w.start,false), cost = referenceDistances(w,w.start,true);
        int connected = 0;
        for (int id = 0; id < CELLS; ++id) {
            if (w.walkable(id)) { ++connected; require(bfs[id] < INF, "every floor reachable"); }
            Point p = point(id);
            if (p.x == 0 || p.x == WIDTH-1 || p.y == 0 || p.y == HEIGHT-1) require(!w.walkable(id), "solid world boundary");
        }
        require(connected == w.floorCount, "floor counter");
        for (auto room : w.rooms) {
            int target = room.center();
            auto b = w.search(w.start,target,"BFS"), d = w.search(w.start,target,"DIJKSTRA"), a = w.search(w.start,target,"ASTAR");
            validatePath(w,w.start,target,b); validatePath(w,w.start,target,d); validatePath(w,w.start,target,a);
            require(int(b.path.size())-1 == bfs[target], "BFS independent shortest hop count");
            require(d.cost == cost[target] && a.cost == cost[target], "Dijkstra/A* independent weighted optimum");
            require(a.order.size() <= d.order.size(), "A* expands no more than Dijkstra in tested world");
            if (b.cost > d.cost) ++differing;
        }
        require(w.search(w.start,0,"ASTAR").path.empty(), "wall is not a valid target");
    }
    require(differing > 0, "weighted terrain produces observable BFS/Dijkstra difference");
    World low(0), high(4294967295u);
    require(low.tile != high.tile, "boundary seeds distinct");
    std::cout << "Worlds: 200 seeds, 2400 targets, 7200 path validations; " << differing << " weighted differences\n";
}

void rebuild(World& w) {
    w.floorCount = 0;
    for (auto& row : w.adjacency) row.clear();
    for (int id = 0; id < CELLS; ++id) if (w.walkable(id)) {
        ++w.floorCount;
        Point p = point(id);
        for (auto d : std::vector<Point>{{1,0},{-1,0},{0,1},{0,-1}}) {
            int x=p.x+d.x,y=p.y+d.y;
            if(x>=0&&x<WIDTH&&y>=0&&y<HEIGHT&&w.walkable(y*WIDTH+x))w.adjacency[id].push_back(y*WIDTH+x);
        }
    }
}

Game fixture() {
    Game g(2026); g.world.tile.fill(0);
    for (int y = 2; y <= 9; ++y) for (int x = 2; x <= 9; ++x) g.world.tile[y*WIDTH+x] = 1;
    rebuild(g.world); g.enemies.clear(); g.crystals.clear(); g.potions.clear();
    g.player = Point{3,3}.id(); g.world.exit = Point{9,9}.id(); g.visible.fill(false); g.explored.fill(false); g.updateSight();
    return g;
}

void rules() {
    auto g = fixture();
    int at = g.player;
    g.act('W'); require(g.player == at-WIDTH, "W moves up");
    int turn = g.turn; g.act('W'); require(g.turn == turn && g.player == at-WIDTH, "wall collision consumes no turn");
    g.act('S'); require(g.player == at, "S moves down");
    g.world.tile[at+1] = 2; g.act('D'); require(g.spent == 7, "terrain movement accumulated cost 1+1+5");
    g = fixture(); g.enemies.push_back({g.player+1,g.player+1,g.player+2,2});
    at = g.player; g.act('D'); require(g.player == at && g.turn == 0, "cannot overlap live enemy");
    g.act('F'); require(g.enemies[0].health == 1 && g.health == 100, "adjacent hit");
    g.act('F'); require(g.kills == 1 && g.enemies[0].health == 0, "second hit kills");
    g.act('D'); require(g.player == at+1, "defeated enemy no longer blocks");
    g = fixture(); g.enemies.push_back({g.player+1,g.player+1,g.player+2,2});
    g.act('.'); g.act('.'); g.act('.'); require(g.health == 92, "guard damage only on third turn");
    g.health = 8; g.act('.'); g.act('.'); g.act('.'); require(g.status == "lost", "health zero loses");
    turn = g.turn; g.act('D'); require(g.turn == turn, "terminal state ignores actions");
    g = fixture(); g.potions.push_back(g.player+1); g.health = 50; g.act('D');
    require(g.health == 80 && g.potions.empty(), "healing station restores 30 and is consumed");
    g = fixture(); g.potions.push_back(g.player+1); g.act('D');
    require(g.health == 100 && g.potions.size() == 1, "full health does not waste potion");
    g = fixture(); g.world.exit = g.player+1; g.act('D'); require(g.status == "playing", "exit locked without collectibles");
    g.act('A'); g.collected = 4; g.act('D'); require(g.status == "won", "exit unlocks at four collectibles");
    g = fixture(); g.crystals.push_back(g.player+1); g.act('D'); g.act('A'); g.act('D');
    require(g.collected == 1 && g.crystals.empty(), "collectible only collected once");
    g = fixture(); at = g.player;
    g.world.tile[at+1]=0; g.updateSight();
    require(g.visible[at+1] && !g.visible[at+2], "wall visible but blocks sight behind it");
    require(!g.lineOfSight(at,at+3), "line of sight respects occlusion");
    require(g.visible[at] && g.explored[at], "avatar cell visible/explored");

    // 构造有两条路线的带权小图：直穿代价高，绕路步数多但更便宜。
    World w(1); w.tile.fill(0);
    int source=Point{2,2}.id(), target=Point{6,2}.id();
    for(int x=2;x<=6;++x){w.tile[2*WIDTH+x]=2;w.tile[3*WIDTH+x]=1;}
    w.tile[source]=w.tile[target]=1;rebuild(w);
    auto b=w.search(source,target,"BFS"),d=w.search(source,target,"DIJKSTRA"),a=w.search(source,target,"ASTAR");
    require(b.path.size()==5 && b.cost==16, "BFS chooses 4-hop costly route");
    require(d.path.size()==7 && d.cost==6 && a.cost==6, "weighted algorithms choose 6-hop cheaper route");
    w.tile[3*WIDTH+4]=0;w.tile[2*WIDTH+4]=0;rebuild(w);
    require(w.search(source,target,"BFS").path.empty() && w.search(source,target,"ASTAR").path.empty(), "unreachable target");
    require(w.search(source,source,"ASTAR").path.size()==1, "zero-length route");
}

void deterministicReplay() {
    std::string history;
    Random random(6140);
    const std::string commands="WASDF.";
    Game live(2026);
    for(int i=0;i<500;++i){char c=commands[random.between(0,5)];history+=c;live.act(c);}
    Game loaded(2026); loaded.replay(history);
    std::ostringstream a,b; jsonGame(a,live);jsonGame(b,loaded);
    require(a.str()==b.str(), "replay restores every exported gameplay field");
    Game before(2026);before.replay(history.substr(0,history.size()-1));before.act(history.back());
    std::ostringstream c;jsonGame(c,before);
    require(c.str()==a.str(), "undo and redo restore complete state");

    // 自动玩家仅用于测试：逐回合重新寻路，邻格有守卫则先攻击。
    for(uint32_t seed:{0u,2026u,4294967295u}){
        Game game(seed);
        for(int i=0;i<3000&&game.status=="playing";++i){
            bool adjacent=false;
            for(auto e:game.enemies)if(e.health>0&&manhattan(e.at,game.player)==1)adjacent=true;
            if(adjacent){game.act('F');continue;}
            int goal=game.crystals.empty()?game.world.exit:game.crystals.front();
            auto path=game.world.search(game.player,goal,"ASTAR").path;
            require(path.size()>1, "playthrough target reachable");
            int delta=path[1]-game.player;
            game.act(delta==1?'D':delta==-1?'A':delta==WIDTH?'S':'W');
        }
        require(game.status=="won"&&game.collected==4&&game.health>0, "complete game is winnable");
        std::cout<<"Playthrough seed "<<seed<<": won in "<<game.turn<<" turns, HP "<<game.health<<"\n";
    }
}

int main() {
    try {
        containers();worlds();rules();deterministicReplay();
        std::cout<<"PASS: "<<checks<<" assertions\n";
    }catch(const std::exception& error){std::cerr<<"FAIL after "<<checks<<": "<<error.what()<<'\n';return 1;}
}
