# Change Log

## 2026-08-26 - GitHub Actions maintenance

- Updated both validation jobs from `actions/checkout@v4` to `actions/checkout@v6`.
- Removed the deprecated Node.js 20 action runtime from the HACS and hassfest jobs.

## 2026-08-26

- Replaced the rolling coordinator interval with a wall-clock polling schedule.
- Set the default schedule to `:01`, `:16`, `:31`, and `:46`.
- Added a configurable polling offset from 0 through 14 minutes.
- Kept configurable polling intervals with clock-aligned choices.
- Added automatic integration reload after option changes.
- Added schedule unit tests and bumped the integration version to `0.3.0`.

## 2026-08-22

- Reviewed GitHub Actions run `32595122177`.
- Added `category: integration` to the HACS validation workflow.
- Moved configuration-flow abort strings under `config.abort`.
- Added an MIT license.
- Added the local HACS brand icon at `custom_components/briceburg_cdec/brand/icon.png`.
- Added the GitHub repository topics `home-assistant`, `hacs`, and `cdec`.
- Verified GitHub Actions run `32603765768`: the `hacs` and `hassfest` jobs passed.
