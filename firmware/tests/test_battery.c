#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "battery_state.h"

static void settle(struct battery_state *state, int mv)
{
	for (int i = 0; i < 32; i++) { assert(battery_update(state, mv)); }
}

int main(void)
{
	assert(battery_estimate_percent(1700) == 0);
	assert(battery_estimate_percent(3600) == 100);
	assert(battery_estimate_percent(2700) == 20);
	assert(battery_estimate_percent(2850) == 50);
	assert(battery_estimate_percent(2775) == 35);
	for (unsigned mv = 1701; mv <= 3600; mv++) {
		assert(battery_estimate_percent(mv) >= battery_estimate_percent(mv - 1));
		assert(battery_estimate_percent(mv) <= 100);
	}
	struct battery_state state = {0};
	uint8_t data[BATTERY_STATUS_SIZE];
	battery_encode(&state, data);
	const uint8_t unavailable[] = {1, 0, 255, 255, 255};
	assert(!memcmp(data, unavailable, sizeof(data)));
	assert(battery_update(&state, 2850));
	assert(state.valid && !state.low && state.percent == 50);
	battery_encode(&state, data);
	const uint8_t half_full[] = {1, 1, 50, 0x22, 0x0b};
	assert(!memcmp(data, half_full, sizeof(data)));

	settle(&state, 2700);
	assert(state.low && state.percent == 20);
	settle(&state, 2720);
	assert(state.low && state.percent > 20 && state.percent < 25);
	settle(&state, 2740);
	assert(!state.low && state.percent >= 25);
	settle(&state, 2700);
	assert(state.low);
	const uint16_t previous_mv = state.millivolts;
	for (int bad = 0; bad < 4; bad++) {
		const int values[] = {-5, 0, 1699, 3601};
		assert(!battery_update(&state, values[bad]));
		assert(!state.valid && state.low && state.millivolts == previous_mv);
		battery_encode(&state, data);
		assert(data[1] == 2 && data[2] == 255 && data[3] == 255 && data[4] == 255);
	}
	assert(battery_update(&state, 2700));
	assert(state.valid && state.low);
	/* One radio/load-recovery spike must not instantly clear the warning. */
	assert(battery_update(&state, 2800));
	assert(state.low);
	settle(&state, 2700);
	assert(battery_update(&state, 3000) && state.low);
	assert(battery_update(&state, 3000) && state.low);
	assert(!battery_update(&state, -1) && state.low);
	assert(battery_update(&state, 3000) && state.low);
	assert(battery_update(&state, 3000) && state.low);
	assert(battery_update(&state, 3000) && !state.low);
	settle(&state, 3100);
	assert(!state.low && state.percent >= 99);
	/* Recovering from an unavailable reading must not blend fresh low voltage
	 * with stale high voltage and temporarily hide the warning. */
	assert(!battery_update(&state, -1));
	assert(battery_update(&state, 2500));
	assert(state.millivolts == 2500 && state.low);
	puts("Battery: voltage curve, interpolation, smoothing, warning hysteresis, invalid samples and BLE payload passed");
	return 0;
}
