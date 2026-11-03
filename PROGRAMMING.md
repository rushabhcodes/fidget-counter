> Current RevC is rotation-only. SW1, R5, C17 and CAP_PRESS are removed; P0.29 is explicitly unused. The five-pin programmer and R4/nRESET remain. Pilot firmware and software count reset are in firmware/; no physical count-clear input is fitted.

# V5 enclosure access update

For the current push-fit enclosure, pull the cap assembly straight off evenly, supporting the appropriate bearing race if it stays on the base. Remove the two nylon PCB screws and lift the PCBA for cable/battery access. See [service instructions](MECHANICAL.md); do not force through the bearing balls.

---

# Programming the Fidget Counter — JST-SH PCB with V5 enclosure

J_DEBUG is a fitted **JST SM05B-SRSS-TB(LF)(SN)** side-entry SMT header, with five contacts on a 1.0 mm pitch. It uses `StandardJstSwdResetSide` from `@tsci/tscircuit.standard-jst-programmer@0.8.0`, with its exact imported footprint, supplier identity **JLCPCB C136657**, and cached supplier 3D models. It replaces the six bare Tag-Connect pads and all three alignment holes. All five signal lands and both mounting tabs receive solder paste.

Use a **straight-through five-way JST-SH cable** with **SHR-05V-S-B** mating housings between J_DEBUG and **J3 / 5PIN** on the [Standard JST programmer 0.8.0](https://tscircuit--standard-jst-programmer-v0-8-0.tscircuit.app/#file=circuits%2Fprogrammer.circuit.tsx). Check continuity **1→1 through 5→5**; wire colors alone do not identify contacts. [JST's SH drawing](https://www.jst-mfg.com/product/pdf/eng/eSH.pdf) specifies the mating housing and the 7.0 × 4.25 × 2.9 mm header body. The PCB footprint courtyard is approximately 8.30 × 6.04 mm. The five-pin extension follows this programmer's assignment; generic five-pin debug cables may differ.

**Select 3V3 and remove the CR2450 before connecting the programmer.** J3 pin 1 follows the programmer's **3V3 / 5V selector** and is directly connected to this board's VBAT rail; it is not a voltage-sense input. The 5V setting must never be used with this board. Disconnect the cable before changing the selector. The programmer's SWD/reset logic is fixed at 3.3 V. Leave programmer J1, J2 and J4 empty while using J3.

The repository now includes [RevC pilot firmware](firmware/README.md), a custom nRF52810 board definition, tests and a CI build. Download the complete HEX only from a successful Firmware run for the intended commit, or build it using that guide. It includes Zephyr's BLE controller and application; no separate SoftDevice or bootloader is needed. Physical flashing and application acceptance remain unverified until tested on a populated unit.

## Access and identify the contacts

Program before enclosure assembly. For an assembled device, pull off the cap/bearing assembly evenly, then remove the two nylon PCB screws and lift the board/holder; see [the service guide](MECHANICAL.md). Remove the coin cell. J_DEBUG remains on the top face at (0, −13.3) mm with cable entry toward −Y. Lift the PCB for side-entry cable access, then disconnect the cable before reassembly.

Viewed from above with the antenna pointing up:

```text
                       Antenna ↑

     1 VOUT     2 DIO     3 GND     4 CLK     5 RESET
        ■         ■         ■         ■         ■
        ┌───────────────────────────────────────┐
        │          J_DEBUG: JST-SH 1 mm          │
        └──────────── cable entry ↓ ────────────┘
```

The marked pin 1 is on the left in this PCB top view. The plug's mating-face view can be mirrored; use JST's contact numbering and a continuity check. The shroud keys the mating housing; a reversed-wire cable is still electrically incorrect.

| JST contact | Programmer J3 signal | Board connection | PCB solder-land center, mm |
|---|---|---|---|
| 1 | VOUT; select **3V3** | VBAT, same rail as BT1 positive | (−1.999615, −11.3001183) |
| 2 | SWDIO | U1 physical pin 26 | (−0.998855, −11.3001183) |
| 3 | GND | Board ground | (+0.000635, −11.3001183) |
| 4 | SWCLK | U1 physical pin 25 | (+1.000125, −11.3001183) |
| 5 | Open-drain NRST | NRESET, U1 P0.21 / pin 24; existing 100 kΩ pull-up | (+2.000885, −11.3001183) |

The two mechanical solder tabs are not additional signal contacts. There are no programming alignment holes or bare programming test-pad row. The V5 fitted-header clearance is regenerated against the actual supplier STEP and a conservative 2.92 mm-high courtyard envelope through the full 360-degree rotation sweep at its fixed height. See `validation/jst-connector-clearance.json` for measured CAD results. Cable mating and printed tolerances still need a prototype.

## Program the supplied pilot firmware

After building or downloading the verified image, use the supplied `firmware/tools/flash.py` (or `flash.py` beside an extracted artifact). It checks the HEX address range/vector table and nRF52810 identity before write/verify/reset. See [the exact command and build instructions](firmware/README.md#flash-before-assembly). The manual OpenOCD/nRF Util alternatives below remain available.

## Power and flash with the linked programmer

1. Disconnect programmer USB, remove the CR2450 and disconnect any bench supply.
2. Set the programmer selector to **3V3** with the target cable disconnected. Connect only the straight-through five-pin cable between **J3 / 5PIN** and J_DEBUG.
3. Apply USB power and confirm approximately **3.3 V between J_DEBUG pins 1 and 3** before programming. Keep the connector fully engaged throughout erase/write/verify.
4. Use the programmer's version-matched CMSIS-DAP firmware and [OpenOCD](https://openocd.org/pages/getting-openocd.html). The example below uses the **OpenOCD 0.12.0** target path `target/nrf52.cfg`. Current development versions may use `target/nordic/nrf52.cfg`; select the installed path. The initial software-reset procedure does not require nRESET to be enabled in UICR.

```sh
# Read/identify the powered target first; require nRF52810.
openocd -f interface/cmsis-dap.cfg \
  -c "transport select swd" -f target/nrf52.cfg \
  -c "adapter speed 1000" -c "reset_config none" \
  -c "init; halt; flash info 0; shutdown"

# Programs and erases affected sectors: use the complete board-specific HEX.
openocd -f interface/cmsis-dap.cfg \
  -c "transport select swd" -f target/nrf52.cfg \
  -c "adapter speed 1000" -c "reset_config none" \
  -c "program {/absolute/path/to/fidget-counter-complete.hex} verify reset exit"
```

The `program … verify reset exit` sequence is from [OpenOCD's programming guide](https://openocd.org/doc/html/Flash-Programming.html). The [0.12.0 nRF52 configuration](https://github.com/openocd-org/openocd/blob/v0.12.0/tcl/target/nrf52.cfg) uses a software system reset, so initial flashing does not depend on P0.21 already being configured as nRESET. The command erases sectors that it writes; it does not promise a complete chip erase or preservation of stored calibration/counts. A deliberate full erase or access-protection recovery requires the appropriate tool procedure and loses existing data. Require successful write **and verify** output.

Disconnect USB before unplugging the JST cable. Refit the cell only after disconnecting programmer power. Power-cycle the board and verify BLE, angle sensing and full-turn counting/reset using [the assembly acceptance steps](ASSEMBLY.md#7-check-the-finished-device). No physical target has been flashed as part of this layout change.

## Optional standard Cortex / J-Link adapter

A SEGGER J-Link can use J_DEBUG through a correctly wired **five-pin JST-SH adapter**. Its **VTref is an input**, unlike programmer J3's pin-1 power output. Map Cortex 2×5 pins **1→JST 1, 2→JST 2, 4→JST 4, 3/5→JST 3 and 10→JST 5**. Check the adapter against [SEGGER's Cortex connector assignments](https://kb.segger.com/9-pin_JTAG/SWD_connector) and the JST contact numbering before connecting it.

With a J-Link, either power from the coin cell with all probe power outputs disabled, or remove the cell and supply regulated 3.0–3.3 V through JST contacts **1 and 3**. VTref senses that rail. Never connect two supplies or apply 5 V. The nRF Util procedure below is for **J-Link**, not for the linked CMSIS-DAP programmer.

## Optional J-Link tools

Install the current standalone [Nordic nRF Util](https://docs.nordicsemi.com/r/bundle/nrfutil/page/guides/installing.html/installing-nrf-util-from-the-web-default) executable and put it on `PATH`. Install the SEGGER J-Link software version required by [Nordic's prerequisites](https://docs.nordicsemi.com/r/bundle/nrfutil/page/guides/installing.html/prerequisites), including the appropriate USB drivers/udev rules for your OS. The commands here use the modern nRF Util with its installable `device` command.

```sh
nrfutil install device
nrfutil device --version
nrfutil device list
```

Copy the J-Link probe's serial number from the first line of its entry, as described in [Nordic's serial-number guide](https://docs.nordicsemi.com/r/bundle/nrfutil/page/nrfutil-device/guides/device-list.html/serial-number). Listing the USB probe alone does not establish that the target is powered or connected.

## Prepare the firmware image

Build for **nRF52810**, with 192 kB flash and 24 kB RAM ([Nordic specification](https://docs.nordicsemi.com/r/bundle/ps_nrf52810/page/keyfeatures_html5.html)). Use this board's pin map from [the firmware pin map below](#firmware-pin-map), including SCL=P0.26, SDA=P0.27 and HALL_INT=P0.28. P0.29 is unused in the rotation-only revision; there is no CAP_PRESS input. Keep **DCDCEN=0 (LDO mode)**; this PCB has no DC/DC inductors. Its crystals are 32 MHz and 32.768 kHz. A development-kit example needs its board pins, clocks and regulator settings adapted before use here.

Produce an Intel HEX with the correct addresses and all required firmware regions. For an application that depends on a separate BLE stack/SoftDevice, bootloader or settings, use the firmware project's complete merged HEX. An application-only HEX that assumes an installed stack cannot boot after a full erase. Let that firmware project define its memory layout; the 192 kB flash also has to accommodate any stack and bootloader.

Keep readback protection disabled during initial bring-up so programming verification and debugging remain available. If hardware reset is required, configure P0.21 as nRESET through the firmware/toolchain's UICR reset configuration. P0.29 is unused; the cap switch and its circuit have been removed. Hardware nRESET remains available through J_DEBUG.

## Firmware pin map

| Function | GPIO / physical QFAA pin |
|---|---|
| I2C SCL | P0.26 / 38 |
| I2C SDA | P0.27 / 39 |
| Hall interrupt | P0.28 / 40 |
| P0.29 / pin41 | Unused in rotation-only RevC; no cap button |
| SWDIO | 26 |
| SWDCLK | 25 |
| Optional nRESET | P0.21 / 24 |

## Optional J-Link programming

The following examples use a POSIX shell (Linux/macOS). Replace both values with your probe serial number and the absolute path to your board-specific, complete HEX. Run each step only after the preceding command succeeds.

```sh
FIDGET_PROBE_SN='REPLACE_WITH_PROBE_SERIAL'
FIDGET_FIRMWARE_HEX='/absolute/path/to/fidget-counter-complete.hex'

nrfutil device device-info --serial-number "$FIDGET_PROBE_SN"
```

Confirm that the detected target is **nRF52810** before proceeding. Stop and check the wiring/adapter if another device is reported; do not force a different device identity.

**The next command erases the existing application, bootloader, saved counts/calibration and UICR configuration.** Use it for initial programming or a deliberate full replacement with a complete image. Back up any required existing data first. Its erase, readback verification and software-reset options follow [Nordic's programming options](https://docs.nordicsemi.com/r/bundle/nrfutil/page/nrfutil-device/guides/programming.html/programming-options).

```sh
nrfutil device program \
  --serial-number "$FIDGET_PROBE_SN" \
  --firmware "$FIDGET_FIRMWARE_HEX" \
  --options chip_erase_mode=ERASE_ALL,verify=VERIFY_READ,reset=RESET_SYSTEM
```

Require a successful programming and verification result. `RESET_SYSTEM` starts the application through SWD without depending on P0.21 already being configured as nRESET. If the image enables readback protection at startup, it may prevent later readback/debugging; leave protection off for this initial procedure. Full erase also removes any previously enabled UICR pin-reset configuration, which must be restored by the new image or the programming tool when needed.

Disconnect the cable, power-cycle the board, and check the application's documented behavior. With suitable fidget firmware, confirm BLE discovery, Hall angle changes during rotation, and count accuracy using the chosen application. There is no cap button or physical count-clear action in RevC. There is no onboard LED for a generic blink test. Flash verification checks the stored image; it does not verify these application functions.

## Recover or troubleshoot

If the probe is absent from `device list`, check USB, J-Link installation and OS permissions. If the probe is present but the MCU cannot be detected, check V-to-G voltage under load, common ground, probe VTref, the five-contact pin map above, and full connector engagement. Keep wires short and select SWD rather than JTAG if using another tool. A populated prototype is required to validate cable access and contact reliability.

If a previously programmed device has access protection enabled, use [Nordic's recovery command](https://docs.nordicsemi.com/r/bundle/nrfutil/page/nrfutil-device/guides/programming_recovery.html) only when loss of its contents is acceptable. **Recovery erases user flash and UICR, including firmware and stored data.** It is not a routine prerequisite for every flash:

```sh
nrfutil device recover --serial-number "$FIDGET_PROBE_SN"
```

After successful recovery, rerun the complete-image programming command above. If verification succeeds but the application does not run, check the firmware target, complete image/stack, clock configuration, DCDCEN=0 and board pin map. There is no cap button or onboard bootloader-entry input.

## Verification status

Updated for1.0.28, tscircuit0.0.3060 and the two-part push-fit enclosure. The exact five-pin side-entry footprint/pinout comes from @tsci/tscircuit.standard-jst-programmer@0.8.0; its C136657 models remain cached under imports/SM05B_SRSS_TB. See validation/programming-interface.json for pinout, stencil,0.13mm connector clearances and clock constraints, and validation/jst-connector-clearance.json for all11 caps. The fresh-routing guard retains all28 fitted geometries, real electrical pin attributes and actual pin-net membership. Actual cable fit, connector retention, flashing and pilot firmware behavior still need a populated prototype.
