# Programming the Fidget Counter

Program U1 (nRF52810-QFAA) over **Serial Wire Debug (SWD)** using the five existing underside pads. Use a SEGGER J-Link with a 1.27 mm 2×5 Arm Cortex debug adapter and a breakout wired to the pads. A five-probe fixture on 2.00 mm centers is suitable; short, temporarily soldered wires are an alternative for a prototype. Support the board by its edges without loading the components or battery holder.

The board exposes standard SWD **signals** on a custom single-row footprint. It has no fitted 10-pin socket or Tag-Connect footprint, so those cables require a breakout/fixture. No connector or layout change is needed for this procedure.

This repository contains the PCB design, **no application firmware, bootloader or flashable HEX**. `bun run build` generates circuit artifacts. Obtain or build a firmware image for this specific board before flashing. Initial programming uses SWD; Bluetooth updates require a compatible bootloader and application installed separately.

## Access and identify the pads

Program the populated board on the bench before enclosure assembly. For an assembled unit, release the cap by pulling both cap-release tabs outward, then follow [the PCB removal and battery-service instructions](MECHANICAL.md#pressing-and-battery-service) for its enclosure. Lift the PCB with its soldered holder and turn it over. The solid bottom tray provides no programming opening.

Look directly at the **underside**, with the antenna end at the top and the programming row at the bottom. The silkscreen reads left to right:

```text
                    Antenna end
                         ↑
                 PCB underside facing you

             R      C      D      G      V
           RESET  SWDCLK  SWDIO  GND    VBAT
             ●------●------●------●------●
                  2.00 mm center spacing
```

The row reverses to **V G D C R** in top-view coordinates; do not wire an underside fixture from the top-view order. Each land is Ø1.20 mm. Only GND has a Ø0.40 mm plated hole; the others are undrilled surface pads.

## Wire a standard Arm Cortex SWD connector

The table uses the **1.27 mm 2×5 Cortex connector numbering**, including the missing/key pin 7. Follow the adapter's pin-1 mark; a connector's solder side is mirrored relative to its mating face. The larger J-Link 20-pin connector uses different numbering and needs its Cortex adapter. The signal assignments below follow [SEGGER's Cortex connector pinout](https://kb.segger.com/9-pin_JTAG/SWD_connector).

| Cortex connector pin | Probe signal | Board pad / legend | PCB top-view center, mm | Connection on this board |
|---|---|---|---|---|
| 1 | VTref, target-voltage **input** | TP_VDD / V | (−4, −14) | VBAT; same rail as BT1 positive and U1 VDD |
| 2 | SWDIO | TP_SWDIO / D | (0, −14) | U1 physical pin 26 |
| 4 | SWCLK | TP_SWDCLK / C | (+2, −14) | U1 physical pin 25 |
| 3 and 5 | GND | TP_GND / G | (−2, −14) | Board ground; join both on the breakout |
| 10 | nRESET | TP_RESET / R | (+4, −14) | U1 P0.21, physical pin 24; 100 kΩ pull-up |

Leave pins 6 (SWO), 8 (TDI) and 9 unconnected for this J-Link SWD hookup; pin 7 is the key. SWO is not routed on this board. nRESET is optional for basic SWD programming: its reset function must first be enabled in the MCU configuration. VTref, GND, SWDIO and SWCLK are the required connections.

## Power the target

**TP_VDD is directly connected to the primary CR2032.** A probe's VTref senses the target rail; it does not normally power the target. Use one of these setups:

| Setup | Target supply | Probe hookup |
|---|---|---|
| Coin-cell powered | Fit a CR2032 in BT1 | Connect VTref to V and GND to G; keep all probe target-power outputs disabled |
| External bench supply, preferred for repeated programming | **Remove the CR2032**, then connect regulated **3.0 V** positive to V and return to G | Connect VTref to the same V rail; keep other power sources disconnected |

With power off, attach the breakout/probes and check for bridges. Apply power and measure approximately 3.0 V from V to G before connecting to the target in software. Keep the supply stable throughout erase and programming. **Never apply 5 V to V. Remove the CR2032 before connecting any external supply:** this board has no charging or power-isolation circuit. A probe's separately labeled target-power output may be used only if its manual confirms a regulated, compatible voltage and the cell is removed.

After programming, turn off external power before removing temporary wiring or changing the cell. Disconnect the debug probe and power-cycle the board before measuring sleep current.

## Install the programming tools

Install the current standalone [Nordic nRF Util](https://docs.nordicsemi.com/r/bundle/nrfutil/page/guides/installing.html/installing-nrf-util-from-the-web-default) executable and put it on `PATH`. Install the SEGGER J-Link software version required by [Nordic's prerequisites](https://docs.nordicsemi.com/r/bundle/nrfutil/page/guides/installing.html/prerequisites), including the appropriate USB drivers/udev rules for your OS. The commands here use the modern nRF Util with its installable `device` command.

```sh
nrfutil install device
nrfutil device --version
nrfutil device list
```

Copy the J-Link probe's serial number from the first line of its entry, as described in [Nordic's serial-number guide](https://docs.nordicsemi.com/r/bundle/nrfutil/page/nrfutil-device/guides/device-list.html/serial-number). Listing the USB probe alone does not establish that the target is powered or connected.

## Prepare the firmware image

Build for **nRF52810**, with 192 kB flash and 24 kB RAM ([Nordic specification](https://docs.nordicsemi.com/r/bundle/ps_nrf52810/page/keyfeatures_html5.html)). Use this board's pin map from [the firmware pin map below](#firmware-pin-map), including SCL=P0.26, SDA=P0.27, HALL_INT=P0.28 and CAP_PRESS=P0.29. Keep **DCDCEN=0 (LDO mode)**; this PCB has no DC/DC inductors. Its crystals are 32 MHz and 32.768 kHz. A development-kit example needs its board pins, clocks and regulator settings adapted before use here.

Produce an Intel HEX with the correct addresses and all required firmware regions. For an application that depends on a separate BLE stack/SoftDevice, bootloader or settings, use the firmware project's complete merged HEX. An application-only HEX that assumes an installed stack cannot boot after a full erase. Let that firmware project define its memory layout; the 192 kB flash also has to accommodate any stack and bootloader.

Keep readback protection disabled during initial bring-up so programming verification and debugging remain available. If hardware reset is required, configure P0.21 as nRESET through the firmware/toolchain's UICR reset configuration. The cap switch is a separate GPIO and is not a hardware reset button.

## Firmware pin map

| Function | GPIO / physical QFAA pin |
|---|---|
| I2C SCL | P0.26 / 38 |
| I2C SDA | P0.27 / 39 |
| Hall interrupt | P0.28 / 40 |
| Cap press (SW1 at X=0, Y=−5 mm) | P0.29 / 41 |
| SWDIO | 26 |
| SWDCLK | 25 |
| Optional nRESET | P0.21 / 24 |

## Detect, program, verify and run

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

Disconnect the fixture, power-cycle the board, and check the application's documented behavior. With suitable fidget firmware, confirm BLE discovery, Hall angle changes during rotation, and count clearing after a continuous two-second cap press. There is no onboard LED for a generic blink test. Flash verification checks the stored image; it does not verify these application functions.

## Recover or troubleshoot

If the probe is absent from `device list`, check USB, J-Link installation and OS permissions. If the probe is present but the MCU cannot be detected, check V-to-G voltage under load, common ground, probe VTref, the **R C D G V** underside order, and spring-contact pressure. Keep wires short and select SWD rather than JTAG if using another tool. A populated prototype is required to validate fixture clearance and contact reliability.

If a previously programmed device has access protection enabled, use [Nordic's recovery command](https://docs.nordicsemi.com/r/bundle/nrfutil/page/nrfutil-device/guides/programming_recovery.html) only when loss of its contents is acceptable. **Recovery erases user flash and UICR, including firmware and stored data.** It is not a routine prerequisite for every flash:

```sh
nrfutil device recover --serial-number "$FIDGET_PROBE_SN"
```

After successful recovery, rerun the complete-image programming command above. If verification succeeds but the application does not run, check the firmware target, complete image/stack, clock configuration, DCDCEN=0 and board pin map. Holding the cap button does not enter a factory bootloader.

## Verification status

Documentation checked 21 October 2026 against the 1.0.9 board imported into GitHub in PR #1. Pad names, positions, dimensions, underside orientation and MCU/power connections were cross-checked against `index.circuit.tsx`, `parts.tsx`, `published.circuit.json` and the source-defined underside legend. Connector assignments and nRF Util commands were checked against the linked manufacturer documentation. This documentation change leaves the PCB layout unchanged. No physical target was flashed, and fixture fit and programming reliability remain untested.
