# Weather – Enigma2 Plugin

Enigma2 plugin that shows weather data from the [Open-Meteo](https://open-meteo.com/) API.

---

## Features

- Multi-city management in settings
- Search cities using Open-Meteo geocoding
- Add, remove and reorder cities
- Main screen always displays the **first** configured city
- Current weather with condition icon, feels-like temperature, humidity, wind and precipitation
- 4-hour forecast with individual condition icons
- 5-day forecast with condition, min/max temperature, precipitation and wind
- Plugin icon variants for multiple menu aspect ratios
- Localized weather icons (sunny, cloudy, rain, snow, thunderstorm, fog, etc.)
- English UI texts with German translations

## Architecture

Core domain logic is decoupled from Enigma2 UI to simplify Kodi porting:

- `src/Weather/core/models.py`: data models
- `src/Weather/core/wmo.py`: weather code mapping
- `src/Weather/core/api_client.py`: HTTP client for Open-Meteo APIs
- `src/Weather/core/service.py`: weather orchestration and view shaping
- `src/Weather/store.py`: persistence for city list and cache
- `src/Weather/screens.py`: Enigma2 presentation layer
- `src/Weather/plugin.py`: Enigma2 entry and wiring

---

## Build & deploy

```bash
# 1. Copy .env.example to .env and enter your box credentials
cp .env.example .env

# 2. Build the .ipk package
make ipk

# 3. Build, upload and install on the box (no restart, no settings)
make install

# 4. Deploy initial city from .env to box
make copy-settings

# 5. Restart Enigma2
make apply

# 6. Or do all three steps at once
make deploy
```

---

## .env variables

| Variable | Description |
|----------|-------------|
| `BOX_HOST` | Enigma2 box IP or hostname |
| `BOX_USER` | SSH user (usually `root`) |
| `BOX_PORT` | SSH port (default `22`) |
| `WEATHER_CITY` | City name for the initial weather location. Resolved via Open-Meteo geocoding API during `make copy-settings`. |

Example:

```env
WEATHER_CITY=Böblingen
```

---

## Test requests

Use `test.http` to run geocoding and forecast calls against Open-Meteo.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Found a bug or have a suggestion for improvement? Please create an issue or pull request.

I appreciate everyone who supports me and the project! For any requests and suggestions, feel free to provide feedback.

<p>
  <a href="https://www.buymeacoffee.com/madoe21">
    <img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" height="50" alt="Buy Me a Coffee">
  </a>

  <a href="https://ko-fi.com/madoe21">
    <img src="https://storage.ko-fi.com/cdn/kofi3.png?v=3" height="50" alt="Ko-fi">
  </a>

  <a href="https://paypal.me/MartinD809">
    <img src="https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_111x69.jpg" height="50" alt="PayPal">
  </a>
</p>
