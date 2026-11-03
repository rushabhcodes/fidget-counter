#ifndef FIDGET_TMAG3001_FRAME_H
#define FIDGET_TMAG3001_FRAME_H
#include <stdint.h>
#define TMAG3001_ADDRESS 0x34
#define TMAG3001_FRAME_BYTES 11
struct hall_sample { uint16_t angle_q4; uint8_t magnitude; };
enum hall_result { HALL_VALID, HALL_NOT_READY, HALL_RESET, HALL_DIAGNOSTIC, HALL_FIELD, HALL_ANGLE };
enum hall_result hall_decode(const uint8_t frame[TMAG3001_FRAME_BYTES], struct hall_sample *sample);
#endif
