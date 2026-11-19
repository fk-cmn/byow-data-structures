#include "music.hpp"

#include <array>

#define MINIAUDIO_IMPLEMENTATION
#define MA_NO_ENCODING
#define MA_NO_MP3
#define MA_NO_CAPTURE
#include <miniaudio.h>

namespace {
struct Clip {
    ma_sound sound{};
    bool ready = false;

    ~Clip() { if (ready) ma_sound_uninit(&sound); }

    void load(ma_engine& engine, const std::filesystem::path& path, float volume,
              bool loop = false, ma_uint32 flags = MA_SOUND_FLAG_DECODE) {
#ifdef _WIN32
        const auto result = ma_sound_init_from_file_w(&engine, path.c_str(), flags, nullptr, nullptr, &sound);
#else
        const auto result = ma_sound_init_from_file(&engine, path.c_str(), flags, nullptr, nullptr, &sound);
#endif
        ready = result == MA_SUCCESS;
        if (!ready) return;
        ma_sound_set_volume(&sound, volume);
        ma_sound_set_looping(&sound, loop);
    }

    void stop() { if (ready) ma_sound_stop(&sound); }

    void play(bool restart = false, float pitch = 1.f) {
        if (!ready) return;
        if (restart) {
            stop();
            ma_sound_seek_to_pcm_frame(&sound, 0);
        }
        ma_sound_set_pitch(&sound, pitch);
        ma_sound_start(&sound);
    }
};

struct AudioEngine {
    ma_engine engine{};
    bool ready = ma_engine_init(nullptr, &engine) == MA_SUCCESS;
    ~AudioEngine() { if (ready) ma_engine_uninit(&engine); }
};
}

struct Music::Playback {
    AudioEngine audio;
    Clip menu, expedition;
    std::array<Clip, 5> effects;
    bool inExpedition = false;
    unsigned steps = 0;

    Clip& theme() { return inExpedition && expedition.ready ? expedition : menu; }
};

Music::Music(const std::filesystem::path& originalTheme, const std::filesystem::path& menuTheme) {
    auto player = std::make_unique<Playback>();
    if (!player->audio.ready) return;
    auto& engine = player->audio.engine;
    const auto root = originalTheme.parent_path();
    player->menu.load(engine, menuTheme, .30f, true, MA_SOUND_FLAG_STREAM);
    if (!player->menu.ready) player->menu.load(engine, originalTheme, .42f, true);
    player->expedition.load(engine, root / "expedition-theme.wav", .42f, true);
    constexpr std::array names{"step-stone.wav", "step-sand.wav", "blade-miss.wav", "blade-hit.wav", "guard-hit.wav"};
    for (std::size_t i = 0; i < names.size(); ++i)
        player->effects[i].load(engine, root / names[i], i < 2 ? .30f : .44f);
    player->theme().play();
    playback = std::move(player);
}

Music::~Music() = default;

void Music::toggle() {
    if (!playback) return;
    silent = !silent;
    ma_engine_set_volume(&playback->audio.engine, silent ? 0.f : 1.f);
}

void Music::setExpedition(bool active) {
    if (!playback || playback->inExpedition == active) return;
    playback->theme().stop();
    playback->inExpedition = active;
    playback->theme().play();
}

void Music::play(Cue cue) {
    if (!playback || silent) return;
    const bool step = cue == Cue::Stone || cue == Cue::Sand;
    const float pitch = step ? (.93f + (.035f * (playback->steps++ % 5))) : 1.f;
    playback->effects[static_cast<std::size_t>(cue)].play(true, pitch);
}
