#include <errno.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/dt-bindings/adc/nrf-adc.h>
#include "battery_adc.h"

/* VBAT directly supplies VDD on RevC. The internal VDD input consumes no GPIO
 * and needs no external divider. Internal 0.6 V reference, 1/6 gain: 3.6 V FS.
 * VDD/4 must not be selected as the reference for a VDD measurement. */
static const struct device *const adc = DEVICE_DT_GET(DT_NODELABEL(adc));

int battery_adc_init(void)
{
	if (!device_is_ready(adc)) { return -ENODEV; }
	const struct adc_channel_cfg channel = {
		.gain = ADC_GAIN_1_6,
		.reference = ADC_REF_INTERNAL,
		.acquisition_time = ADC_ACQ_TIME(ADC_ACQ_TIME_MICROSECONDS, 10),
		.channel_id = 0,
		.input_positive = NRF_SAADC_VDD,
	};
	return adc_channel_setup(adc, &channel);
}

int battery_adc_read_mv(int32_t *millivolts)
{
	int16_t raw;
	const struct adc_sequence sequence = {
		.channels = 1U,
		.buffer = &raw,
		.buffer_size = sizeof(raw),
		.resolution = 12,
		.oversampling = 4,
		.calibrate = true,
	};
	int err = adc_read(adc, &sequence);
	if (err) { return err; }
	if (raw < 0) { return -ERANGE; }
	int32_t mv = raw;
	err = adc_raw_to_millivolts(600, ADC_GAIN_1_6, 12, &mv);
	if (!err) { *millivolts = mv; }
	return err;
}
