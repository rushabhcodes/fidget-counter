import importlib.util, struct, sys, tempfile, types, unittest
from pathlib import Path
from unittest.mock import patch
TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from verify_build import check_hex
with patch.dict(sys.modules, {"bleak":types.SimpleNamespace(BleakClient=None,BleakScanner=None)}):
    from client import decode

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
if __name__ == "__main__": unittest.main()
