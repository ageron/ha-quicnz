# ha-quicnz

Home Assistant custom integration for [Quic Broadband](https://quic.nz/) (New Zealand).

Exposes your Quic broadband session and service details as Home Assistant entities via the [quicnz](https://github.com/ageron/quicnz) library.

> **Disclaimer:** This project is independent and community-maintained. It is not affiliated with, endorsed by, or supported by Quic Broadband / Vetta Trading Ltd in any way. Use it at your own risk.

---

## Features

| Entity | Type | Description |
|---|---|---|
| Connected | Binary sensor | `on` when the session status is `connected` |
| Session Status | Sensor | Raw session status string (e.g. `connected`) |
| Session Type | Sensor | `DHCP` or `PPPoE` |
| IPv4 Address | Sensor | Assigned public IPv4 address |
| IPv6 Prefix | Sensor | Assigned IPv6 prefix |
| Last RADIUS Update | Sensor | Timestamp of the last RADIUS accounting update |
| Session Expires | Sensor | Timestamp when the current session expires |
| Local Fibre Company | Sensor | LFC name (e.g. `Chorus`) |
| Service Status | Sensor | Service account status (e.g. `active`) |
| Data Cap | Sensor | Monthly data cap in GB (`unavailable` when uncapped) |
| Network Weather Map | Image | JPEG snapshot of the Quic network weather map |

Session data is refreshed every **5 minutes**; the weather map every **6 minutes** — both matching the Quic API's server-side cache TTLs.

---

## Requirements

- Home Assistant 2024.4.0 or newer
- A Quic Broadband account with an API key

## Getting an API key

Log in to the [Quic portal](https://account.quic.nz/), select a service, scroll to the bottom of the page and copy your API key. If the field is empty, click **Roll API Key** to generate one.

---

## Installation

### HACS (recommended)

1. Open HACS → **Integrations** → ⋮ menu → **Custom repositories**.
2. Add `https://github.com/ageron/ha-quicnz` with category **Integration**.
3. Search for **Quic Broadband** and install it.
4. Restart Home Assistant.

### Manual

1. Copy the `custom_components/quicnz` folder into your HA `config/custom_components/` directory.
2. Restart Home Assistant.

---

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Quic Broadband**.
3. Enter your API key. If your account has multiple services you will be asked to pick one.

Each service you add becomes its own device with all entities listed above.

---

## Displaying the weather map

The **Network Weather Map** image entity is not shown on the default dashboard automatically. To add it:

1. Go to your dashboard and click the **pencil** (edit) icon.
2. Click **Add card** and search for **Picture**.
3. Set **Entity** to `image.quic_<service_id>_network_weather_map`.
4. Save.

If you cannot find the entity, it may be disabled. To enable it:

1. Go to **Settings → Devices & Services → Quic Broadband → your device**.
2. Find **Network Weather Map** in the entity list (it may appear as *disabled*).
3. Click it, toggle **Enable**, and confirm.

Then add it to your dashboard as described above.

---

## Licence

[MIT](LICENSE)
