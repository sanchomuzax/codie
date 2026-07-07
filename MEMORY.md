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

### v0.1.0 — bleak-kliens + szenzorok élőben igazolva
- Elkészült a Python package: `codie/protocol.py` (frame encode/decode, parancs-ID-k,
  szín-HSV) + `codie/client.py` (aszinkron bleak `CodieClient`, notify-feliratkozás,
  SEQ↔REQSEQ kérés/válasz párosítás). 15 unit teszt zöld (az igazolt beep-frame ellen is).
- **Szenzorok mind válaszolnak** (notify `52af0003`), a dekódolás bájtra pontos:
  akku 5%, fény 4041, vonal (3895, 3808), szonár 81 mm, mikrofon 633.
  Válaszfejléc: INFO=0x10 (MCU→APP), CMD felső bájt 0x80-nal jelölt, ARGLEN a REQSEQ-et is
  beleszámolja, a hasznos adat a 9. bájttól — pontosan a Java processResponse szerint.
- Megjegyzés: az akku a mérésnél 5% volt (töltőn) — a mozgásteszt motorjaira ez kevés lehet.

### v0.2.0 — hivatalos SDK előkerült, protokoll validálva
- A user talált egy régi SDK-t (`/home/sancho/Downloads/codie.zip`): benne a **hivatalos Codie
  BLE API v1.0** HTML doksi, `comApi.h`, Qt/C++ példák (Simple + Complex), és maga a
  **CodieGateway_dotNet.exe** (a 2019-ben "hiányzó" darab!).
- A visszafejtett protokoll **teljesen igazolt** a `comApi.h` és a HTML ellen: INFO bájt
  (source<<4 | dest<<6), packet-struktúra (info/seq/cmdId/arglen/data), minden parancs-ID,
  drive-argumentumok, reply (INFO megfordul, CMD MSB=1, ARGLEN = reply-SEQ + ReARG, nSuccess u8).
  RX=52af0002 (write w/o response, max 20B), TX=52af0003 (notify).
- **Feltárt hiba:** a HSV skála 0-255 (nem 0-100, ahogy a Java repo). Javítva; a "piros" előbb
  fakó volt (0,100,100), most helyes (0,255,255).
- Új parancsok felvéve: LedStartAnim 0x1066, AppConnected 0x1067, AppDisconnected 0x1068,
  BatteryGetVoltage 0x106e, SwitchToBootloader 0x106d (veszélyes).
- **Aktuátorok élőben (v0.1.0 teszt):** beep ✅ (hallható), kerekek pörögtek ✅ (5% akkun is);
  minden parancs `nSuccessful=0`-val nyugtázva. LED-ek lépésenkénti vizuális ellenőrzése a
  0-255 fix után folyamatban.

### Nyitott szálak
- Szenzorolvasás notify-csatornán (akku `0x1069` lenne az első jó teszt — tényleges adat vissza).
- LED-vezérlés (`0x1065`) HSV-vel.
- Python/BlueZ wrapper a bluetoothctl-heredoc kiváltására.
- Mozgás CSAK töltőről levéve, külön jóváhagyással.
