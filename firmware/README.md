# RevC firmware and programming

Pilot application for the actual nRF52810-QFAA, TMAG3001A2 and CR2450 PCB. One complete360° turn in either direction adds one to the total. Backtracking cancels unfinished travel; moving180° forward and180° back adds zero. Directional counters follow the sensor's increasing/decreasing angle, not a qualified physical CW label.

This is source for hardware bring-up. A successful [Firmware workflow](https://github.com/rushabhcodes/fidget-counter/actions/workflows/firmware.yml) produces the complete flashable HEX, ELF, map, generated board/configuration and SHA256 manifest. **Use an artifact only from a successful run for the intended source commit.** A build is not a physical-device qualification.

## Get the image

Open the successful Firmware run on codex/bearing-supported-enclosure, download its fidget-counter-revc-COMMIT artifact and extract it. The image is fidget-counter-revc.hex. Check its SHA256 against firmware-build-manifest.json. The image includes Zephyr's BLE controller and application, starts at flash0 and needs neither a separate Nordic SoftDevice nor a bootloader. Application flash is0..0x2DFFF; the final8KiB at0x2E000 is NVS count storage.

The board uses192KiB flash and24KiB RAM. CI rejects the wrong MCU, DC/DC enabled, wrong I2C pins, invalid HEX/vector table, writes into NVS/UICR, flash overflow, or less than2KiB additional static RAM headroom. Thread stacks are already included in linked RAM usage; their physical high-water use remains to be measured.

## Build on Linux

Ubuntu24.04, GCC ARM Embedded, Python3, CMake, Ninja and devicetree compiler are assumed. The maintained Zephyr3.7 LTS snapshot is pinned by commit in west.yml; its imported cmsis/hal_nordic revisions are pinned by that manifest. West is1.4.0. The CI workflow contains the exact build sequence.

From the Git repository root:

```sh
sudo apt-get install cmake ninja-build gperf device-tree-compiler gcc-arm-none-eabi libnewlib-arm-none-eabi python3-venv
python3 -m venv firmware/.venv
. firmware/.venv/bin/activate
pip install west==1.4.0
sh firmware/tools/test.sh
west init -l firmware
west update --narrow -o=--depth=1
west zephyr-export
pip install -r zephyr/scripts/requirements-base.txt
export ZEPHYR_TOOLCHAIN_VARIANT=gnuarmemb
export GNUARMEMB_TOOLCHAIN_PATH=/usr
west build -b fidget_counter firmware -d firmware/build -p always
python3 firmware/tools/verify_build.py firmware/build
```

Run west init once; subsequent builds start with west update. SDK checkouts live in ignored zephyr/ and modules/ directories beside firmware/. The linked image is firmware/build/zephyr/zephyr.hex. Firmware and circuit builds are independent.

## Flash before assembly

See [PROGRAMMING.md](../PROGRAMMING.md) for cable identification and probe options. Remove the CR2450, set the linked CMSIS-DAP programmer to3V3, verify straight-through continuity and measure the supplied voltage. J_DEBUG is1=VBAT/VOUT,2=SWDIO,3=GND,4=SWCLK,5=nRESET. Never select5V or connect two supplies.

From the repository root with OpenOCD0.12.0 installed:

```sh
python3 firmware/tools/flash.py --hex firmware/build/zephyr/zephyr.hex
```

For a downloaded artifact, run python3 flash.py --hex fidget-counter-revc.hex in its extracted folder. Use --interface jlink only for the documented externally powered J-Link wiring. Some OpenOCD versions need --target-config target/nordic/nrf52.cfg. --probe-serial selects a specific probe.

The script validates the complete HEX, identifies FICR.INFO.PART as nRF52810, writes the application sectors, verifies and resets. It does not mass-erase, recover protection or enable readback protection. Successful programming preserves the reserved NVS area, unless a separate deliberate chip erase/recovery is performed. Initial startup enables P0.21 as nRESET; software reset works independently. Disconnect probe power before refitting the CR2450.

## Use Bluetooth

Install Nordic nRF Connect for Mobile, scan for Fidget Counter, connect and subscribe to the State characteristic. Alternatively install the desktop client dependency and run:

```sh
pip install -r firmware/tools/requirements-client.txt
python3 firmware/tools/client.py --seconds 60
python3 firmware/tools/client.py --save
python3 firmware/tools/client.py --reset
```

Select --address when several units are present. Reset clears both directional counters and total. Wait for confirmation before disconnecting. The pilot permits one unbonded BLE client; connected clients can read and reset it. It has no owner authentication or production phone application.

Service:76b8a000-5aa4-4c10-b5df-0da684303f21. State:...a001, read/notify. Control:...a002, write with response; exact ASCII ZERO or SAVE (four bytes). Notifications are at most10Hz while connected; advertising interval is0.5–1.0s.

State is20bytes, little endian:

| Offset | Field |
| --- | --- |
| 0 | Protocol version1 |
| 1 | Flags: bit0 sensor fault;1 storage fault;2 unsaved counts;3 sample gap/rebased unfinished turn;4 saturation |
| 2–3 | Angle in0.0625° units |
| 4–7 | Increasing-angle turns, uint32 |
| 8–11 | Decreasing-angle turns, uint32 |
| 12–15 | Total turns, saturating uint32 |
| 16–19 | State sequence, uint32 |

Counts checkpoint after2s without accepted motion, at most every60s during continuous motion, or on SAVE/ZERO. CRC-protected NVS uses two4KiB pages. Abrupt power loss can lose counts since the last checkpoint and always loses an unfinished turn. Storage errors are reported; the firmware never silently erases damaged stored data.

## Sensor and qualification

SCL=P0.26, SDA=P0.27, Hall INT=P0.28 (input, polling pilot), reset=P0.21; P0.29 is unused. LDO only. External32MHz and32.768kHz crystals are used with a conservative500ppm sleep-clock allowance.

TMAG3001A2 is verified by TI manufacturer/device IDs at address0x34. The driver uses4x averaging, XY angle, ±240mT XY range and5ms wake/sleep; it latches address0x34 before sleeping and rearms after reads. One burst captures X/Y/Z, conversion status, unsigned13-bit angle and magnitude/diagnostics. POR, diagnostics, weak/clipped field and invalid angles suppress counting and trigger recovery. The 1° anchored noise deadband preserves slow movement.

Polling sleeps10ms between reads. A gap over50ms or apparent jump over120° discards unfinished travel instead of inventing counts. Flash erases, radio scheduling, very fast rotation and sensor faults can therefore cause undercounts and must be measured. Target the first acceptance tests at no more than10turns/s. Battery runtime, magnetic thresholds, distortion from the steel bearing/ring/phone, oscillator accuracy, peak current, BLE stability, stack high-water and count accuracy are **not physically validated**. CRC on I2C is disabled in this initial driver; NVS data CRC is enabled.

Before batch release, complete the [assembly acceptance steps](../ASSEMBLY.md), compare at least100 rotations in each direction with a reference, test wrap/backtracking/noise/removal/reconnect/save/reset/power cycling and measure current on the final magnetic stack. This firmware does not convert the digitally checked pilot into a production-qualified product.

References: [TI TMAG3001 SLYS053C](https://www.ti.com/lit/ds/symlink/tmag3001.pdf), sections6.3.5,6.4,6.5.2.5 and7; [Nordic nRF52810 specification](https://infocenter.nordicsemi.com/pdf/nRF52810_PS_v1.5.pdf); [Zephyr LTS source](https://github.com/zephyrproject-rtos/zephyr/tree/19aeae80fac00aa3310ef9a26d08fab4502e812f).
