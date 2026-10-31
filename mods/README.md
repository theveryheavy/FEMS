# Community mods

To add or update a mod, open a pull request in this directory. FEMS does not host mod files, and there is no live in-app catalog yet. A listing is just a way to help people find the author's project and download page.

## Add or update a listing

1. Make a folder named after your mod's unique ID, such as `mods/example-mod/`.
2. Add a `mod.json` file and a `README.md`.
3. Keep the mod itself in a repository or download location you control. Don't add game files or anything you don't have permission to share.
4. Open a pull request. To update a mod, change its existing folder. To remove it, delete that folder and explain why.
5. Maintainers will review the listing and may ask you to make changes before it is merged.

## `mod.json`

Use this as a starting point and replace the example values:

```json
{
  "id": "example-mod",
  "name": "Example Mod",
  "description": "A short description of the mod.",
  "author": "Mod Author",
  "repository": "https://github.com/example/example-mod",
  "download": "https://github.com/example/example-mod/releases",
  "version": "1.0.0",
  "license": "MIT",
  "gameVersions": ["False Echo version"],
  "femsVersions": ["Not yet available"],
  "categories": ["gameplay"],
  "tags": [],
  "dependencies": [],
  "screenshots": [],
  "icon": null
}
```

Use `null` or an empty list for optional information you don't have. Be specific about versions you've tested; say when something is untested. Keep the ID stable when updating a listing.

In the mod's `README.md`, explain what it changes, how to get it, known issues, compatibility, dependencies, and its license. Link to your source and download pages.

## Before opening a pull request

- Check that the folder name and `id` match and aren't already in use.
- Make sure `mod.json` is valid JSON and the links work.
- Include accurate compatibility and dependency details.
- State the mod's license and check that you have permission to share any screenshots, icons, or other material.
- Don't include game files, extracted game content, secrets, or other people's work without permission.

You keep ownership of your mod and choose its license. The FEMS MIT license does not apply to mod listings or third-party material. A listing is not a safety check or endorsement by FEMS. Use the [mod catalog issue form](https://github.com/theveryheavy/FEMS/issues/new?template=mod-submission.yml) to report a broken or potentially malicious listing. Don't install a mod you suspect is malicious.
