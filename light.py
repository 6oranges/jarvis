import asyncio
from kasa import Discover

async def get_device(ip_address):
    device =  await Discover.discover_single(ip_address)
    if device is not None:
        print(f"Using device at IP: {ip_address} with alias: {device.alias}")
        print(f"Using existing device: {device}")
        return device,ip_address
    devices = await Discover.discover()
    for key in devices:
        ip_address = key
        if "tim" not in devices[key].alias.lower():
            continue
        print(f"Found device at IP: {ip_address} with alias: {devices[key].alias}")
        print(f"Using device: {device}")
        return devices[key],ip_address
async def turn_on_device(dev):
    await dev.turn_on()
    await dev.update()
    print("Device turned on")

async def turn_off_device(dev):
    await dev.turn_off()
    await dev.update()
    print("Device turned off")
async def set_brightness(dev, brightness):
    # Probably a bug in kasa, but we need to use _set_brightness instead of set_brightness
    await dev._set_brightness(brightness)
    await dev.update()
    print("Device brightness set to", brightness)
async def set_color(dev, h, s, v):
    await dev._set_hsv(h, s, v)
    await dev.update()
    print("Device color set to", h, s, v)
async def process(dev,ip_address,command):
    if command[0]=="on":
        await turn_on_device(dev)
    elif command[0]=="off":
        await turn_off_device(dev)
    elif command[0]=="brightness":
        await set_brightness(dev, int(command[1]))
    elif command[0]=="connect":
        dev,ip_address = await get_device()
    elif command[0]=="color":
        await set_color(dev, int(command[1]), int(command[2]), int(command[3]))
    return dev,ip_address
async def main(ip_address):
    dev,ip_address = await get_device(ip_address)
    while True:
        command =input().strip().split(" ")
        try:
            dev,ip_address = await process(dev,ip_address,command)
        except Exception as e:
            print(e)
            try:
                dev,ip_address = await get_device(ip_address)
                dev,ip_address = await process(dev,ip_address,command)
            except Exception as e:
                print(e)
                pass
asyncio.run(main("192.168.1.213"))