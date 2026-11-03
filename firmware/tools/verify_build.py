"""Fail-closed checks on the actual linked RevC image, configuration and memory."""
import hashlib, json, re, struct, subprocess, sys
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
def check_hex(path):
    memory = {}
    upper = 0
    eof = False
    for line in path.read_text().splitlines():
        if not line.startswith(":"):
            raise ValueError("Invalid Intel HEX line")
        row = bytes.fromhex(line[1:])
        if len(row) != row[0] + 5 or sum(row) & 255:
            raise ValueError("Invalid Intel HEX length/checksum")
        length, address, kind = row[0], int.from_bytes(row[1:3], "big"), row[3]
        data = row[4:4 + length]
        if eof:
            raise ValueError("Data after EOF")
        if kind == 0:
            for offset, value in enumerate(data):
                key = upper + address + offset
                if key in memory and memory[key] != value:
                    raise ValueError("Conflicting HEX data")
                memory[key] = value
        elif kind == 1:
            if length or address: raise ValueError("Malformed EOF")
            eof = True
        elif kind in (2, 4):
            if length != 2 or address: raise ValueError("Malformed address")
            upper = int.from_bytes(data, "big") << (4 if kind == 2 else 16)
        elif kind in (3, 5):
            # Start-segment/start-linear metadata do not write memory.
            # Actual boot uses the independently checked Cortex-M vectors.
            if length != 4 or address: raise ValueError("Malformed start address")
        else:
            raise ValueError("Unsupported HEX record type")
    if not eof or not memory: raise ValueError("Incomplete HEX")
    # Allow application flash only. UICR reset is configured by Zephyr startup code.
    if any(address >= 0x2e000 for address in memory):
        raise ValueError("HEX writes outside the184KiB application partition")
    vector = bytes(memory[i] for i in range(8))
    stack, reset = struct.unpack("<II", vector)
    if not 0x20000000 < stack <= 0x20006000 or stack % 8:
        raise ValueError("Initial stack is outside nRF52810 RAM")
    if not reset & 1 or not (8 <= (reset & ~1) < 0x2e000):
        raise ValueError("Invalid Cortex-M reset vector")
    if (reset & ~1) not in memory or (reset & ~1) + 1 not in memory:
        raise ValueError("HEX does not contain its reset handler")
    return {"initial_stack":hex(stack), "reset_vector":hex(reset),
            "flash_data_bytes":len(memory), "highest_flash_address":hex(max(memory))}

def main():
    build = Path(sys.argv[1] if len(sys.argv) > 1 else APP / "build")
    config = (build / "zephyr/.config").read_text()
    required = ["SOC_NRF52810_QFAA", "BOARD_FIDGET_COUNTER", "BT", "BT_CTLR", "BT_PERIPHERAL",
                "CLOCK_CONTROL_NRF_K32SRC_XTAL", "NVS_DATA_CRC"]
    for symbol in required:
        assert re.search(r"^CONFIG_" + symbol + r"=y$", config, re.M), symbol
    for symbol in ["SOC_DCDC_NRF52X","SERIAL","CONSOLE","BT_SMP","NRF_APPROTECT_LOCK"]:
        assert not re.search(r"^CONFIG_" + symbol + r"=y$", config, re.M), symbol
    for symbol, value in [("FLASH_SIZE",192),("SRAM_SIZE",24)]:
        assert re.search(r"^CONFIG_" + symbol + "=" + str(value) + "$", config, re.M), symbol
    board = (APP / "boards/others/fidget_counter/fidget_counter.dts").read_text()
    assert "NRF_PSEL(TWIM_SCL, 0, 26)" in board
    assert "NRF_PSEL(TWIM_SDA, 0, 27)" in board
    assert "gpio-as-nreset" in board and "0x0002e000 0x00002000" in board
    circuit = (APP.parent / "index.circuit.tsx").read_text()
    for label, port in [("SCL","P0_26"),("SDA","P0_27"),("HALL_INT","P0_28")]:
        assert re.search(r'n: "' + label + '", p: "' + port + '"', circuit), label
    assert '"SW1"' not in circuit and "GPIO_CAP_PRESS" not in circuit
    dts = (build / "zephyr/zephyr.dts").read_text()
    assert 'model = "Fidget Counter RevC CR2450"' in dts
    assert '"gpio-leds"' not in dts and '"gpio-keys"' not in dts
    elf = build / "zephyr/zephyr.elf"
    raw = subprocess.check_output(["arm-none-eabi-readelf","-lW",str(elf)], text=True)
    ram_end = 0x20000000
    for line in raw.splitlines():
        columns = line.split()
        if not columns or columns[0] != "LOAD": continue
        virtual, physical, filesz, memsz = [int(columns[i],16) for i in [2,3,4,5]]
        if filesz and physical < 0x20000000: assert physical + filesz <= 0x2e000
        if 0x20000000 <= virtual < 0x30000000:
            assert virtual + memsz <= 0x20006000
            ram_end = max(ram_end, virtual + memsz)
    # Thread stacks are already in RAM usage; leave2KiB additional headroom.
    assert ram_end <= 0x20005800, "Less than2KiB static RAM headroom"
    hexpath = build / "zephyr/zephyr.hex"
    result = check_hex(hexpath)
    result.update({"compiled_for":"nRF52810 QFAA / RevC", "application_flash_limit":188416,
                   "ram_bytes":ram_end - 0x20000000, "ram_headroom_bytes":0x20006000 - ram_end,
                   "physical_tested":False, "zephyr_commit":"19aeae80fac00aa3310ef9a26d08fab4502e812f",
                   "compiler":subprocess.check_output(["arm-none-eabi-gcc","--version"],text=True).splitlines()[0],
                   "source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=APP,text=True).strip(),
                   "files":{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in [hexpath,elf,build/"zephyr/.config",build/"zephyr/zephyr.dts"]}})
    (build / "firmware-build-manifest.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__ == "__main__": main()
