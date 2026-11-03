#ifndef FIDGET_ROTATION_COUNTER_H
#define FIDGET_ROTATION_COUNTER_H
#include <stdbool.h>
#include <stdint.h>

#define FIDGET_TURN_Q4 5760
#define FIDGET_DEADBAND_Q4 16
#define FIDGET_MAX_DELTA_Q4 1920
#define FIDGET_MAX_SAMPLE_GAP_MS 50

struct rotation_counter {
	uint32_t forward;
	uint32_t reverse;
	uint32_t sample_ms;
	uint16_t reference_q4;
	int32_t remainder_q4;
	bool tracking;
};
enum rotation_result { ROTATION_STILL, ROTATION_MOVED, ROTATION_COUNTED, ROTATION_REBASED };
void rotation_invalidate(struct rotation_counter *counter);
void rotation_reset(struct rotation_counter *counter);
enum rotation_result rotation_update(struct rotation_counter *counter, uint16_t angle_q4,
				     uint32_t now_ms);
uint32_t rotation_total(const struct rotation_counter *counter);
#endif
