# RevC battery reporting

Targets **RevC / CR2450 / nRF52810-QFAA**. VBAT directly supplies the MCU. The SAADC uses its internal VDD input, **0.6 V internal reference, 1/6 gain, 12-bit resolution and 16× oversampling**. No external divider or GPIO is needed. Measurements run at boot and every **60 seconds**, including while disconnected. This does not change rotation polling or add a thread. [Nordic SAADC specification](https://docs.nordicsemi.com/r/bundle/ps_nrf52810/page/saadc.html).

## App API

| Service | Characteristic | Properties | Value |
|---|---|---|---|
| Standard Battery Service `180F` | Battery Level `2A19` | Read, notify | One unsigned byte, estimated `0..100%` |
| Fidget `76b8a000-5aa4-4c10-b5df-0da684303f21` | Battery Status `76b8a003-5aa4-4c10-b5df-0da684303f21` | Read, notify | Five bytes, layout below |

Battery Status provides percentage, filtered voltage and warning/error state together. Discover services by UUID and subscribe/read on each connection; re-subscribe after reconnecting. Enabling notifications requests the current value. Status notifies after each periodic sample; standard Battery Level notifies when its value changes or it is subscribed. Transient notification-buffer exhaustion is retried on the existing system workqueue, keeping that wait out of the rotation sampling thread.

Battery Status is little-endian:

| Offset | Field |
|---|---|
| 0 | Payload version `1` |
| 1 | Flags: bit 0 = valid measurement; bit 1 = low-battery latch; other bits reserved |
| 2 | Estimated percentage `0..100`, or `255` when unavailable |
| 3–4 | Filtered millivolts, uint16, or `65535` when unavailable |

`01 01 32 22 0B` means **50%, 2850 mV, valid, not low**. `01 02 FF FF FF` means unavailable, retaining the last known low warning. Show **battery unavailable** when validity is clear. Standard `2A19` reads return an ATT error in that case; the firmware never invents a 0%/100% reading or sends a reserved percentage byte through the standard characteristic.

The existing 20-byte counter State and ZERO/SAVE commands keep their UUIDs, layout and protocol version. Two previously reserved State flag bits are added: **bit 5 low battery**, **bit 6 battery measurement fault**. ZERO preserves these flags. The [Python client](tools/client.py) subscribes to Battery Status and emits `battery_percent`, `battery_millivolts`, `battery_valid` and `low_battery`; unavailable numeric fields are JSON `null`.

App decoding example:

```js
function decodeBattery(bytes) {
  if (bytes.length !== 5 || bytes[0] !== 1 || (bytes[1] & ~3)) {
    throw new Error("Unsupported battery payload")
  }
  const valid = Boolean(bytes[1] & 1)
  const mv = bytes[3] | (bytes[4] << 8)
  if (valid ? (bytes[2] > 100 || mv < 1700 || mv > 3600)
            : (bytes[2] !== 255 || mv !== 65535)) {
    throw new Error("Invalid battery payload")
  }
  return {
    percentage: valid ? bytes[2] : null,
    millivolts: valid ? mv : null,
    lowBattery: Boolean(bytes[1] & 2),
    valid,
  }
}
```

## Estimate and warning

The warning starts at **20% or below** and clears after **three consecutive valid readings at 25% or above**. An invalid reading interrupts recovery and preserves the warning. A four-sample exponential voltage filter starts with an immediate first reading. The one-minute interval and filtering mean later changes take minutes to settle.

`src/battery_state.c` contains this **provisional engineering curve**, interpolated and clamped to 0–100%. It is not calibrated to measured RevC capacity:

| mV | % |
|---:|---:|
| 2000 | 0 |
| 2400 | 5 |
| 2600 | 10 |
| 2700 | 20 |
| 2850 | 50 |
| 2950 | 80 |
| 3100 | 100 |

Calibrate it against the chosen cell, load, temperature and qualified cutoff. Primary lithium coin-cell voltage is fairly flat and sags under load, so percentage is approximate. [Energizer application manual](https://data.energizer.com/pdfs/lithiumcoin_appman.pdf).

## Battery life

Runtime and average current are **not measured**. A nominal [620 mAh CR2450](https://energizer.com/wp-content/uploads/2023/11/cr2450.pdf) gives ideal calculations of 517 days at 0.05 mA, 258 days at 0.10 mA, or 52 days at 0.50 mA. These are scenarios, not product claims. Load, radio pulses, temperature, cell age and cutoff reduce usable capacity. The existing firmware polls the Hall sensor every 10 ms and can notify counter state at 10 Hz even at rest; multi-month runtime has not been established.

## Validation

`sh firmware/tools/test.sh` checks interpolation/clamping, monotonicity, filtering, warning hysteresis, interrupted recovery, error handling, exact wire bytes and client decoding alongside the existing counter tests. The nRF52810 cross-build and image verifier check ADC selection, LDO configuration, NVS/UICR boundaries and RAM/flash limits.

Before app release, remove the primary cell and use a regulated adjustable supply to compare reported voltage with a meter, step across warning/recovery thresholds, and test notifications/reconnect/ZERO. Measure post-ADC idle current and peak/radio current on the actual silicon. The application uses one ADC channel, not scan mode. Discharge the intended CR2450 at the real workload to calibrate percentage and runtime, and verify counting during conversions.

No physical target has been flashed or tested for this feature. Use only the RevC image described in [the firmware guide](README.md); the older RevA/CR2032 mechanical branch is separate.
