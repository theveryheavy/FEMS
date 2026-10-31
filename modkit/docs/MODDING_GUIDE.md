# Modding guide (recipes)

All commands run from `modkit/`. Content and asset paths below are relative to
the active profile `project/targets/steam-26300950/`. After an edit, run
`fedk pack --with-assets` and `install_fems.cmd`; the installer backs up the
original Steam files under `modkit/backups/`.

---

## 1. Change UI / story text

1. `fedk extract` (once)
2. Edit `project/targets/steam-26300950/content/data/localization/Localization EN.json`
3. `fedk pack && install_fems.cmd`

For translation work use CSV instead:

```bash
fedk localize export --out mytranslation
# edit "Localization - PL.csv" etc. in Excel / LibreOffice (UTF-8)
fedk localize import --dir mytranslation
fedk pack && install_fems.cmd
```

Keys are `[key, text]` pairs; you may add new keys at the end.

---

## 2. Rewrite a day's script

`project/targets/steam-26300950/content/data/day01.json` holds the ordered steps. Example - insert a
new step at the start of day 1:

```json
"step_0_intro": {
  "UID": "day01_custom_intro",
  "triggers": [{"type": "on_message_received", "event_id": "ng_begin"}],
  "actions": [
    {"type": "mono_nonskip", "text_key": "my_custom_line", "auto_ms": 4000.0}
  ]
}
```

and add `["my_custom_line", "Your new line here."]` to the localisation table.

---

## 3. Create a custom campaign / extra day

```bash
fedk campaign new --day 09 --index 4 --lang EN
```

Creates `day09.json`, `day09_dialogues.json`, `d09_missions.json`,
`d09_rules.json`, seeds localisation keys, and registers the files in the
content index so `pack` ships them.

The shipped demo exposes `day_index` 0-3; `d99` is the endless mode. A new
`day_index` becomes reachable when the day-selection list is extended
(`Localization` keys starting with `txt_ui_day`), or by editing a save's
`highest_unlocked_day`.

---

## 4. Replace sprites / textures

```bash
# same-size frame replacement (composited into the existing atlas slot)
project/targets/steam-26300950/assets/sprites/spr_menu_icon_newgame/0.png   <- overwrite
fedk pack --with-assets && install_fems.cmd
```

* `project/targets/steam-26300950/assets/textures/Texture N.png` are whole texture pages - editing one
  replaces every sprite on that page.
* `project/targets/steam-26300950/assets/sprites/<sprite>/<frame>.png` are individual frames; they are
  written back into the page at their original position.
* Frame size must match the original. To change a sprite's size you must repack
  the atlas (UndertaleModTool GUI: *Sprite editor -> Import*).

---

## 5. Shaders

Sources live in `project/targets/steam-26300950/assets/shaders/<name>/`
(`vertex_glsl_es.txt`, `fragment_glsl_es.txt`, `vertex_glsl.txt`,
`fragment_glsl.txt`, `vertex_hlsl9.txt`, `fragment_hlsl9.txt`).

`fedk pack --with-assets` writes them back into `data.win`.

**Caveat:** the Windows build renders with D3D11, which uses the precompiled
DXBC blobs (`HLSL11_*` in the shader record), not the GLSL text. For visual
shader mods on Windows you must also compile the HLSL with `fxc.exe`
(Windows SDK) using GM's entry points (`main` for vertex, `main` for pixel) and
inject the resulting `DXBC` blob with UndertaleModTool
(*Shader -> HLSL11 Vertex/Pixel Data*). GLSL edits do take effect in the
macOS/Linux/Android exports.

Effects worth playing with: `__ppf_shRenderVHS`, `__ppf_shRenderChromAber`,
`__ppf_shRenderBloom`, `_filter_underwater_shader`, `shdr_mask_ui`.

---

## 6. Save editing

```bash
fedk save list
fedk save show                            # full payload
fedk save unlock --day 3
fedk save set --path flags.day03_power_issue --value true
fedk save set --path social_state.ship.crew_morale --value 100
```

The checksum is `SHA1(payload)` and is recomputed automatically.

---

## 7. Rules / mission data

See [CONTENT_FORMAT.md](CONTENT_FORMAT.md). The fastest way to make the game
easier/harder is `d99_rules.json` (`papers[*].action_true`, `stamps[*].echo`,
`date.mode`, `cables.mode`) and the mission objects in `d*_missions.json`
(`lose_type`, `count_typing_mistakes`, `time_sec`, `stamp_required`).

---

## 8. Adding brand-new content keys

Because the game resolves text through a key->string dictionary built from the
localisation tables, you can invent keys freely. Keep them unique and
`snake_case`, and add them to every language you care about.

---

## 9. Testing loop

```bash
fedk pack --with-assets && install_fems.cmd && fedk play
```

`fedk play` sets `SteamAppId=5072320 SteamGameId=5072320` so the local copy
starts without going through the Steam client (Steam itself must be running).

If the game refuses to boot after a mod, restore the newest backup:

```
modkit/project/backup/<timestamp>/
```
