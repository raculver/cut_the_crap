import asyncio
from bleak import BleakClient, BleakScanner

MODEL_NBR_UUID = "00001525-1212-EFDE-1523-785FEABCD123"

async def test():
    devices = await BleakScanner.discover()
    [print(device) for device in devices]

async def main():
    devices = await BleakScanner.discover()
    device = [device for device in devices if device.name == "Test Ad"][0]

    print("Device is {}".format(device.name))

    async with BleakClient(device) as client:
        print("Connected:", client.is_connected)
    
#        for service in client.services:
#            print(service.uuid)

        for service in client.services:
            print(service.uuid)
            for char in service.characteristics:
                print("   ", char.uuid, char.properties)

#        for char in service.characteristics:
#            print("   ", char.uuid, char.properties)

#        for service in client.services:
#            for char in service.characteristics:
#                if char.uuid.endswith("2ab4-0000-1000-8000-00805f9b34fb"):
#                    print(char)
#                    value = await client.read_gatt_char(char)
#                    print(value)


    async with BleakClient(device.address) as client:
        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print(f"Model Number: {model_number.decode()}")

asyncio.run(test())
asyncio.run(main())
