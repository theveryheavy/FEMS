# False Echo - technical architecture

## 1. Engine

| Property | Value |
|---|---|
| Engine | GameMaker Studio 2, runtime **2024.14.0.251** |
| Data file | `data.win` (FORM/GEN8, bytecode v17) |
| Compiler | **YYC** - GML is compiled to native x64 C++ |
| Executable | `False Echo.exe`, 60 MB, PE32+ / MSVC, no PDB |
| Steam | App 5072320 (demo), parent 4418080 |

Because the build is YYC, `data.win` has **no CODE chunk** - decompiling GML
bytecode is impossible, and the game logic must be analysed from the binary.

## 2. What lives where

### `data.win` (23 MB)
* 1 210 sprites, 2 264 texture-page items, 24 texture pages
* 81 shaders (GLSL, GLSL ES and HLSL9 source + compiled HLSL11/DXBC blobs)
* 18 bitmap fonts, 504 objects, 9 rooms, 163 sounds, 1 path
* 22 671 strings (STRG) - mostly asset names, debug messages and *dead copies*
  of the content blobs

**Important:** the STRG copies of the content blobs are *not* used by the game.
Editing them changes nothing (verified in-game). The live copies are in the EXE.

### `False Echo.exe`
* All GML string constants (about 24 340 `gml_Script_*` and 16 900
  `gml_Object_*` debug names, UI text, JSON content blobs)
* 129 926 functions described by the PE exception directory (`.pdata`)

Each GML string constant is materialised by a tiny "literal getter" function:

```
sub  rsp, 0x28
lea  rdx, [rip+disp]      ; <- the string bytes
lea  rcx, [rip+disp]
call 0x142593440          ; string construction
lea  rcx, [rip+disp]
add  rsp, 0x28
jmp  0x1429bdec8
```

That `lea rdx` is the single anchor used for patching and relocating content.

## 3. Content blob registry

The supported FEMS 0.9.0 profile (Steam build `26300950`) indexes 56
`base64(zlib(JSON + NUL))` strings in the EXE. Its STRG IDs shifted from the
older `26295067` profile; FEMS stores the build-specific mapping in
`fems_supported_build.json`.

| STRG id | logical file |
|---|---|
| 2602-2616 | characters, missions, rules, day data, dialogues, `env_days.json`, intro |
| 2617-2626 | localization/Endless (10 languages) |
| 2627 | localization/FE Rules and Missions - Rules |
| 2628-2637 | localization/Frontline News (10 languages) |
| 2638-2647 | localization/Localization (10 languages) |
| 2648-2657 | localization/War Diary (10 languages) |

The game also contains a *day editor*: several strings mention
`datafiles/data/day*.json` and "Save writes to datafiles/data/dayXX.json",
so developer builds can round-trip days to disk. In the retail demo the
`datafiles` folder is absent and the embedded copies are used.

## 4. Save format

`%LOCALAPPDATA%\False_Echo\save\savegame_slot_N.json`

```json
{"checksum":"<sha1>","version":1.0,"format":"false_echo_save","payload":"<json string>"}
```

`checksum = SHA1(payload)` - the payload is itself JSON (player stats, flags,
current day/step/event, social state). Rewriting a save only requires
recomputing that SHA-1 (implemented in `fedklib/saves.py`).

Other files: `settings.json`, `day_tutorial.json`, `citation_intro.json`,
`PREGAME_savegame_slot_0.json` (a snapshot used before a run).

## 5. Rendering / effects

* Windows path renders through D3D11; `data.win` stores 146 compiled DXBC
  blobs (`DXBC` magic) for the shaders.
* The project bundles two third-party GameMaker libraries whose shaders are
  visible in the dump: **Crystal Lighting Engine** (`__cle_*`) and
  **Post-Processing FX** (`__ppf_*`), plus game shaders
  (`shd_alpha_outline`, `shdr_mask_ui`, `_filter_underwater_shader`, ...).
* `eff_general_0.yytex` next to the EXE is a packaged effect texture used by
  the post-processing pack.

## 6. Packaging / DRM

* Steamworks extension 2.2.1 (`Steamworks_x64.dll`), `steam_init` is called at
  boot; `steam_restart_app_if_necessary` aborts the process when not launched
  from Steam.
* Running the local copy for testing works by setting
  `SteamAppId=5072320 SteamGameId=5072320` (what `fedk play` does).
