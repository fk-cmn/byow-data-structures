#include "session.hpp"
#include <iostream>
#include <stdexcept>

using namespace relic;

void testChallengeLimits() {
    GameSession countdown(2026, 7);
    const int clock = countdown.clocks.front();
    countdown.game.enemies.clear();
    countdown.game.player = countdown.game.world.adjacency[clock].front();
    const int delta = clock - countdown.game.player;
    countdown.act(delta == 1 ? 'D' : delta == -1 ? 'A' : delta == WIDTH ? 'S' : 'W');
    if (countdown.timeLimit() != 270 || countdown.clocks.size() != 1)
        throw std::runtime_error("last level clock must grant 30 seconds and disappear");
    countdown.updateTime(std::chrono::seconds(269));
    if (countdown.game.status != "playing") throw std::runtime_error("bonus time did not extend the round");
    countdown.updateTime(std::chrono::seconds(270));
    if (countdown.game.status != "lost") throw std::runtime_error("round did not end at zero");

    for (bool stepBudget : {true, false}) {
        GameSession limited(2026);
        auto& game = limited.game;
        game.enemies.clear();
        const auto destination = game.world.adjacency[game.player].front();
        const int direction = destination - game.player;
        const char command = direction == 1 ? 'D' : direction == -1 ? 'A' : direction == WIDTH ? 'S' : 'W';
        game.steps = stepBudget ? limited.limits.steps : 0;
        game.spent = stepBudget ? 0 : limited.limits.cost;
        limited.act(command);
        if (game.player == destination || game.status != "lost" || !game.limitFailure)
            throw std::runtime_error("exceeding a budget must end the round before moving");
    }
}

int main() {
    try {
        testChallengeLimits();
        GameSession session(2026);
        const int start = session.game.player;
        session.setTarget(session.game.world.exit);
        for (int algorithm = 0; algorithm < 3; ++algorithm) {
            session.setAlgorithm(algorithm);
            const auto path = session.route();
            if (path.path.empty() || path.path.front() != start || path.path.back() != session.game.world.exit)
                throw std::runtime_error("selected algorithm must return a route to target");
        }
        session.setAlgorithm(0);
        session.moveTowardTarget();
        if (session.game.turn != 1 || session.game.player == start || session.notice.empty())
            throw std::runtime_error("route action must move the game session");
        const int beforeWall = session.game.player;
        session.setTarget(-1);
        if (!session.route().path.empty()) throw std::runtime_error("invalid target must clear the route");
        session.moveTowardTarget();
        if (session.game.player != beforeWall || session.game.turn != 1)
            throw std::runtime_error("missing route must not alter game state");
        const int turns = session.game.turn;
        int wallNeighbor = WIDTH;
        while (wallNeighbor < CELLS &&
               (!session.game.world.walkable(wallNeighbor) ||
                session.game.world.walkable(wallNeighbor - WIDTH))) ++wallNeighbor;
        if (wallNeighbor == CELLS) throw std::runtime_error("fixture must contain a wall boundary");
        session.game.player = wallNeighbor;
        session.act('W');
        if (session.game.turn != turns || session.notice.find(u8"挡住") == std::string::npos)
            throw std::runtime_error("blocked movement must update UI feedback without consuming a turn");
        std::cout << "PASS: native game session integration\n";
    } catch (const std::exception& error) {
        std::cerr << "FAIL: " << error.what() << '\n';
        return 1;
    }
}
