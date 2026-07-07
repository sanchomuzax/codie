# Codie — BLE vezérlés Raspberry Pi 5-ről

A [csorbazoli/CodieController](https://github.com/csorbazoli/CodieController) 2016-os,
félbehagyott Java PoC-jából visszafejtett wire-protokoll tiszta Python implementációja.
A **Codie** oktatórobotot közvetlen Bluetooth Low Energy-n (BlueZ) vezérli — az a láncszem,
ami 2019-ben hiányzott (PC-oldali BLE út), Linuxon triviális.

A protokoll- és hardverrészletek a [CLAUDE.md](CLAUDE.md)-ben; a fejlődési napló a
[MEMORY.md](MEMORY.md)-ben.

## Teszt eredmények (2026-07-07 — minden funkció élőben igazolva)

| Kategória | Funkció | Állapot |
|-----------|---------|---------|
| Szenzor | akku (SoC), fény, vonal, szonár, mikrofon | ✅ objektív adat, bájtra pontos dekódolás |
| Hang | SpeakBeep | ✅ hallható |
| Mozgás | DriveSpeed, DriveDistance, DriveTurn | ✅ kerekek pörögtek (alacsony akkun is) |
| Fény | LedSetColor (mind a 12 + egyesével) | ✅ vizuálisan igazolt, helyes színek, erős fény |

Minden parancsot a robot `nSuccessful=0`-val nyugtázott. A protokollt a hivatalos
Codie BLE API v1.0 (`docs/comApi.h`) teljesen igazolta.

## Telepítés

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env      # majd töltsd ki a robot BLE címét
```

A robot címét megtalálod:

```bash
bluetoothctl scan le      # keresd a "Codie" nevű eszközt
```

## Használat

```python
import asyncio
from codie import CodieClient

async def main():
    async with CodieClient("DF:74:94:43:36:ED") as c:
        await c.beep(700)                 # sípol
        await c.led_all("red")            # mind a 12 LED piros
        print("akku:", await c.battery(), "%")
        await c.drive_speed(30, 30)       # előre 30%
        await asyncio.sleep(1)
        await c.stop()

asyncio.run(main())
```

## Teljes funkció-teszt

A robot **az oldalán, töltőn** feküdjön — a kerekek szabadon pörögnek, de a robot nem
szalad le az asztalról.

```bash
.venv/bin/python scripts/test_all.py            # minden
.venv/bin/python scripts/test_all.py sensors    # csak szenzorok
.venv/bin/python scripts/test_all.py led drive  # csak LED + mozgás
```

## Hang: ritmus és Morse

A hangszóró fix hangmagasságú csipogó (nincs WAV/dallam), de a ritmus vezérelhető:

```bash
.venv/bin/python scripts/play.py tune shave_haircut   # beépített ritmus
.venv/bin/python scripts/play.py morse "SOS"          # Morse-kód
.venv/bin/python scripts/play.py list                 # elérhető ritmusok
```

A csipogó **hangmagassága** telefonos felvételből mérhető (a robot mikrofonja erre kevés):

```bash
.venv/bin/python scripts/play.py beep 3000            # hosszú beep a felvételhez
# ...vedd fel telefonnal, majd:
.venv/bin/python scripts/fft_pitch.py felvetel.m4a    # domináns frekvencia + felharmonikusok
```

Rendszerfüggőség az FFT-elemzéshez: `ffmpeg` (a felvétel dekódolásához).

## Unit tesztek (robot nélkül)

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## Parancsok

| Metódus | Parancs | Megjegyzés |
|---------|---------|-----------|
| `beep(ms)` | SpeakBeep | max 10000 ms |
| `play_rhythm(pattern)` / `play_morse(text)` / `play_tune(name)` | SpeakBeep sorozat | fix hangmagasság → **ritmus**, nem dallam |
| `led_all(color)` / `led_single(color, idx)` | LedSetColor | színek: white, green, red, blue, cyan, yellow, orange |
| `drive_speed(l, r)` | DriveSpeed | -100..100 % |
| `drive_distance(mm, l, r)` | DriveDistance | mm + kerék-sebességek |
| `drive_turn(deg, speed)` | DriveTurn | fok + sebesség |
| `battery()` | BatteryGetSoc | % |
| `light()` / `line()` / `sonar()` / `mic()` | szenzorok | raw / mm |
