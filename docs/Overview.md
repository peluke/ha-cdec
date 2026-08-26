# Briceburg API

## Purpose

Home Assistant CDEC is a HACS custom integration that polls current California Data Exchange Center observations and creates Home Assistant sensor entities.

## Source

- Local source: `/Users/peluke/Documents/ChatGPT/Briceburg API`
- GitHub: `https://github.com/peluke/ha-cdec`
- Home Assistant domain: `briceburg_cdec`

## Configuration

The default CDEC station is `MBG`. Users can configure other station IDs and sensor numbers. CDEC updates observations every 15 minutes. The default wall-clock polling schedule runs at `:01`, `:16`, `:31`, and `:46` in Home Assistant's local timezone. The polling interval can be selected from clock-aligned choices, and the offset can be set from 0 through 14 minutes.

## Validation

GitHub Actions runs HACS validation and Home Assistant hassfest validation. Run `32603765768` passed both jobs on 2026-08-22.

## Related Notes

- [[Change Log]]
