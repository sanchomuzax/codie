# Codie — BLE vezérlés Raspberry Pi 5-ről

Ez a projekt a **Codie oktatórobot** felélesztése: közvetlen Bluetooth Low Energy (BLE)
vezérlés Raspberry Pi 5-ről, BlueZ-n keresztül.

## Háttér

A Codie egy 2015–2016 körüli magyar oktatórobot. A hozzá tartozó
[csorbazoli/CodieController](https://github.com/csorbazoli/CodieController) egy 2016-os,
**félbehagyott** Java proof-of-concept volt, amely a robotot a Scratch 2 offline editorból
akarta vezérelni (helyi HTTP szerver + Scratch-blokkok). A szerző 2019-ben feladta: Windows
alatt nem talált BLE 4-es drivert, és úgy hitte, a `CodieGateway` protokoll dokumentálatlanul
elveszett.

Valójában a protokoll **nem veszett el** — a repo `DataPackage.java` és `CodieCommandType.java`
fájljai tartalmazzák a teljes, visszafejtett MCU-frame formátumot. A hiányzó láncszem csak a
PC→BLE fizikai út volt, ami BlueZ-vel (Linux) triviális.

**2026-07-07:** az RPi5-ről, BlueZ GATT-tal, a szerző saját frame-formátumával a robot élőben
fogadott és végrehajtott parancsot (SpeakBeep) — ismételhetően igazolva.

## Hardver / BLE topológia

| Elem | Érték |
|------|-------|
| Robot BLE cím | `DF:74:94:43:36:ED` (random address), Name: `Codie` |
| RPi5 adapter | `hci0` — `88:A2:9E:0C:70:EB` |
| Vendor service | `52af0001-978a-628d-c845-0a104ca2b8dd` |
| Write (parancs) char | `52af0002-978a-628d-c845-0a104ca2b8dd` — flags: `write`, `write-without-response` |
| Notify (válasz/szenzor) char | `52af0003-978a-628d-c845-0a104ca2b8dd` — flags: `notify` |

A `52af0002` write-without-response → nincs ATT-szintű nyugta. A robot válaszai / szenzoradatai
a `52af0003` notify-csatornán jönnek vissza.

## Frame formátum

20 byte-os buffer, csak a kitöltött rész megy ki. Minden többbájtos mező **little-endian**.

```
INFO(1) | SEQ(2) | CMD(2) | ARGLEN(2) | ARGDAT...
```

- **INFO** = `(from.ordinal() << 4) | (to.ordinal() << 6) | prio`
  - Role ordinal: `APP=0, MCU=1, BLE=2, Broadcast=3`
  - prio: NORMAL=`0x00`, HIGH=`0x08`
  - Tipikus APP→MCU, normal prio: **`0x40`**
- **SEQ** — növekvő sorszám (tetszőleges, wrap 0xFFFF-nél)
- **CMD** — 2 byte parancs-ID (lásd lent)
- **ARGLEN** — az argumentumok hossza byte-ban
- **ARGDAT** — argumentumok; U8/I8 = 1 byte, U16 = 2 byte LE

### Parancs-ID-k (`CodieCommandType`)

| Parancs | ID | Argumentumok |
|---------|-----|-------------|
| DriveSpeed / DriveDistanceBySpeed | `0x1060` | speedLeft i8, speedRight i8 (%) |
| DriveDistance | `0x1061` | distance u16 (mm), leftSpeed i8, rightSpeed i8 (%) |
| DriveTurn | `0x1062` | (fordulás) |
| SonarGetRange | `0x1063` | — (szenzor) |
| SpeakBeep | `0x1064` | duration u16 (ms, max 10000) |
| LedSetColor / LedSetColorSingle | `0x1065` | ledMask u16 (0x08ff = mind), hue u8, sat u8, val u8 |
| BatteryGetSoc | `0x1069` | — (szenzor) |
| LightSenseGetRaw | `0x106a` | — (szenzor) |
| LineGetRaw | `0x106b` | — (szenzor) |
| MicGetRaw | `0x106c` | — (szenzor) |

## Igazolt parancs — beep (~1 mp)

Írás a `52af0002` karakterisztikára:

```
40 01 00 64 10 02 00 e8 03
│  │  │  │  │  │  │  └──┴─ duration u16 = 1000 ms (0x03E8)
│  │  │  │  │  └──┴─ ARGLEN = 2
│  │  │  └──┴─ CMD = 0x1064 (SpeakBeep), LE
│  └──┴─ SEQ = 1
└─ INFO = 0x40 (APP→MCU, normal)
```

A közvetlen APP→MCU kódolás működik; **nem** kellett a CMD felső bájtját `0x80`-nal jelölő,
REQSEQ-et beszúró alternatív BLE-forward variáns.

## Csatlakozás bluetoothctl-lel

A connect ~10 mp; a sessiont életben kell tartani (a heredoc azonnal lezárja a stdin-t, ezért
`sleep`-ekkel adagolt parancsokkal megy). Vázlat:

```bash
{
  echo "connect DF:74:94:43:36:ED"; sleep 11
  echo "menu gatt"; sleep 1
  echo "select-attribute /org/bluez/hci0/dev_DF_74_94_43_36_ED/service000c/char000d"; sleep 1
  echo "notify on"; sleep 2        # 52af0003 — válasz/szenzor stream
  echo "select-attribute /org/bluez/hci0/dev_DF_74_94_43_36_ED/service000c/char0010"; sleep 1
  echo 'write "0x40 0x01 0x00 0x64 0x10 0x02 0x00 0xe8 0x03"'; sleep 4   # 52af0002 — beep
  echo "exit"
} | bluetoothctl
```

(A `service000c/char0010` = `52af0002`, `service000c/char000d` = `52af0003` — a handle-alias
a konkrét BlueZ felderítéskor rögzült; connect után `menu gatt` → `list-attributes` ellenőrzi.)

## Biztonság

- **Mozgásparancsot (DriveDistance / DriveTurn / DriveSpeed) csak a töltőről levéve** és az
  asztal szélétől távol küldeni. Töltés közben tilos.
- Sípolás és LED biztonságos, mozgásmentes — életjel-próbához ezek valók.
- Minden fizikai actuálás (kiváltképp mozgás) előtt rákérdezni a felhasználónál.

## Következő lépések

- LED-vezérlés (`0x1065`) — HSV a repo `CodieColors` enumjából
- Szenzorolvasás a notify-csatornán: akku (`0x1069`), fény, vonal, szonár, mikrofon
- Vékony Python/BlueZ (bleak vagy dbus) wrapper a bluetoothctl-heredoc helyett
- Esetleg a Scratch-blokkos réteg újraélesztése a working BLE-backenddel
