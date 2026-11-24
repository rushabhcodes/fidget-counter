#include "battery_state.h"
#include <stddef.h>

/* Provisional Li/MnO2 voltage model for the RevC CR2450. These are engineering
 * starting points, not a calibrated remaining-capacity measurement. Replace
 * the table after measuring the chosen cell at the actual load/temperature. */
static const struct { uint16_t mv; uint8_t percent; } curve[] = {
	{2000, 0}, {2400, 5}, {2600, 10}, {2700, 20},
	{2850, 50}, {2950, 80}, {3100, 100},
};

uint8_t battery_estimate_percent(uint16_t millivolts)
{
	if (millivolts <= curve[0].mv) { return 0; }
	for (size_t i = 1; i < sizeof(curve) / sizeof(curve[0]); i++) {
		if (millivolts <= curve[i].mv) {
			uint32_t span = curve[i].mv - curve[i - 1].mv;
			uint32_t step = (millivolts - curve[i - 1].mv) *
				(curve[i].percent - curve[i - 1].percent);
			return curve[i - 1].percent + (step + span / 2) / span;
		}
	}
	return 100;
}

bool battery_update(struct battery_state *state, int32_t millivolts)
{
	if (millivolts < 1700 || millivolts > 3600) {
		state->valid = false;
		state->initialized = false;
		state->recovery_samples = 0;
		return false;
	}
	/* Four-sample exponential smoothing, with an immediate first measurement. */
	state->millivolts = state->initialized ?
		(uint16_t)((3U * state->millivolts + (uint32_t)millivolts + 2U) / 4U) :
		(uint16_t)millivolts;
	state->initialized = true;
	state->valid = true;
	state->percent = battery_estimate_percent(state->millivolts);
	if (state->percent <= BATTERY_LOW_PERCENT) {
		state->low = true;
		state->recovery_samples = 0;
	} else if (state->low && state->percent >= BATTERY_RECOVER_PERCENT) {
		if (++state->recovery_samples >= 3) {
			state->low = false;
			state->recovery_samples = 0;
		}
	} else {
		state->recovery_samples = 0;
	}
	return true;
}

void battery_encode(const struct battery_state *state, uint8_t data[BATTERY_STATUS_SIZE])
{
	data[0] = 1;
	data[1] = (state->valid ? 1U : 0U) | (state->low ? 2U : 0U);
	data[2] = state->valid ? state->percent : UINT8_MAX;
	uint16_t mv = state->valid ? state->millivolts : UINT16_MAX;
	data[3] = mv & 0xff;
	data[4] = mv >> 8;
}
