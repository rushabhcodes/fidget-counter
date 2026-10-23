# Programming the Fidget Counter — TC2030 release 1.0.15

Release 1.0.15 uses the **TC2030-NL no-legs footprint**, imported from `@tsci/tscircuit.standard-jst-programmer@0.8.0`. It replaces the custom five-pad row with six Ø0.7874 mm contacts on a 1.27 mm grid and three Ø0.9906 mm non-plated alignment holes. No connector is fitted and no solder paste is applied. Use the **TC2030-IDC-NL-050** cable with the linked [Standard JST programmer 0.8.0](https://tscircuit--standard-jst-programmer-v0-8-0.tscircuit.app/#file=circuits%2Fupward.circuit.tsx), programmer header **J4 TAG**. The footprint follows [Tag-Connect's Rev B drawing](https://www.tag-connect.com/wp-content/uploads/bsk-pdf-manager/2019/12/TC2030-IDC-NL-Datasheet-Rev-B.pdf).

**Remove the CR2032 before plugging in this programmer.** Its pin 1 is a fixed **3.3 V output**, not a voltage-sense input. Its pin 6 carries **USB 5 V** and is deliberately unconnected on this board. Do not fit a battery while the programmer supplies the board. This J4 pinout is specific to the linked programmer; a generic six-pin SWD cable may assign pin 6 to SWO instead.

This repository contains the PCB design, **no application firmware, bootloader or flashable HEX**. Obtain a complete firmware image for this board before flashing.

## Access and identify the contacts

Program before enclosure assembly. For an assembled device, release the cap, push both PCB latch tips outward 0.6 mm and lift the PCB with its holder; see [battery service](MECHANICAL.md#pressing-and-battery-service). Remove the coin cell. The programming contacts are now on the **top face**, centered at **(0, −13.3) mm**, near the edge opposite the antenna. The probe approaches from above and has a clear 10.4 × 7.8 mm courtyard. Hold the no-legs probe in place; use a support that clears the underside holder and protruding alignment pins. A retention clip requires separate underside access.

Viewed from above with the antenna pointing up:

```text
                       Antenna ↑

                         PCB top
               2 DIO     4 CLK     6 NC (5 V on cable)
                  ●         ●         ●           ○
          ○                                       alignment holes
                  ●         ●         ●           ○
               1 3V3     3 RESET   5 GND
                   pin 1 / TC2030 legend
```

The asymmetric three-hole pattern keys the probe. Match pin 1 at both the probe and the programmer's unshrouded IDC header before applying USB power. A 2.54 mm IDC plug or a 10-pin Cortex cable does not directly mate with J4.

| TC2030 contact | Programmer 0.8.0 signal | Board net | PCB top-view center, mm |
|---|---|---|---|
| 1 | Fixed 3.3 V output | VBAT, same rail as BT1 positive | (−1.27, −13.935) |
| 2 | SWDIO | U1 physical pin 26 | (−1.27, −12.665) |
| 3 | Open-drain NRST | NRESET, U1 P0.21 / pin 24; 100 kΩ pull-up | (0, −13.935) |
| 4 | SWCLK | U1 physical pin 25 | (0, −12.665) |
| 5 | GND | Board ground | (+1.27, −13.935) |
| 6 | Fixed USB 5 V output | **NC; isolated pad, no trace** | (+1.27, −12.665) |

The alignment-hole centers are (−2.54, −13.3), (+2.54, −12.284) and (+2.54, −14.316) mm. The library's central keepout blocks routing on both layers. An added top-side keepout clears the ground pours by 0.508 mm from the contact edges; the five fanout branches leave the array outward. The footprint is DNL and adds no assembled height.

## Power and flash with the linked programmer

1. Disconnect programmer USB, remove the CR2032 and disconnect any bench supply.
2. Connect only the TC2030 cable between programmer J4 and J_DEBUG. Leave the JST target connectors empty. J4 bypasses the voltage selector and current monitor; its pin 1 is always 3.3 V when USB is powered. Pin 6 stays unconnected on the target.
3. Apply USB power and confirm approximately 3.3 V between contacts 1 and 5 before programming. The MCU and sensor accept 3.3 V. Keep the probe stable throughout erase/write/verify.
4. Use the programmer's version-matched CMSIS-DAP firmware and [OpenOCD](https://openocd.org/pages/getting-openocd.html). The example below uses the **OpenOCD 0.12.0** target path `target/nrf52.cfg`. Current development versions may use `target/nordic/nrf52.cfg`; select the installed path.

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

Disconnect USB before removing the probe. Refit the cell only after disconnecting programmer power. Power-cycle the board and verify BLE, angle sensing and count reset with suitable application firmware. No physical target has been flashed as part of this layout change.

## Optional standard Cortex / J-Link adapter

A SEGGER J-Link can use this same footprint through a correctly wired TC2030 adapter. Its **VTref is an input**, unlike the linked programmer's pin-1 output. Map Cortex 2×5 pins 1→TC2030 1, 2→2, 4→4, 3/5→5 and 10→3; leave TC2030 6 unconnected. Check the adapter pinout against [SEGGER's Cortex connector assignments](https://kb.segger.com/9-pin_JTAG/SWD_connector); do not connect a differently wired cable directly.

With a J-Link, either power from the coin cell and disable all probe power outputs, or remove the cell and supply regulated 3.0–3.3 V through contacts 1 and 5. VTref senses that rail. Never connect two supplies or apply 5 V. The nRF Util procedure below is for **J-Link**, not for the linked CMSIS-DAP programmer.

## Optional J-Link tools

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

Disconnect the fixture, power-cycle the board, and check the application's documented behavior. With suitable fidget firmware, confirm BLE discovery, Hall angle changes during rotation, and count clearing after a continuous two-second cap press. There is no onboard LED for a generic blink test. Flash verification checks the stored image; it does not verify these application functions.

## Recover or troubleshoot

If the probe is absent from `device list`, check USB, J-Link installation and OS permissions. If the probe is present but the MCU cannot be detected, check V-to-G voltage under load, common ground, probe VTref, the six-contact pin map above, and spring-contact pressure. Keep wires short and select SWD rather than JTAG if using another tool. A populated prototype is required to validate fixture clearance and contact reliability.

If a previously programmed device has access protection enabled, use [Nordic's recovery command](https://docs.nordicsemi.com/r/bundle/nrfutil/page/nrfutil-device/guides/programming_recovery.html) only when loss of its contents is acceptable. **Recovery erases user flash and UICR, including firmware and stored data.** It is not a routine prerequisite for every flash:

```sh
nrfutil device recover --serial-number "$FIDGET_PROBE_SN"
```

After successful recovery, rerun the complete-image programming command above. If verification succeeds but the application does not run, check the firmware target, complete image/stack, clock configuration, DCDCEN=0 and board pin map. Holding the cap button does not enter a factory bootloader.

## Verification status

Updated 23 October 2026 for release 1.0.15. Package version, pad/hole geometry and the programmer-specific pinout were checked against the linked 0.8.0 source and saved circuit. See `validation/programming-interface.json` and `validation/pcb-mount-check-summary.json` for the measured layout checks. Probe fit, contact reliability and actual flashing require a populated prototype. These changes are included in release 1.0.15.
