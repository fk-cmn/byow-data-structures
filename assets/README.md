# Native game assets

The eight explorers use transparent sheets in `heroes/`. Idle sheets contain 24 frames in six columns for the character picker, full-size detail portrait, and maze. Walk sheets contain eight frames in four columns for movement. Frames run left to right, then top to bottom. Keep the feet aligned and leave a little padding around each pose.

Run `python tools/draw-heroes.py` from the repository root with Pillow to export the hero sheets and GIFs to `build/qq-preview/eyes/`. Install the Windows package again after updating the sheets in this directory.

The four original guards use the horizontal four-frame PNG strips in `guards/`. The animated GIFs show the same frames and can be opened separately for preview.

`font.ttf` is the public-domain Tuffy font bundled with the SFML 3.0.2 examples. See `licenses/TUFFY.md`.

`ruins-zh.ttf` is a renamed Noto Sans SC subset that contains the Chinese interface glyphs and basic Latin characters. See `licenses/NotoSansSC-OFL.txt`.

`LXGWWenKaiLite-Medium.ttf` is the unmodified [LXGW WenKai Lite Medium](https://github.com/lxgw/LxgwWenKai-Lite/tree/7ee35a71b44fe60b81187dddd32b28478a1ff303/fonts/TTF) from commit `7ee35a71b44fe60b81187dddd32b28478a1ff303`, used for menu labels and character headings. See `licenses/LXGWWenKaiLite-OFL.txt`.

`LongCang-Regular.ttf` and `UnifrakturMaguntia-Book.ttf` are the Chinese title and English subtitle fonts. Both binaries are from Google Fonts commit `5bd87dfc525c8a0d1d8529d3684716e00c3fc59a`. See `licenses/LongCang-OFL.txt` and `licenses/UnifrakturMaguntia-OFL.txt`.

`gothic-hall.jpg` is the original 2880 × 1800 title background. Run `python tools/draw-gothic-hall.py` with Pillow and NumPy to regenerate it. SFML animates candlelight, floor mist and falling petals at runtime.

`menu-theme.flac` is the user-supplied William — Are you lost（梦核版） track for the course demo. The game streams it and loops it in the menus. If it cannot load, the game plays the original `ruins-theme.wav` loop. `expedition-theme.wav` plays after a player starts a level. The remaining WAV files are footsteps and combat cues. M toggles all audio.
