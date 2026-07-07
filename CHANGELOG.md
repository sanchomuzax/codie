# Changelog

A projekt verziózása [semver](https://semver.org/lang/hu/) szerint.

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
