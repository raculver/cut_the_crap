import asyncio
from bleak import BleakClient, BleakScanner
from typing import Optional

SERVICE_UUID = "593af084-a37f-4b3a-832a-bcb8e547b259"
CHARACTERISTIC_UUID = "0829d7d5-9f92-4c66-8117-c0733207dc76"

def match_name(search_name, device):
    name = device.name
    return isinstance(name, str) and search_name in name

search_name = "CTC_Serv"

class ClientInterface:
    def __init__(self):
        self.owner = ClientOwner(search_name, CHARACTERISTIC_UUID)
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def start(self):
        # Connect (blocking)
        self.loop.run_until_complete(self.owner.connect())

    def write_ble(self, value: bool):
        """Synchronous call from normal code."""
        self.loop.run_until_complete(
            self.owner.write_characteristic(value)
        )

    def read_ble(self):
        return self.loop.run_until_complete(
            self.owner.read_characteristic()
        )

    def stop(self):
        self.loop.run_until_complete(self.owner.disconnect())
        self.loop.close()

class ClientOwner:
    def __init__(self, name_fragment: str,
#                 service_uuid: str,
                 char_uuid: str):
        self.name_fragment = name_fragment
#        self.service_uuid = service_uuid
        self.char_uuid = char_uuid

        self.client: Optional[BleakClient] = None
        self._device = None
        self._connected = False

    # ---------- Discovery & Connection ----------
    async def connect(self, timeout: float = 10.0) -> bool:
        """Scan, connect and keep the client open."""
        print(f"Scanning for '{self.name_fragment}'...")
        devices = await BleakScanner.discover(timeout=timeout)
        [print(device) for device in devices]

        matches = [d for d in devices
                   if d.name and self.name_fragment in d.name]

        if not matches:
            print("Device not found")
            return False

        self._device = matches[0]
        print(f"Found: {self._device.name} ({self._device.address})")

        self.client = BleakClient(self._device)
        await self.client.connect()
        self._connected = self.client.is_connected
        print("Connected:", self._connected)
        return self._connected

    async def disconnect(self):
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            print("Disconnected")
        self._connected = False
        self.client = None

    # ---------- Characteristic helpers ----------
    async def write_characteristic(self, value: bool | int | bytes,
                                   response: bool = False) -> None:
        """
        Write a single-byte bool (True/False/0/1) or raw bytes.
        """
        if not self._connected or not self.client:
            raise RuntimeError("Not connected")

        if isinstance(value, bool) or value in (0, 1):
            data = b"\x01" if value else b"\x00"
        elif isinstance(value, (bytes, bytearray)):
            data = bytes(value)
        else:
            raise TypeError("value must be bool, 0/1 or bytes")

        await self.client.write_gatt_char(
            self.char_uuid, data, response=response
        )
        print(f"Wrote: {data.hex()}")

    async def read_characteristic(self) -> bytearray:
        if not self._connected or not self.client:
            raise RuntimeError("Not connected")
        data = await self.client.read_gatt_char(self.char_uuid)
        print(f"Read:  {data.hex()}")
        return data

    @property
    def is_connected(self) -> bool:
        return self._connected and self.client is not None and self.client.is_connected
    