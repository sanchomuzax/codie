# Codie — BLE vezérlés Raspberry Pi 5-ről

A [csorbazoli/CodieController](https://github.com/csorbazoli/CodieController) 2016-os,
félbehagyott Java PoC-jából visszafejtett wire-protokoll tiszta Python implementációja.
A **Codie** oktatórobotot közvetlen Bluetooth Low Energy-n (BlueZ) vezérli — az a láncszem,
ami 2019-ben hiányzott (PC-oldali BLE út), Linuxon triviális.

A protokoll- és hardverrészletek a [CLAUDE.md](CLAUDE.md)-ben; a fejlődési napló a
[MEMORY.md](MEMORY.md)-ben.

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

## Unit tesztek (robot nélkül)

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## Parancsok

| Metódus | Parancs | Megjegyzés |
|---------|---------|-----------|
| `beep(ms)` | SpeakBeep | max 10000 ms |
| `led_all(color)` / `led_single(color, idx)` | LedSetColor | színek: white, green, red, blue, cyan, yellow, orange |
| `drive_speed(l, r)` | DriveSpeed | -100..100 % |
| `drive_distance(mm, l, r)` | DriveDistance | mm + kerék-sebességek |
| `drive_turn(deg, speed)` | DriveTurn | fok + sebesség |
| `battery()` | BatteryGetSoc | % |
| `light()` / `line()` / `sonar()` / `mic()` | szenzorok | raw / mm |
