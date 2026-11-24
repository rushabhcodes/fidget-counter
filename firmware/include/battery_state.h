#ifndef FIDGET_BATTERY_STATE_H
#define FIDGET_BATTERY_STATE_H

#include <stdbool.h>
#include <stdint.h>

#define BATTERY_LOW_PERCENT 20U
#define BATTERY_RECOVER_PERCENT 25U
#define BATTERY_SAMPLE_INTERVAL_MS 60000U
#define BATTERY_STATUS_SIZE 5U

struct battery_state {
	uint16_t millivolts;
	uint8_t percent;
	uint8_t recovery_samples;
	bool initialized;
	bool valid;
	bool low;
};

uint8_t battery_estimate_percent(uint16_t millivolts);
/* Negative values and out-of-range readings invalidate telemetry, preserving
 * the last low-battery latch. Only successful readings enter the filter. */
bool battery_update(struct battery_state *state, int32_t millivolts);
void battery_encode(const struct battery_state *state, uint8_t data[BATTERY_STATUS_SIZE]);

#endif
