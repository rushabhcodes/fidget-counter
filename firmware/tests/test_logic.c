#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>
#include "rotation_counter.h"
#include "tmag3001_frame.h"

static uint32_t tick;
static enum rotation_result at(struct rotation_counter *c, int angle)
{
	tick += 10;
	return rotation_update(c, (uint16_t)angle, tick);
}
static void turn(struct rotation_counter *c, int start, int direction)
{
	for (int n = 1; n <= 36; n++) {
		int angle = (start + direction * n * 160) % FIDGET_TURN_Q4;
		if (angle < 0) { angle += FIDGET_TURN_Q4; }
		at(c, angle);
	}
}
int main(void)
{
	struct rotation_counter c = {0};
	assert(at(&c, 0) == ROTATION_REBASED);
	turn(&c, 0, 1);
	assert(c.forward == 1 && c.reverse == 0 && rotation_total(&c) == 1);
	turn(&c, 0, -1);
	assert(c.forward == 1 && c.reverse == 1 && rotation_total(&c) == 2);
	rotation_reset(&c); at(&c, 2871);
	turn(&c, 2871, 1); turn(&c, 2871, -1);
	assert(rotation_total(&c) == 2 && c.remainder_q4 == 0);
	rotation_reset(&c); at(&c, 0);
	at(&c, 1440); at(&c, 2880); at(&c, 1440); at(&c, 0);
	assert(rotation_total(&c) == 0 && c.remainder_q4 == 0);
	at(&c, 1440); at(&c, 2880); at(&c, 4320); at(&c, 5760);
	assert(rotation_total(&c) == 1);
	rotation_reset(&c); at(&c, 0);
	for (int i = 0; i < 100; i++) { at(&c, i % 2 ? 5759 : 1); }
	assert(rotation_total(&c) == 0 && c.remainder_q4 == 0);
	for (int i = 1; i < 16; i++) { assert(at(&c, i) == ROTATION_STILL); }
	assert(at(&c, 16) == ROTATION_MOVED && c.remainder_q4 == 16);
	rotation_invalidate(&c);
	assert(!c.tracking && !c.remainder_q4);
	at(&c, 200); at(&c, 300); tick += 100;
	assert(at(&c, 400) == ROTATION_REBASED && !c.remainder_q4);
	assert(at(&c, 6000) == ROTATION_REBASED && !c.tracking);
	at(&c, 0);
	assert(at(&c, 2880) == ROTATION_REBASED && !c.remainder_q4);
	c.sample_ms = UINT32_MAX - 5; c.reference_q4 = 0; c.tracking = true;
	assert(rotation_update(&c, 160, 5) == ROTATION_MOVED);
	rotation_reset(&c); at(&c, 0); c.forward = UINT32_MAX - 1;
	turn(&c, 0, 1); turn(&c, 0, 1);
	assert(c.forward == UINT32_MAX);
	c.reverse = 1; assert(rotation_total(&c) == UINT32_MAX);
	uint32_t before = c.forward;
	rotation_invalidate(&c); at(&c, 1000);
	assert(c.forward == before && c.reverse == 1);
	rotation_reset(&c);
	assert(!c.forward && !c.reverse && !c.tracking);

	uint8_t frame[11] = {0x05,0x5a, 0,0, 0,0, 1, 0x10,0xe0, 5,0};
	struct hall_sample sample;
	assert(hall_decode(frame, &sample) == HALL_VALID && sample.angle_q4 == 4320);
	frame[7] = 0x16; frame[8] = 0x80;
	assert(hall_decode(frame, &sample) == HALL_VALID && sample.angle_q4 == 0);
	frame[8] = 0x81; assert(hall_decode(frame, &sample) == HALL_ANGLE);
	frame[7] = 0; frame[8] = 0;
	frame[6] = 0x11; assert(hall_decode(frame, &sample) == HALL_RESET);
	frame[6] = 0x03; assert(hall_decode(frame, &sample) == HALL_DIAGNOSTIC);
	frame[6] = 0; assert(hall_decode(frame, &sample) == HALL_NOT_READY);
	frame[6] = 1; frame[10] = 2;
	assert(hall_decode(frame, &sample) == HALL_DIAGNOSTIC);
	frame[10] = 0; frame[9] = 0;
	assert(hall_decode(frame, &sample) == HALL_FIELD);
	frame[9] = 5; frame[0] = 0x7d; frame[1] = 0;
	assert(hall_decode(frame, &sample) == HALL_FIELD);
	frame[0] = 0x83; assert(hall_decode(frame, &sample) == HALL_FIELD);
	frame[0] = 0; assert(hall_decode(frame, &sample) == HALL_FIELD);
	frame[0] = 0x05; frame[1] = 0x5a;
	assert(hall_decode(frame, &sample) == HALL_VALID);
	puts("PASS: full turns both directions, arbitrary phase, cancellation, wrap/noise, slow motion, gaps, jumps, reset, overflow, sensor byte order/POR/diagnostic/field/angle validation");
	return 0;
}
