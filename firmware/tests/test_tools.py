import asyncio, importlib.util, struct, sys, tempfile, types, unittest
from pathlib import Path
from unittest.mock import patch
TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from verify_build import check_hex
with patch.dict(sys.modules, {"bleak":types.SimpleNamespace(BleakClient=None,BleakScanner=None)}):
    from client import decode, decode_battery
    import client as client_module

def record(kind, address=0, data=b""):
    body = bytes([len(data)]) + address.to_bytes(2,"big") + bytes([kind]) + data
    return ":" + (body + bytes([-sum(body) & 255])).hex().upper()
def image(stack=0x20005800, reset=0x101, extra=()):
    return [record(0,0,struct.pack("<II",stack,reset)),record(0,0x100,b"\x70\x47"),*extra,record(1)]

class Tools(unittest.TestCase):
    def check(self, lines):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "test.hex"
            p.write_text("\n".join(lines)+"\n")
            return check_hex(p)
    def test_real_vectors(self):
        self.assertEqual(self.check(image())["initial_stack"],"0x20005800")
    def test_bad_checksum(self):
        lines = image(); lines[0] = lines[0][:-2]+"00"
        with self.assertRaises(ValueError): self.check(lines)
    def test_reserved_storage(self):
        with self.assertRaises(ValueError):
            self.check(image(extra=[record(4,data=b"\x00\x02"),record(0,0xe000,b"\x01")]))
    def test_uicr_write(self):
        with self.assertRaises(ValueError):
            self.check(image(extra=[record(4,data=b"\x10\x00"),record(0,0x1208,b"\x00")]))
    def test_wrong_ram_and_reset(self):
        for stack,reset in [(0x20008000,0x101),(0x20005804,0x101),(0x20005800,0x100),(0x20005800,0x2e001)]:
            with self.subTest(stack=stack,reset=reset),self.assertRaises(ValueError):
                self.check(image(stack,reset))
    def test_segment_records(self):
        self.check(image(extra=[record(2,data=b"\x10\x00"),record(0,0,b"\x01"),record(3,data=b"\x00\x00\x01\x01")]))
    def test_segment_into_storage(self):
        with self.assertRaises(ValueError):
            self.check(image(extra=[record(2,data=b"\x2e\x00"),record(0,0,b"\x01")]))
    def test_malformed_segment(self):
        with self.assertRaises(ValueError): self.check(image(extra=[record(2,data=b"\x01")]))
    def test_missing_entry_code(self):
        with self.assertRaises(ValueError): self.check(image(reset=0x201))
    def test_missing_eof(self):
        with self.assertRaises(ValueError): self.check(image()[:-1])
    def test_conflicting_data(self):
        with self.assertRaises(ValueError): self.check(image(extra=[record(0,0x100,b"\x00")]))
    def test_data_after_eof(self):
        with self.assertRaises(ValueError): self.check(image()+[record(0,0x101,b"\x00")])
    def test_ble_wire_format(self):
        data = struct.pack("<BBHIIII",1,31,4320,7,5,12,1234)
        state = decode(data)
        self.assertEqual((state["angle_degrees"],state["total"],state["forward"],state["reverse"],state["sequence"]),(270,12,7,5,1234))
        self.assertTrue(all(state[k] for k in ["sensor_fault","storage_fault","unsaved","sample_gap","saturated"]))
    def test_bad_ble_payload(self):
        for data in [b"",b"x"*19,bytes([2])+bytes(19)]:
            with self.subTest(data=data),self.assertRaises(ValueError): decode(data)
    def test_battery_wire_format(self):
        self.assertEqual(decode_battery(bytes([1,1,50,0x22,0x0b])),
            {"battery_percent":50,"battery_millivolts":2850,"battery_valid":True,"low_battery":False})
        self.assertTrue(decode_battery(struct.pack("<BBBH",1,3,20,2700))["low_battery"])
    def test_battery_fault_does_not_report_empty_or_clear_last_warning(self):
        state=decode_battery(bytes([1,2,255,255,255]))
        self.assertIsNone(state["battery_percent"])
        self.assertIsNone(state["battery_millivolts"])
        self.assertFalse(state["battery_valid"])
        self.assertTrue(state["low_battery"])
    def test_invalid_battery_wire_format(self):
        for payload in [b"",bytes(4),bytes([2,1,50,0x22,0x0b]),
                        bytes([1,4,255,255,255]),bytes([1,1,101,0x22,0x0b]),
                        bytes([1,0,0,0,0]),struct.pack("<BBBH",1,1,50,5000)]:
            with self.subTest(payload=payload),self.assertRaises(ValueError): decode_battery(payload)
    def test_legacy_state_preserves_battery_flags(self):
        state=decode(struct.pack("<BBHIIII",1,96,0,0,0,0,0))
        self.assertTrue(state["low_battery"])
        self.assertTrue(state["battery_fault"])

class BatteryClient(unittest.TestCase):
    def test_reads_and_subscribes_warning_and_unavailable_status(self):
        for payload in [struct.pack("<BBBH",1,3,20,2700),bytes([1,2,255,255,255])]:
            with self.subTest(payload=payload):
                subscriptions=[]
                stopped=[]
                state=struct.pack("<BBHIIII",1,32,0,7,5,12,1234)
                class FakeClient:
                    async def __aenter__(self): return self
                    async def __aexit__(self,*_): return None
                    async def read_gatt_char(self,uuid):
                        return payload if uuid==client_module.BATTERY else state
                    async def start_notify(self,uuid,callback):
                        subscriptions.append(uuid)
                        callback(None,payload if uuid==client_module.BATTERY else state)
                    async def stop_notify(self,uuid): stopped.append(uuid)
                args=types.SimpleNamespace(address="test-device",reset=False,save=False,seconds=0)
                with patch.object(client_module,"BleakClient",return_value=FakeClient()),patch("builtins.print") as printed:
                    asyncio.run(client_module.run(args))
                self.assertEqual(subscriptions,[client_module.BATTERY,client_module.STATE])
                self.assertCountEqual(stopped,subscriptions)
                decoded=[client_module.json.loads(call.args[0]) for call in printed.call_args_list]
                batteries=[item for item in decoded if "battery_percent" in item]
                self.assertEqual(len(batteries),2)
                self.assertTrue(all(item["low_battery"] for item in batteries))
                self.assertTrue(any(item.get("total")==12 for item in decoded))
                if payload[1] & 1:
                    self.assertEqual(batteries[0]["battery_percent"],20)
                else:
                    self.assertIsNone(batteries[0]["battery_percent"])
if __name__ == "__main__": unittest.main()
