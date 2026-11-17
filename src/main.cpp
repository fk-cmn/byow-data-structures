#include "engine.hpp"
#include <cctype>
#include <exception>

int main(int argc,char** argv){
    try{
        if(argc<2){std::cerr<<"Usage: relic_engine <seed 0..4294967295> [WASDF. history] [goal cell id]\n";return 2;}
        std::string raw=argv[1];
        if(raw.empty()||raw.find_first_not_of("0123456789")!=std::string::npos)throw std::invalid_argument("invalid seed");
        unsigned long long seed=std::stoull(raw);
        if(seed>4294967295ULL)throw std::invalid_argument("seed out of range");
        std::string history=argc>2?argv[2]:"";
        if(history.size()>20000||history.find_first_not_of("WASDF.")!=std::string::npos)throw std::invalid_argument("invalid history");
        int goal=argc>3?std::stoi(argv[3]):-1;
        relic::Game game(static_cast<uint32_t>(seed));game.replay(history);relic::jsonGame(std::cout,game,goal);std::cout<<'\n';
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 2;}
}
