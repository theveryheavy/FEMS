# Content format

Every content file is JSON (2-space indented in the project, packed compactly).
All text shown to the player is *indirected* through localisation keys, so a
new line of dialogue always needs a key in the four localisation tables.

---

## `data/dayNN.json` - day script

```json
{
  "day": "day01",
  "day_index": "1",
  "step_1": {
    "UID": "day01_ev_01",
    "triggers": [{ "type": "on_message_received", "event_id": "ng_begin" }],
    "actions": [
      { "type": "mono_nonskip", "text_key": "d01_t0_intro_01", "auto_ms": 5000.0 },
      { "type": "delay", "duration_sec": 1.0, "block_input": false }
    ]
  }
}
```

* `day`, `day_index` - identity used by the save system (`current_day`,
  `highest_unlocked_day`).
* `step_*` - ordered steps; the only trigger type used by the shipped content is
  `on_message_received` with an `event_id`. Steps fire once, in file order.
  The demo contains **353 steps** across `intro`/`day01`/`day02`/`day03`.
* Actions are a small scripting VM. The 47 action types used in the demo:

```
char_behavior      delay                dialogue_group      map_bubbles
char_leave         character_go_to_cabin set_flag           ready_for_next
cinema_bars        social_effect         sub_conning_crew   start_mission
mono_skip          cam_zoom_in           cam_zoom_out       branch_echo_value
tv_shrink          resume_character      central_message    depth_top
play_sound         encoding_tutorial_wait cam_pan           change_water_depth
disable_character  lights_flash          mono_nonskip       day01_cabin_intro
enable_character   depth_central         depth_side         do_drop
day_start          day_end               interior_lights    statement_signature_scene
set_mission_lose_type  lose_screen       cabin_lights_red   flashlight_cursor
...
```

Common fields: `type`, plus `text_key`/`loc`, `duration_sec`, `block_input`,
`notify` (raises an event that another step can trigger on), `flag`/`value`
for `set_flag`.

---

## `data/dayNN_dialogues.json`

```json
{ "groups": {
    "d01_m4_po_false": [
      { "side": "left",  "loc": "day_01_txt_dia_m4_po_false_01", "npc": "chief_po" },
      { "side": "right", "loc": "day_01_txt_dia_m4_po_false_02" }
    ] } }
```

`side` = left/right speaker, `loc` = localisation key, `npc` = character id
(see `characters.json`). Groups are referenced from `dialogue_group` actions.

---

## `data/dNN_missions.json` - puzzle definitions

One object per mission id (`m_d01_03`, `m_endless_encode_01`, ...). 23 missions
ship in the demo. Fields seen in the data:

```
character  message  type  lose_type  count_typing_mistakes  stamp_required
echo_from_checks  echo_paper  echo_capital  echo_side  msgDateTrue
ver_sender_key  verification_direction  isSenderGood  ver_receiver_key
isReceiverGood  check_sender_id  approvalCodeTrue  approvalCodeWord  check_date
senderIdTrue  senderIdCode  handoff_output  stamp_paper  stamp_side  time_sec
msgDateMode  decoded_message  character_pool  paper_requirements
```

These drive the ECHO machine: which stamps are required, whether the date is
true/late/false, cable and rotor settings, sender/receiver verification and the
lose conditions.

---

## `data/d99_rules.json` - rule set (endless mode)

```json
{ "papers": { "warning": {"action_false":"none","action_true":"none"}, ... },
  "rotors": {"mode":"default","left":"A","middle":"A","right":"A"},
  "date":   {"mode":"actual","late_allowed_sender_keys":[]},
  "cables": {"mode":"default","pairs":["","",""]},
  "sender_id_code": "SUBHUNT",
  "version": 1.0,
  "approval_code_word": "CITADEL",
  "stamps": { "output": {"echo": false, "color": "red"}, ... } }
```

Paper kinds: `warning`, `verification`, `private`, `output`, `input`.
`action_true` / `action_false`: `none` | `give` (hand the paper over).

---

## `data/characters.json` - NPC staging

```json
{ "characters": {
    "xo": {
      "points":  { "from": {"px": -54, "py": 261}, "to": {"px": 72, "py": 261} },
      "coming":  { "C1": "spr_xo_walk", "C2": "spr_xo_walk_to_us", "C3": "spr_xo_idle_front_01",
                   "duration_sec": 3.0 },
      "leaving": { "L1": "spr_xo_idle_front_01", "L2": "spr_xo_walk_from_us", "L3": "spr_xo_walk" }
    } } }
```

Sprite names refer to entries in `data.win` - so a custom character needs both
a JSON entry and (optionally) new sprites.

---

## Localisation tables

`data/localization/Localization XX.json`, `Endless XX.json`, `Frontline News
XX.json`, `War Diary XX.json`:

```json
[ ["txt_ui_mm_btn_newgame", "NEW GAME"],
  ["txt_task_decode", "Decode the message"] ]
```

* Ordered list of `[key, text]` pairs (the original files were CSV).
* Languages: **CS, DE, EN, ES, FR, ITA, KO, PL, RU**.
* `Localization` = 1 473 keys (UI + all in-game text), `Endless` = 2 390 keys
  (procedural message pool), `Frontline News` = 9, `War Diary` = 14.
* `FE Rules and Missions - Rules.json` is a plain matrix (rows x day columns)
  used by the rules cheat-sheet screen; it is not key-based.

Missing keys render as the raw key, so when adding content add the key to at
least EN (and ideally all nine languages).
