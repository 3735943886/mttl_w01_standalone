# MTTL-W01 2.0 Home Assistant Card

[한국어](README.md) | English

A Lovelace card for standalone firmware 2.0.x. It retains the entity mapping and features of the backend 1.0.68 card, with separate 2.0 file and registration names. The card version does not need to match each firmware patch release.

![Home Assistant card](HA_card.png)

## Installation

1. Copy [mttl-w01-2.0-card.js](mttl-w01-2.0-card.js) to Home Assistant's `/config/www/`.
2. Under **Settings → Dashboards → Resources**, add `/local/mttl-w01-2.0-card.js` as a **JavaScript Module**. Enable advanced mode in your user profile if the resource menu is hidden.
3. Refresh the browser and add a card.

```yaml
type: custom:mttl-w01-2-0-card
mac: 97c0123
mobile_two_rows: true
```

- `mac`: Last seven hexadecimal characters of the device MAC. Separators and case are normalized.
- `name`: Optional title; defaults to `MTTL XXXXXXX`.
- `mobile_two_rows`: Keep channels in a 2×2 layout on mobile when `true`. Default: one mobile column.
- `channel_names`, `channel_icons`: Arrays for four channel names/icons, also configurable in the visual editor.

Displays total power/energy/voltage/current and per-channel power/energy/current/temperature. Tap a channel header to toggle power or a sensor row to open more-info. Top sensors use a three-plus-two layout on mobile.

Enable MQTT in the device web UI first to create HA Discovery entities. Default entity IDs are required, for example `switch.mttl_97c0123_sw1` and `sensor.mttl_97c0123_current1`. Manually renamed entity IDs will not map automatically.

When migrating from the old card, update both the resource URL and YAML `type`. Continuing to use the existing 1.0.68 card is also supported.
