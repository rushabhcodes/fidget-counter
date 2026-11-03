"""Pilot BLE reader/reset utility. Install bleak==0.22.3 on the computer."""
import argparse, asyncio, json, struct
from bleak import BleakClient, BleakScanner

SERVICE = "76b8a000-5aa4-4c10-b5df-0da684303f21"
STATE = "76b8a001-5aa4-4c10-b5df-0da684303f21"
CONTROL = "76b8a002-5aa4-4c10-b5df-0da684303f21"
def decode(payload):
    if len(payload) != 20: raise ValueError("Expected20-byte state")
    version,flags,angle,a,b,total,sequence = struct.unpack("<BBHIIII",payload)
    if version != 1: raise ValueError("Unsupported protocol version")
    return {"total":total,"forward":a,"reverse":b,"angle_degrees":angle/16,
            "sensor_fault":bool(flags&1),"storage_fault":bool(flags&2),
            "unsaved":bool(flags&4),"sample_gap":bool(flags&8),
            "saturated":bool(flags&16),"sequence":sequence}
async def run(args):
    device = args.address or await BleakScanner.find_device_by_filter(
        lambda d,a: SERVICE in [u.lower() for u in (a.service_uuids or [])],timeout=20)
    if not device: raise RuntimeError("No Fidget Counter found")
    async with BleakClient(device) as client:
        if args.reset or args.save:
            await client.write_gatt_char(CONTROL,b"ZERO" if args.reset else b"SAVE",response=True)
            for _ in range(30):
                state = decode(await client.read_gatt_char(STATE))
                if not state["unsaved"] and (not args.reset or state["total"] == 0):
                    if state["storage_fault"]: raise RuntimeError("Count storage fault")
                    print(json.dumps(state)); break
                await asyncio.sleep(.1)
            else: raise RuntimeError("Reset/save not confirmed; inspect device status")
        else:
            print(json.dumps(decode(await client.read_gatt_char(STATE))))
            await client.start_notify(STATE,lambda _,data:print(json.dumps(decode(data))))
            await asyncio.sleep(args.seconds)
            await client.stop_notify(STATE)
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--address",help="OS-specific BLE address/identifier; select explicitly if multiple units")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--reset",action="store_true",help="Clear all saved/live counts")
    group.add_argument("--save",action="store_true",help="Checkpoint counts before removing the cell")
    p.add_argument("--seconds",type=float,default=60)
    asyncio.run(run(p.parse_args()))
if __name__ == "__main__": main()
