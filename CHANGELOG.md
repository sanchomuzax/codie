# Changelog

A projekt verziózása [semver](https://semver.org/lang/hu/) szerint.

## [0.2.0] — 2026-07-07

### Validated
- Előkerült a **hivatalos Codie BLE API v1.0** dokumentáció + `comApi.h` (a user régi SDK-jából,
  `docs/comApi.h`). A visszafejtett protokoll **teljesen igazolt**: INFO bájt, packet-struktúra,
  minden parancs-ID, drive-argumentumok, reply-formátum (reply-SEQ + nSuccess), RX/TX csatornák.

### Fixed
- **HSV skála 0-255-re javítva** (a Java repóból örökölt 0-100 hibás volt) — pl. a "zöld" korábban
  narancsnak látszott volna. `color_hsv` most a hivatalos 0-255 tartományt adja.
- LED-maszk `0x0FFF` (mind a 12 LED) — megerősítve helyesnek (a Java `0x08ff` hiba volt).

### Added
- Új parancsok a hivatalos enumból: `LedStartAnim` (0x1066), `AppConnected` (0x1067),
  `AppDisconnected` (0x1068), `BatteryGetVoltage` (0x106e); `SwitchToBootloader` (0x106d) csak
  konstansként, veszélyes.
- `CodieClient.battery_voltage()`, `app_connected()`, `app_disconnected()`.
- `scripts/led.py` — egyetlen LED-parancs lépésenkénti teszthez.
- `docs/comApi.h` — a hivatalos header referenciaként.

## [0.1.0] — 2026-07-07

### Added
- Python package (`codie/`) a Codie BLE vezérléséhez:
  - `protocol.py` — a csorbazoli/CodieController-ből visszafejtett wire-protokoll
    (frame kódolás/dekódolás, parancs-ID-k, szín-HSV), függőségmentes és unit-tesztelt.
  - `client.py` — `CodieClient` aszinkron bleak-kliens: connect, notify-feliratkozás,
    kérés/válasz párosítás SEQ↔REQSEQ alapján, aktuátor- és szenzormetódusok.
- `scripts/test_all.py` — teljes funkció-teszt harness (sensors|beep|led|drive szekciók).
- `tests/test_protocol.py` — unit tesztek (az élőben igazolt beep-frame ellen is).
- `.env.example` + `.env` (utóbbi gitignore-olt) a cím/adapter konfigurációhoz.
- README, CHANGELOG, VERSION, requirements.

### Verified
- Élő BLE kapcsolat és beep-parancs 2026-07-07-én (SpeakBeep), ismételhetően.
