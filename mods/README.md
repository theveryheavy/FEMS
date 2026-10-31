# Community mod catalog

Community mods are added and updated through pull requests to this directory. There is no live FEMS catalog or download service yet; a merged entry is a reviewed repository listing, not a hosted mod or an application feature.

## Add or update a mod

1. Create a stable, lowercase directory under `mods/` using a unique mod ID, for example `mods/example-mod/`.
2. Add `mod.json` and `README.md` using the fields below. Include screenshots or an icon only when you have permission to share them.
3. Keep the mod's own source in its author-controlled repository. Provide a repository URL and a stable download/release URL if one exists; do not commit game files, extracted False Echo content, or third-party assets without redistribution permission.
4. Open a pull request against `main`. For an update, edit the existing directory and keep the mod ID stable. To remove an entry, delete its directory in a pull request and explain the request.
5. Maintainers review metadata, links, compatibility, licensing, and contribution rights. They may request changes before merging.

## Required `mod.json` fields

```json
{
  "id": "example-mod",
  "name": "Example Mod",
  "description": "A concise description of the mod.",
  "author": "Mod Author",
  "repository": "https://github.com/example/example-mod",
  "download": "https://github.com/example/example-mod/releases",
  "version": "1.0.0",
  "license": "MIT",
  "gameVersions": ["False Echo Demo version"],
  "femsVersions": ["Not yet available"],
  "categories": ["gameplay"],
  "tags": [],
  "dependencies": [],
  "screenshots": [],
  "icon": null
}
```

Replace example values with accurate information. Use `null` or an empty list when an optional URL, icon, tag, screenshot, or dependency is not available. Do not claim compatibility that has not been tested. The fields above are the initial catalog convention, not a promise that an application currently parses this file.

## `README.md`

Describe what the mod changes, installation requirements or steps if known, supported game/FEMS versions, known issues, dependencies, and where users can get help. Link to the author's repository and download page. Clearly state the mod's license and any separate licenses required by assets or dependencies.

## Review checklist

- The directory name and `id` match and are unique.
- JSON is valid and required metadata is present.
- Links point to the author's project or stable download page.
- Compatibility and dependencies are stated accurately.
- Licensing and redistribution rights are clear.
- No False Echo game files, extracted assets, secrets, or unauthorized third-party content are included.

Authors retain ownership and choose the license for their mods. FEMS's MIT license does not apply to mod folders or third-party material. Catalog review does not guarantee safety, compatibility, endorsement, or hosting by FEMS. Report broken or potentially malicious listings using the [mod catalog issue form](https://github.com/theveryheavy/FEMS/issues/new?template=mod-submission.yml); do not install a mod you suspect is malicious.
