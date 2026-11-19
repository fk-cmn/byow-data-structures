#pragma once
#include "engine.hpp"

namespace relic {
inline void jsonString(std::ostream& out,const std::string& s){
    out<<'"';for(unsigned char c:s){if(c=='"'||c=='\\')out<<'\\'<<c;else if(c<32)out<<' ';else out<<c;}out<<'"';
}
template<class T> void jsonArray(std::ostream& out,const T& values){
    out<<'[';bool first=true;for(auto value:values){if(!first)out<<',';first=false;out<<int(value);}out<<']';
}
inline void jsonSearch(std::ostream& out,const SearchResult& r){
    out<<"{\"algorithm\":\""<<r.algorithm<<"\",\"path\":";jsonArray(out,r.path);
    out<<",\"order\":";jsonArray(out,r.order);
    out<<",\"cost\":"<<r.cost<<",\"expanded\":"<<r.order.size()<<",\"micros\":"<<r.micros<<'}';
}
inline void jsonGame(std::ostream& out,const Game& game,int goal=-1){
    const auto&w=game.world;
    out<<"{\"version\":1,\"seed\":"<<w.seed<<",\"width\":"<<WIDTH<<",\"height\":"<<HEIGHT
       <<",\"player\":"<<game.player<<",\"exit\":"<<w.exit<<",\"health\":"<<game.health
       <<",\"turn\":"<<game.turn<<",\"spent\":"<<game.spent<<",\"collected\":"<<game.collected
       <<",\"kills\":"<<game.kills<<",\"status\":\""<<game.status<<"\",\"message\":";
    jsonString(out,game.message);out<<",\"tiles\":";jsonArray(out,w.tile);
    out<<",\"visible\":";jsonArray(out,game.visible);out<<",\"explored\":";jsonArray(out,game.explored);
    out<<",\"crystals\":";jsonArray(out,game.crystals);out<<",\"potions\":";jsonArray(out,game.potions);
    out<<",\"floorCount\":"<<w.floorCount<<",\"treeWeight\":"<<w.treeWeight<<",\"rooms\":[";
    bool first=true;for(auto r:w.rooms){if(!first)out<<',';first=false;out<<"{\"x\":"<<r.x<<",\"y\":"<<r.y<<",\"w\":"<<r.w<<",\"h\":"<<r.h<<",\"center\":"<<r.center()<<'}';}
    out<<"],\"edges\":[";first=true;
    for(auto e:w.edges){if(!first)out<<',';first=false;out<<"{\"a\":"<<e.a<<",\"b\":"<<e.b<<",\"weight\":"<<e.weight<<",\"tree\":"<<(e.tree?"true":"false")<<'}';}
    out<<"],\"enemies\":[";first=true;
    for(auto e:game.enemies){if(e.health<=0)continue;if(!first)out<<',';first=false;
        out<<"{\"at\":"<<e.at<<",\"health\":"<<e.health<<",\"path\":";
        jsonArray(out,game.enemyPlan(e).path);out<<'}';}
    out<<"],\"goal\":"<<goal<<",\"searches\":[";
    if(w.walkable(goal)){first=true;for(const auto* algo:{"BFS","DIJKSTRA","ASTAR"}){
        if(!first)out<<',';
        first=false;jsonSearch(out,w.search(game.player,goal,algo));}}
    out<<"]}";
}
}
