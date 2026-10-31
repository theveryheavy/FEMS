# Portable mod packages

`fedk mod` creates and handles `.femod` packages. A package is a ZIP archive
with a `mod.json` manifest and only the files the author chose to include. It
does not include the game executable, `data.win`, or original game assets.

## Create and build a mod

```powershell
cd modkit
python fedk.py mod create --name alternate-history --author "Your Name"
```

FEMS uses the active build profile named by `fems_supported_build.json` (for
the current release, `project/targets/steam-26300950`). Copy files you changed
from that profile's `content/` or `assets/` folders into the matching paths
under its `mods/alternate-history/` folder. For example, put
`day01_dialogues.json` at
`project/targets/steam-26300950/mods/alternate-history/content/data/day01_dialogues.json`.
Only add files the mod changes. Then build and inspect the package:

```powershell
python fedk.py mod build --name alternate-history
python fedk.py mod inspect --file project/targets/steam-26300950/build/alternate-history.femod
```

The manifest records the mod ID, name, version, author, description, paths,
and SHA-256 digest for every payload file. The packer checks the digest and
rejects unlisted files, duplicate paths, and paths outside `content/` and
`assets/` before applying anything.

To show a link and cover in the FEMS overlay, set `homepage` in `mod.json` to
an `https://` URL and add a PNG, JPEG, or WebP image at `media/cover.png`.
`fedk mod build` includes the image and its checksum in the package. The image
is display metadata; it is not written into the game.

```json
{
  "name": "Alternate History",
  "version": "1.0.0",
  "author": "Mod Author",
  "description": "A new story route with altered orders and dialogue.",
  "homepage": "https://example.com/alternate-history",
  "image": "media/cover.png"
}
```

## Apply a mod

```powershell
python fedk.py mod apply --file project/targets/steam-26300950/build/alternate-history.femod
python fedk.py pack --with-assets
```

Applying a package overlays its files in the working project. Existing target
files are backed up under `project/backup/mod-<id>-<timestamp>/`. Mods that
change the same file use last-applied-wins ordering; apply them in the desired
order. Build the executable with `fedk pack`; use `--with-assets` when the
package changed assets handled by the current asset builder.

## Use the FEMS overlay

Press **F8** to open or close the overlay. Add a `.femod` package with
**Add mod**, select it, then use **Enable Mod** or **Disable Mod** to queue the
change. The overlay shows its description, cover, version, author, packaged
file count, and homepage link. A queued change is marked **RESTART REQUIRED**.
Close the game and launch it again with `fems_play.cmd`; FEMS restores the clean
profile baseline, applies the selected packages in order, installs the rebuilt
game, and launches it. Launching from Steam directly does not run the companion
overlay or process queued selections.

## Included example mods

Three ready-to-enable packages are installed in the active profile's
`.fems/library/`. Their editable sources are in
`project/targets/steam-26300950/mods/`:

* `POLSKA` (`fems-example-polish-localization`) translates the interface, tutorial
  prompts, forms, message sheets, Frontline News, War Diary, and non-dialogue
  Endless-mode documents into Polish when English is selected. Spoken dialogue
  and character monologues are left untouched.
* `Example` (`fems-example-alternate-dialogue`) rewrites a Day 1 confrontation in all nine
  supported languages and includes the same Polish opening translations.
* `Uhhh IDK` (`fems-example-custom-mission`) changes the existing `m_d01_03` mission slot.
  The game does not register new mission IDs automatically, so this sample
  demonstrates a custom mission variant in a slot already referenced by the
  day script.

## Supported content and limits

Content JSON supports alternate dialogue, localization, day-event sequences,
missions, rules, and character staging inside the game's existing content
slots. The engine only recognizes its compiled action types and the shipped
game has a fixed set of day slots. A package can replace those data files, but
cannot make the native game recognize a new action type or register a new day
slot on its own.

Current automated asset packing supports same-size sprite frame replacement,
whole texture page replacement, and shader source replacement. Windows uses
precompiled shader bytecode, so source-only shader edits will not change the
Windows rendering. The project dump includes font and sound metadata, but
automated font, music/audio, room, object, and executable logic replacement
is not implemented yet. Files in those asset folders are archived faithfully
but will not affect the built game until a matching importer is added.

Game logic is a native C++ YYC build rather than GML bytecode. Existing
analysis notes are in `CODE_ATLAS.md`; supporting arbitrary new logic requires
reverse engineering and safe binary patching and is a separate, larger stage
of the mod suite.
