#pragma once
#include "engine.hpp"

namespace relic {
class GameSession {
    std::array<SearchResult, 3> searches{};
    void refreshRoutes() {
        static constexpr const char* names[] = {"BFS", "DIJKSTRA", "ASTAR"};
        for (int i = 0; i < 3; ++i) searches[i] = game.world.search(game.player, target, names[i]);
    }
public:
    struct Challenge { int seconds, steps, cost; };
    inline static constexpr std::array<Challenge, 8> challenges{{
        {480, 420, 490}, {445, 380, 445}, {410, 350, 410}, {375, 320, 385},
        {340, 300, 365}, {305, 280, 340}, {270, 260, 315}, {240, 240, 295}
    }};
    static constexpr int guardTier(int level, int guard) { return std::min(3, (level + guard) / 3); }
    static constexpr int guardDamage(int tier) { return 30 + 10 * tier; }
    static constexpr int clockCount(int level) { return level >= 5 ? 2 : 3; }
    Game game;
    std::vector<int> clocks;
    int bonusSeconds = 0;
    int target = -1;
    int algorithm = 2;
    std::string notice = u8"集齐四朵花，前往出口。";
    const Challenge limits;

    explicit GameSession(uint32_t seed, int level = 0) : game(seed), limits(challenges.at(level)) {
        game.expeditionLevel = level;
        game.stepLimit = limits.steps;
        game.costLimit = limits.cost;
        game.world.addExpeditionTerrain(level);
        for (std::size_t i = 0; i < game.enemies.size(); ++i) {
            auto& guard = game.enemies[i];
            guard.tier = guardTier(level, static_cast<int>(i));
            guard.health = 2 + guard.tier;
            guard.damage = guardDamage(guard.tier);
        }
        for (int room : {1, 6, 9}) {
            if (clockCount(level) == 2 && room == 1) continue;
            const auto& area = game.world.rooms[room];
            const int cell = Point{area.x, area.y}.id();
            clocks.push_back(cell);
        }
    }

    void setTarget(int cell) { target = game.world.walkable(cell) ? cell : -1; refreshRoutes(); }
    void setAlgorithm(int index) { if (index >= 0 && index < 3) algorithm = index; }
    const SearchResult& route() const { return searches[algorithm]; }
    const SearchResult& route(int index) const { return searches.at(index); }
    int timeLimit() const { return limits.seconds + bonusSeconds; }
    void updateTime(std::chrono::seconds elapsed) {
        if (game.status == "playing" && elapsed.count() >= timeLimit()) {
            game.status = "lost";
            notice = u8"时间用尽";
        }
    }
    void act(char command, bool jump = false) {
        const int turn = game.turn, health = game.health, flowers = game.collected, kills = game.kills;
        const int previous = game.player;
        game.act(command, jump);
        bool pickedClock = false;
        if (game.player != previous) {
            const auto clock = std::find(clocks.begin(), clocks.end(), game.player);
            if (clock != clocks.end()) {
                clocks.erase(clock);
                bonusSeconds += 30;
                pickedClock = true;
            }
        }
        refreshRoutes();
        if (game.status == "won") notice = u8"已找到出口！";
        else if (game.status == "lost") notice = game.limitFailure ? game.limitFailure : u8"生命耗尽。";
        else if (pickedClock) notice = u8"拾取时钟，延长 30 秒。";
        else if (game.collected > flowers) notice = u8"获得一朵花！" + std::to_string(game.collected) + " / 4";
        else if (game.health < health) notice = u8"受到守卫攻击，失去 " + std::to_string(health - game.health) + u8" 点生命。";
        else if (game.health > health) notice = u8"使用药剂，恢复生命。";
        else if (game.kills > kills) notice = u8"已击败守卫。";
        else if (command == 'F') notice = u8"挥动光刃，攻击相邻守卫。";
        else if (game.turn == turn) notice = jump ? u8"前方没有可安全跳过的碎石。" : u8"前方挡住了去路。";
        else if (game.player == game.world.exit) notice = u8"出口未开启，需集齐四朵花。";
        else notice = u8"在遗迹中寻找花朵。";
    }
    bool moveTowardTarget() {
        const auto path = route().path;
        if (path.size() < 2 || game.status != "playing") return false;
        for (const auto& enemy : game.enemies) if (enemy.health > 0 && manhattan(enemy.at, path[1]) <= 1) {
            notice = u8"守卫在附近，已停止自动行走。"; return false;
        }
        const int before = game.player, health = game.health;
        const int delta = path[1] - game.player;
        act(delta == 1 ? 'D' : delta == -1 ? 'A' : delta == WIDTH ? 'S' : 'W');
        return game.player != before && game.health >= health && game.status == "playing" && route().path.size() >= 2;
    }
    void attack() { act('F'); }
    void waitTurn() { act('.'); }
};
}
