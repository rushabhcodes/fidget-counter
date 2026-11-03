#include "rotation_counter.h"
#include <limits.h>
#include <string.h>

void rotation_invalidate(struct rotation_counter *c)
{
	c->tracking = false;
	c->remainder_q4 = 0;
}
void rotation_reset(struct rotation_counter *c)
{
	memset(c, 0, sizeof(*c));
}
uint32_t rotation_total(const struct rotation_counter *c)
{
	return UINT32_MAX - c->forward < c->reverse ? UINT32_MAX : c->forward + c->reverse;
}
enum rotation_result rotation_update(struct rotation_counter *c, uint16_t angle, uint32_t now)
{
	if (angle > FIDGET_TURN_Q4) {
		rotation_invalidate(c);
		return ROTATION_REBASED;
	}
	if (angle == FIDGET_TURN_Q4) { angle = 0; }
	if (!c->tracking || (uint32_t)(now - c->sample_ms) > FIDGET_MAX_SAMPLE_GAP_MS) {
		c->reference_q4 = angle;
		c->sample_ms = now;
		c->remainder_q4 = 0;
		c->tracking = true;
		return ROTATION_REBASED;
	}
	c->sample_ms = now;
	int32_t delta = (int32_t)angle - c->reference_q4;
	if (delta > FIDGET_TURN_Q4 / 2) { delta -= FIDGET_TURN_Q4; }
	if (delta < -FIDGET_TURN_Q4 / 2) { delta += FIDGET_TURN_Q4; }
	if (delta > FIDGET_MAX_DELTA_Q4 || delta < -FIDGET_MAX_DELTA_Q4) {
		c->reference_q4 = angle;
		c->remainder_q4 = 0;
		return ROTATION_REBASED;
	}
	/* Hold the reference through sub-degree noise, preserving eventual slow motion. */
	if (delta < FIDGET_DEADBAND_Q4 && delta > -FIDGET_DEADBAND_Q4) {
		return ROTATION_STILL;
	}
	c->reference_q4 = angle;
	c->remainder_q4 += delta;
	if (c->remainder_q4 >= FIDGET_TURN_Q4) {
		if (c->forward != UINT32_MAX) { c->forward++; }
		c->remainder_q4 -= FIDGET_TURN_Q4;
		return ROTATION_COUNTED;
	}
	if (c->remainder_q4 <= -FIDGET_TURN_Q4) {
		if (c->reverse != UINT32_MAX) { c->reverse++; }
		c->remainder_q4 += FIDGET_TURN_Q4;
		return ROTATION_COUNTED;
	}
	return ROTATION_MOVED;
}
