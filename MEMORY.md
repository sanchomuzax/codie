# Codie projekt — napló / memória

Időrendi napló a Codie BLE-vezérlés felélesztéséről. A tartós technikai referencia a
[CLAUDE.md](CLAUDE.md)-ben van; ide a döntések, mérföldkövek és incidensek kerülnek.

---

## 2026-07-07 — A robot feltámasztva

- A `csorbazoli/CodieController` repo átnézve. Megerősítve: 2016-os, félbehagyott Java PoC
  (Scratch 2 offline editor vezérlés), bluecove BT + jlhttp helyi HTTP szerver, robot- és
  szenzorparancsok, `resources/codie_scratch_project.sb2`.
- Az egyetlen issue (#1, 2019-03) a felhasználó (sanchomuzax) nyitotta. A szerző válasza:
  feladta, mert Windows-on nem volt BLE 4 driver, és a `CodieGateway` doksi hiányzott.
- **Kulcsfelismerés:** a protokoll nincs elveszve — a repo `DataPackage.java` +
  `CodieCommandType.java` tartalmazza a teljes visszafejtett MCU-frame formátumot. A hiányzó
  darab csak a PC→BLE út volt.
- Az RPi5 (`hci0`) BLE scan megtalálta: `DF:74:94:43:36:ED` "Codie". Connect sikeres, GATT
  feloldva → vendor service `52af0001`, write char `52af0002`, notify char `52af0003`.
- **Élő teszt:** beep-frame (`40 01 00 64 10 02 00 e8 03`) a `52af0002`-re → a Codie **sípolt**,
  ismételten. Determinisztikus, valódi vezérlés. A közvetlen APP→MCU frame-kódolás működik.
- Frame-formátum, parancs-ID-k és a csatlakozási recept rögzítve a CLAUDE.md-ben.
- Projekt inicializálva `/home/sancho/codie`-ban, privát GitHub repóba mentve.

### Nyitott szálak
- Szenzorolvasás notify-csatornán (akku `0x1069` lenne az első jó teszt — tényleges adat vissza).
- LED-vezérlés (`0x1065`) HSV-vel.
- Python/BlueZ wrapper a bluetoothctl-heredoc kiváltására.
- Mozgás CSAK töltőről levéve, külön jóváhagyással.
