#include "tmag3001_frame.h"
#include "rotation_counter.h"
static int32_t signed_word(const uint8_t *p)
{
	uint32_t value = ((uint32_t)p[0] << 8) | p[1];
	return value & 0x8000U ? (int32_t)value - 65536 : (int32_t)value;
}
enum hall_result hall_decode(const uint8_t f[TMAG3001_FRAME_BYTES], struct hall_sample *out)
{
	/* One atomic burst: X/Y/Z (12h..17h), status18h, angle19h..1Ah, magnitude1Bh, diag1Ch. */
	if (f[6] & 0x10U) { return HALL_RESET; }
	if ((f[6] & 0x02U) || (f[10] & 0x06U)) { return HALL_DIAGNOSTIC; }
	if (!(f[6] & 0x01U)) { return HALL_NOT_READY; }
	int32_t x = signed_word(f), y = signed_word(f + 2);
	/* Initial sample-screening limits, to be qualified on the physical magnetic stack. */
	if (f[9] < 3 || x >= 32000 || x <= -32000 || y >= 32000 || y <= -32000 ||
	    x * x + y * y < 256 * 256) {
		return HALL_FIELD;
	}
	uint16_t angle = ((uint16_t)f[7] << 8) | f[8];
	if (angle > FIDGET_TURN_Q4) { return HALL_ANGLE; }
	out->angle_q4 = angle == FIDGET_TURN_Q4 ? 0 : angle;
	out->magnitude = f[9];
	return HALL_VALID;
}
