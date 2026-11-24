#ifndef FIDGET_BATTERY_ADC_H
#define FIDGET_BATTERY_ADC_H
#include <stdint.h>
int battery_adc_init(void);
int battery_adc_read_mv(int32_t *millivolts);
#endif
