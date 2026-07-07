"""CodieClient — aszinkron BLE kliens (bleak) a Codie robothoz.

A kliens csatlakozik, feliratkozik a notify-csatornára, és a kérés SEQ ->
válasz REQSEQ párosítással kéri le a szenzorértékeket. Az aktuátor-parancsok
(beep, LED, mozgás) is várnak nyugtára, de ha nem jön, `None`-t adnak vissza.
"""

from __future__ import annotations

import asyncio

from bleak import BleakClient

from . import protocol as p


class CodieClient:
    def __init__(self, address: str, adapter: str = "hci0", timeout: float = 15.0):
        self.address = address
        self.adapter = adapter
        self._connect_timeout = timeout
        self._client: BleakClient | None = None
        self._pending: dict[int, asyncio.Future] = {}
        self.notifications: list[tuple[bytes, dict | None]] = []

    # --- életciklus ------------------------------------------------------

    async def __aenter__(self) -> "CodieClient":
        await self.connect()
        return self

    async def __aexit__(self, *exc) -> None:
        await self.disconnect()

    async def connect(self) -> None:
        kwargs = {"timeout": self._connect_timeout}
        if self.adapter:
            kwargs["adapter"] = self.adapter
        self._client = BleakClient(self.address, **kwargs)
        await self._client.connect()
        await self._client.start_notify(p.NOTIFY_UUID, self._on_notify)

    async def disconnect(self) -> None:
        if self._client is not None:
            try:
                await self._client.disconnect()
            finally:
                self._client = None

    @property
    def is_connected(self) -> bool:
        return self._client is not None and self._client.is_connected

    # --- notify kezelés --------------------------------------------------

    def _on_notify(self, _characteristic, data: bytearray) -> None:
        raw = bytes(data)
        resp = p.decode_response(raw)
        self.notifications.append((raw, resp))
        if resp is not None:
            fut = self._pending.get(resp["req_seq"])
            if fut is not None and not fut.done():
                fut.set_result(resp)

    # --- alap küldés/válasz ---------------------------------------------

    async def _send(
        self,
        cmd_id: int,
        args: bytes = b"",
        expect_response: bool = True,
        timeout: float = 2.5,
    ) -> dict | None:
        if self._client is None:
            raise RuntimeError("Nincs kapcsolat — hívd előbb a connect()-et.")
        frame, seq = p.build_frame(cmd_id, args)
        loop = asyncio.get_event_loop()
        fut: asyncio.Future = loop.create_future()
        if expect_response:
            self._pending[seq] = fut
        await self._client.write_gatt_char(p.WRITE_UUID, frame, response=False)
        if not expect_response:
            return None
        try:
            return await asyncio.wait_for(fut, timeout)
        except asyncio.TimeoutError:
            return None
        finally:
            self._pending.pop(seq, None)

    # --- aktuátorok ------------------------------------------------------

    async def beep(self, duration_ms: int = 1000) -> dict | None:
        return await self._send(p.CMD_SPEAK_BEEP, p.beep_args(duration_ms))

    async def led_all(self, color: str = "green") -> dict | None:
        return await self._send(p.CMD_LED_SET_COLOR, p.led_all_args(color))

    async def led_single(self, color: str, index: int) -> dict | None:
        return await self._send(p.CMD_LED_SET_COLOR, p.led_single_args(color, index))

    async def leds_off(self) -> dict | None:
        # "kikapcsolt" = value 0 (fekete)
        h, s, _v = p.color_hsv("white")
        return await self._send(p.CMD_LED_SET_COLOR, p._u16(0x0FFF) + p._u8(0) + p._u8(0) + p._u8(0))

    async def drive_speed(self, left: int, right: int) -> dict | None:
        return await self._send(p.CMD_DRIVE_SPEED, p.drive_speed_args(left, right))

    async def stop(self) -> dict | None:
        return await self.drive_speed(0, 0)

    async def drive_distance(self, distance_mm: int, left: int = 30, right: int = 30) -> dict | None:
        return await self._send(p.CMD_DRIVE_DISTANCE, p.drive_distance_args(distance_mm, left, right))

    async def drive_turn(self, degree: int, speed: int = 30) -> dict | None:
        return await self._send(p.CMD_DRIVE_TURN, p.drive_turn_args(degree, speed))

    # --- szenzorok -------------------------------------------------------

    async def battery(self) -> int | None:
        r = await self._send(p.CMD_BATTERY)
        return p.read_u8(r["args"], 0) if r else None

    async def light(self) -> int | None:
        r = await self._send(p.CMD_LIGHT)
        return p.read_u16(r["args"], 0) if r else None

    async def line(self) -> tuple[int | None, int | None] | None:
        r = await self._send(p.CMD_LINE)
        if not r:
            return None
        return p.read_u16(r["args"], 0), p.read_u16(r["args"], 2)

    async def sonar(self) -> int | None:
        r = await self._send(p.CMD_SONAR)
        return p.read_u16(r["args"], 0) if r else None

    async def mic(self) -> int | None:
        r = await self._send(p.CMD_MIC)
        return p.read_u16(r["args"], 0) if r else None
