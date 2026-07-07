# Changelog

A projekt verziózása [semver](https://semver.org/lang/hu/) szerint.

## [0.8.0] — 2026-07-07

### Added — Hermes skill (robot-playbook)
- `hermes/skills/robotics/codie-robot/SKILL.md` — agentskills.io-kompatibilis Hermes-skill, ami
  megtanítja az agentnek, *hogyan* használja a `mcp_codie_*` toolokat: érzékelj mozgás előtt,
  csak véges parancs, töltő↔LED ütközés, alacsony akku, fix csipogó, BLE-késleltetés+reconnect,
  fizikai biztonság. `requires_tools`-szal a Codie MCP-toolokhoz kötve.
- README: skill betöltése `skills.external_dirs`-szel (a repóból, verziózva).

## [0.7.1] — 2026-07-07

### Added
- Konkrét **Hermes MCP-config** (README „Hermes bekötés"): `~/.hermes/config.yaml`,
  `PYTHONPATH`-szal (a Hermes sémában nincs `cwd`), explicit `env` (title-szűrés miatt),
  `supports_parallel_tool_calls: false`, `timeout`/`connect_timeout: 30`.

### Changed
- Az MCP szerver lifespan **lustán csatlakozik**: a szerver azonnal indul, az első tool-hívás
  nyit BLE-kapcsolatot → a tool-felderítés nem vár a ~10-15 mp-es connectre.

### Verified
- Mozgásirányok élőben igazolva (előre/hátra/jobbra/balra) — a `turn` konvenció és a hátramenet
  helyes, nincs előjel-fix. `assets/codie.jpg` alkatrész-diagram a README-ben.

## [0.7.0] — 2026-07-07

### Added — MCP szerver (Hermes / agent integráció)
- `codie/mcp_server.py` — a `CodieClient` fölé MCP réteg (FastMCP), 9 magas szintű tool:
  `status`, `look_ahead`, `drive_forward`, `drive_backward`, `turn`, `stop`, `beep`,
  `say_morse`, `set_leds`.
- Tartós BLE-kapcsolat **reconnect-wrapperrel** (`_ensure`): drop után a következő
  tool-hívás automatikusan újracsatlakozik.
- Safety-by-design: csak véges, magától megálló mozgásparancsok (nincs nyers folytonos
  `drive_speed` az agent kezében).
- `mcp` függőség; README MCP/Hermes szekció; `tests/test_mcp_server.py` (5 teszt, összesen 27).

### Fixed
- **`turn()` előjel-bug** (egy külső vázlatból): a `drive_turn` foka u16 (előjel nélküli),
  az irányt a **speed előjele** adja (hivatalos API: pozitív speed = balra). A javított tool
  a fok abszolútértékét küldi, az irányt a speed előjelével — nincs u16 wraparound.

## [0.6.0] — 2026-07-07

### Added — FFT frekvenciaelemzés
- `scripts/fft_pitch.py` — egy hangfelvételből (bármilyen formátum, ffmpeg-gel dekódolva)
  kiadja a domináns frekvenciát, a felharmonikusokat és egy óvatos értelmezést
  (rezonáns buzzer vs passzív elem). A Codie csipogó hangmagasságának méréséhez.
- `numpy` függőség (FFT). Rendszerfüggőség: `ffmpeg` (dekódolás).
- Validálva szintetikus szinusz (3000 Hz) és négyszögjel (2700 Hz, páratlan felharmonikusok) ellen.

## [0.5.0] — 2026-07-07

### Added — mikrofon↔csipogó zárt hurok kísérlet
- `scripts/mic_beep.py` — a robot a saját beepjét a mikrofonjával "hallja".

### Findings (empirikus)
- A mic BLE-n **~5 Hz** effektív mintavétellel olvasható (200 ms/olvasás), ~50 ms átlagolással →
  hangmagasság (frekvencia) mérésére **alkalmatlan** (Nyquist, ~600× túl lassú 3 kHz-hez).
- Amplitúdó/burkoló viszont jól látszik: beep alatt 456 → 1866; a beep **hossza** is
  visszamérhető a burkolóból.
- A mic-lekérdezés **nem szakítja meg** a folyamatban lévő SpeakBeep-et.

## [0.4.0] — 2026-07-07

### Added — hang: ritmus és Morse
- `codie/morse.py` — szöveg → Morse-ritmus (szabványos időzítés), tiszta és tesztelt.
- `codie/tunes.py` — beépített ritmusminták (shave_haircut, beethoven5, heartbeat,
  tada, alarm, countdown). Fix hangmagasság → ritmus, nem dallam.
- `CodieClient.play_rhythm()`, `play_morse()`, `play_tune()`.
- `scripts/play.py` — CLI: morse / tune / beep / list.
- `tests/test_morse.py` — 7 új unit teszt (összesen 22).

### Megjegyzés
- A hardver csak fix-frekvenciás csipogó (BLE API v1.0: SpeakBeep, "frequency is fixed").
  WAV/dallam nincs; a kifejezőeszköz a ritmus (csipogáshossz + szünetek).

## [0.3.0] — 2026-07-07

### Verified — teljes funkció-teszt kész
- **Minden funkció élőben igazolva:** szenzorok (akku/fény/vonal/szonár/mikrofon),
  SpeakBeep (hallható), mozgás (DriveSpeed/Distance/Turn — kerekek pörögtek),
  LedSetColor (vizuálisan: erős fény, helyes színkör, a 0-255 HSV-fix bizonyítva).
- Minden parancsot a robot `nSuccessful=0`-val nyugtázott.

### Added
- `scripts/led_sweep.py` — lassú szín-szekvencia vizuális ellenőrzéshez.
- README: teszt-eredmény összefoglaló táblázat.

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
