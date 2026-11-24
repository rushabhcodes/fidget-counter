#include <errno.h>
#include <limits.h>
#include <string.h>
#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/drivers/flash.h>
#include <zephyr/fs/nvs.h>
#include <zephyr/storage/flash_map.h>
#include <zephyr/sys/atomic.h>
#include <zephyr/sys/byteorder.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/uuid.h>
#include "rotation_counter.h"
#include "tmag3001_frame.h"
#include "battery_state.h"
#include "battery_adc.h"

/* Custom RevC board only. No LED, UART, cap button, bootloader or SoftDevice. */
#define SERVICE_UUID BT_UUID_128_ENCODE(0x76b8a000, 0x5aa4, 0x4c10, 0xb5df, 0x0da684303f21)
#define STATE_UUID BT_UUID_128_ENCODE(0x76b8a001, 0x5aa4, 0x4c10, 0xb5df, 0x0da684303f21)
#define CONTROL_UUID BT_UUID_128_ENCODE(0x76b8a002, 0x5aa4, 0x4c10, 0xb5df, 0x0da684303f21)
#define BATTERY_UUID BT_UUID_128_ENCODE(0x76b8a003, 0x5aa4, 0x4c10, 0xb5df, 0x0da684303f21)
#define SENSOR_FAULT 1U
#define STORAGE_FAULT 2U
#define UNSAVED 4U
#define SAMPLE_GAP 8U
#define SATURATED 16U
#define LOW_BATTERY 32U
#define BATTERY_FAULT 64U
#define NOTIFY_BATTERY_LEVEL 1U
#define NOTIFY_BATTERY_STATUS 2U
#define NOTIFY_BATTERY_ALL (NOTIFY_BATTERY_LEVEL | NOTIFY_BATTERY_STATUS)

static const struct device *const bus = DEVICE_DT_GET(DT_NODELABEL(i2c0));
static const struct device *const gpio = DEVICE_DT_GET(DT_NODELABEL(gpio0));
static struct rotation_counter counter;
static uint8_t flags = SENSOR_FAULT | BATTERY_FAULT;
static struct battery_state battery;
static bool battery_ready;
static atomic_t battery_notifications;
static uint16_t current_angle;
static uint32_t sequence;
static K_MUTEX_DEFINE(state_lock);
static atomic_t control_request;
static atomic_t connected;
static atomic_t advertising_requested = ATOMIC_INIT(1);
static struct nvs_fs storage;
static bool storage_ready;
static bool sensor_ready;

static void encode_state(uint8_t data[20])
{
	k_mutex_lock(&state_lock, K_FOREVER);
	data[0] = 1;
	data[1] = flags;
	if (counter.forward == UINT32_MAX || counter.reverse == UINT32_MAX ||
	    UINT32_MAX - counter.forward < counter.reverse) { data[1] |= SATURATED; }
	sys_put_le16(current_angle, data + 2);
	sys_put_le32(counter.forward, data + 4);
	sys_put_le32(counter.reverse, data + 8);
	sys_put_le32(rotation_total(&counter), data + 12);
	sys_put_le32(sequence, data + 16);
	k_mutex_unlock(&state_lock);
}

static ssize_t read_state(struct bt_conn *conn, const struct bt_gatt_attr *attr,
			  void *buf, uint16_t len, uint16_t offset)
{
	uint8_t data[20];
	encode_state(data);
	return bt_gatt_attr_read(conn, attr, buf, len, offset, data, sizeof(data));
}
static ssize_t write_control(struct bt_conn *conn, const struct bt_gatt_attr *attr,
			     const void *buf, uint16_t len, uint16_t offset, uint8_t write_flags)
{
	ARG_UNUSED(conn); ARG_UNUSED(attr);
	if (offset || (write_flags & BT_GATT_WRITE_FLAG_PREPARE)) {
		return BT_GATT_ERR(BT_ATT_ERR_INVALID_OFFSET);
	}
	if (len != 4) { return BT_GATT_ERR(BT_ATT_ERR_INVALID_ATTRIBUTE_LEN); }
	int request = !memcmp(buf, "ZERO", 4) ? 1 : !memcmp(buf, "SAVE", 4) ? 2 : 0;
	if (!request) { return BT_GATT_ERR(BT_ATT_ERR_VALUE_NOT_ALLOWED); }
	if (!atomic_cas(&control_request, 0, request)) {
		return BT_GATT_ERR(BT_ATT_ERR_UNLIKELY);
	}
	return len;
}
static void ccc_changed(const struct bt_gatt_attr *attr, uint16_t value)
{
	ARG_UNUSED(attr); ARG_UNUSED(value);
}
static void battery_ccc_changed(const struct bt_gatt_attr *attr, uint16_t value)
{
	ARG_UNUSED(attr);
	if (value & BT_GATT_CCC_NOTIFY) {
		atomic_or(&battery_notifications, NOTIFY_BATTERY_ALL);
	}
}
static ssize_t read_battery(struct bt_conn *conn, const struct bt_gatt_attr *attr,
			   void *buf, uint16_t len, uint16_t offset)
{
	uint8_t data[BATTERY_STATUS_SIZE];
	k_mutex_lock(&state_lock, K_FOREVER);
	battery_encode(&battery, data);
	k_mutex_unlock(&state_lock);
	return bt_gatt_attr_read(conn, attr, buf, len, offset, data, sizeof(data));
}
static ssize_t read_battery_level(struct bt_conn *conn, const struct bt_gatt_attr *attr,
				 void *buf, uint16_t len, uint16_t offset)
{
	k_mutex_lock(&state_lock, K_FOREVER);
	bool valid = battery.valid;
	uint8_t level = battery.percent;
	k_mutex_unlock(&state_lock);
	/* Standard Battery Level has no reserved value for an unknown reading. */
	if (!valid) { return BT_GATT_ERR(BT_ATT_ERR_UNLIKELY); }
	return bt_gatt_attr_read(conn, attr, buf, len, offset, &level, sizeof(level));
}
BT_GATT_SERVICE_DEFINE(fidget_service,
	BT_GATT_PRIMARY_SERVICE(BT_UUID_DECLARE_128(SERVICE_UUID)),
	BT_GATT_CHARACTERISTIC(BT_UUID_DECLARE_128(STATE_UUID),
		BT_GATT_CHRC_READ | BT_GATT_CHRC_NOTIFY, BT_GATT_PERM_READ,
		read_state, NULL, NULL),
	BT_GATT_CCC(ccc_changed, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE),
	BT_GATT_CHARACTERISTIC(BT_UUID_DECLARE_128(CONTROL_UUID),
		BT_GATT_CHRC_WRITE, BT_GATT_PERM_WRITE, NULL, write_control, NULL),
	BT_GATT_CHARACTERISTIC(BT_UUID_DECLARE_128(BATTERY_UUID),
		BT_GATT_CHRC_READ | BT_GATT_CHRC_NOTIFY, BT_GATT_PERM_READ,
		read_battery, NULL, NULL),
	BT_GATT_CCC(battery_ccc_changed, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE)
);
BT_GATT_SERVICE_DEFINE(battery_service,
	BT_GATT_PRIMARY_SERVICE(BT_UUID_BAS),
	BT_GATT_CHARACTERISTIC(BT_UUID_BAS_BATTERY_LEVEL,
		BT_GATT_CHRC_READ | BT_GATT_CHRC_NOTIFY, BT_GATT_PERM_READ,
		read_battery_level, NULL, NULL),
	BT_GATT_CCC(battery_ccc_changed, BT_GATT_PERM_READ | BT_GATT_PERM_WRITE)
);

static void refresh_battery(void)
{
	int32_t mv = -1;
	if (!battery_ready) { battery_ready = battery_adc_init() == 0; }
	if (battery_ready && battery_adc_read_mv(&mv)) {
		mv = -1;
		battery_ready = false;
	}
	k_mutex_lock(&state_lock, K_FOREVER);
	bool was_valid = battery.valid;
	uint8_t previous_level = battery.percent;
	uint8_t previous_flags = flags;
	battery_update(&battery, mv);
	flags &= ~(LOW_BATTERY | BATTERY_FAULT);
	if (battery.low) { flags |= LOW_BATTERY; }
	if (!battery.valid) { flags |= BATTERY_FAULT; }
	if (flags != previous_flags) { sequence++; }
	if (battery.valid && (!was_valid || battery.percent != previous_level)) {
		atomic_or(&battery_notifications, NOTIFY_BATTERY_LEVEL);
	}
	k_mutex_unlock(&state_lock);
	atomic_or(&battery_notifications, NOTIFY_BATTERY_STATUS);
}

static void battery_notify(struct k_work *work)
{
	ARG_UNUSED(work);
	if (!atomic_get(&connected)) { return; }
	atomic_val_t requested = atomic_set(&battery_notifications, 0);
	if (!requested) { return; }
	uint8_t data[BATTERY_STATUS_SIZE];
	k_mutex_lock(&state_lock, K_FOREVER);
	battery_encode(&battery, data);
	k_mutex_unlock(&state_lock);
	int err;
	if ((requested & NOTIFY_BATTERY_LEVEL) && (data[1] & 1U)) {
		err = bt_gatt_notify(NULL, &battery_service.attrs[2], data + 2, 1);
		if (err == -ENOMEM || err == -ENOBUFS || err == -EAGAIN) {
			atomic_or(&battery_notifications, NOTIFY_BATTERY_LEVEL);
		}
	}
	if (requested & NOTIFY_BATTERY_STATUS) {
		err = bt_gatt_notify(NULL, &fidget_service.attrs[7], data, sizeof(data));
		if (err == -ENOMEM || err == -ENOBUFS || err == -EAGAIN) {
			atomic_or(&battery_notifications, NOTIFY_BATTERY_STATUS);
		}
	}
}
/* System-workqueue notifications return on TX-buffer exhaustion instead of
 * waiting in the rotation sampling thread; the pending bits are retried. */
K_WORK_DEFINE(battery_notify_work, battery_notify);

static void on_connected(struct bt_conn *conn, uint8_t err)
{
	ARG_UNUSED(conn);
	if (err) { atomic_set(&advertising_requested, 1); }
	else {
		atomic_set(&connected, 1);
		atomic_or(&battery_notifications, NOTIFY_BATTERY_ALL);
	}
}
static void on_disconnected(struct bt_conn *conn, uint8_t reason)
{
	ARG_UNUSED(conn); ARG_UNUSED(reason);
	atomic_set(&connected, 0);
	atomic_set(&advertising_requested, 1);
}
BT_CONN_CB_DEFINE(connection_callbacks) = {
	.connected = on_connected, .disconnected = on_disconnected,
};
static const struct bt_data advertisement[] = {
	BT_DATA_BYTES(BT_DATA_FLAGS, BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR),
	BT_DATA_BYTES(BT_DATA_UUID128_ALL, SERVICE_UUID),
	BT_DATA_BYTES(BT_DATA_UUID16_ALL, 0x0f, 0x18),
};
static const struct bt_data scan_response[] = {
	BT_DATA(BT_DATA_NAME_COMPLETE, CONFIG_BT_DEVICE_NAME, sizeof(CONFIG_BT_DEVICE_NAME) - 1),
};

static int sensor_write(uint8_t reg, uint8_t value)
{
	return i2c_reg_write_byte(bus, TMAG3001_ADDRESS, reg, value);
}
static int sensor_init(void)
{
	uint8_t identity[3], check[4];
	int err = i2c_burst_read(bus, TMAG3001_ADDRESS, 0x0d, identity, sizeof(identity));
	if (err) { return err; }
	if ((identity[0] & 0x0c) != 0x08 || identity[1] != 0x49 || identity[2] != 0x54) {
		return -ENODEV;
	}
	/* TI SLYS053C: A2, 4x averaging, XY angle, wide XY range, 5ms W&S.
	 * Explicitly latch address0x34 before W&S: the ADDR pin is not sampled there.
	 * INT is unused in this polling pilot and P0.28 remains a high-impedance input.
	 */
	const uint8_t setup[][2] = {
		{0x01, 0x00}, {0x00, 0x08}, {0x02, 0x31}, {0x03, 0x06},
		{0x07, 0x00}, {0x08, 0x00}, {0x09, 0x00}, {0x0a, 0x00},
		{0x0b, 0x00}, {0x0c, 0x69}, {0x18, 0x10}, {0x01, 0x03},
	};
	for (size_t i = 0; i < ARRAY_SIZE(setup); i++) {
		err = sensor_write(setup[i][0], setup[i][1]);
		if (err) { return err; }
	}
	err = i2c_burst_read(bus, TMAG3001_ADDRESS, 0x00, check, sizeof(check));
	if (err) { return err; }
	/* Reads may return W&S to standby. Accept only those two operating modes. */
	if (check[0] != 0x08 || (check[1] != 0x00 && check[1] != 0x03) ||
	    check[2] != 0x31 || check[3] != 0x06) { return -EIO; }
	return sensor_write(0x01, 0x03);
}
static int sensor_read(struct hall_sample *sample)
{
	uint8_t frame[TMAG3001_FRAME_BYTES];
	int err = i2c_burst_read(bus, TMAG3001_ADDRESS, 0x12, frame, sizeof(frame));
	if (err) { return err; }
	/* Rearm after every read: W&S must be restored after an interrupt/read wake. */
	err = sensor_write(0x01, 0x03);
	if (err) { return err; }
	switch (hall_decode(frame, sample)) {
	case HALL_VALID: return 0;
	case HALL_NOT_READY: return -EAGAIN;
	default: return -EIO;
	}
}

static int storage_init(void)
{
	storage.flash_device = FIXED_PARTITION_DEVICE(storage_partition);
	if (!device_is_ready(storage.flash_device)) { return -ENODEV; }
	storage.offset = FIXED_PARTITION_OFFSET(storage_partition);
	struct flash_pages_info page;
	int err = flash_get_page_info_by_offs(storage.flash_device, storage.offset, &page);
	if (err) { return err; }
	storage.sector_size = page.size;
	storage.sector_count = FIXED_PARTITION_SIZE(storage_partition) / page.size;
	if (storage.sector_count < 2) { return -EINVAL; }
	err = nvs_mount(&storage);
	if (err) { return err; }
	uint8_t record[12];
	ssize_t bytes = nvs_read(&storage, 1, record, sizeof(record));
	if (bytes == -ENOENT) { return 0; }
	if (bytes != (ssize_t)sizeof(record) || memcmp(record, "FCR1", 4)) { return -EIO; }
	counter.forward = sys_get_le32(record + 4);
	counter.reverse = sys_get_le32(record + 8);
	return 0;
}
static void save_counts(void)
{
	if (!storage_ready) { return; }
	uint8_t record[12];
	memcpy(record, "FCR1", 4);
	/* Main thread owns count mutations; BLE callbacks only queue commands. */
	k_mutex_lock(&state_lock, K_FOREVER);
	sys_put_le32(counter.forward, record + 4);
	sys_put_le32(counter.reverse, record + 8);
	k_mutex_unlock(&state_lock);
	ssize_t result = nvs_write(&storage, 1, record, sizeof(record));
	k_mutex_lock(&state_lock, K_FOREVER);
	if (result < 0) { flags |= STORAGE_FAULT; }
	else { flags &= ~(UNSAVED | STORAGE_FAULT); }
	sequence++;
	k_mutex_unlock(&state_lock);
}

int main(void)
{
	if (!device_is_ready(bus) || !device_is_ready(gpio)) { return -ENODEV; }
	/* External10k pull-up exists. Do not drive the Hall INT line or unused P0.29. */
	int err = gpio_pin_configure(gpio, 28, GPIO_INPUT);
	if (err) { return err; }
	storage_ready = storage_init() == 0;
	if (!storage_ready) { flags |= STORAGE_FAULT; }
	refresh_battery();
	uint32_t last_battery_sample = k_uptime_get_32();
	err = bt_enable(NULL);
	if (err) { return err; }
	uint32_t last_advertise = (uint32_t)k_uptime_get_32() - 1000U;
	uint32_t last_sensor_retry = last_advertise;
	uint32_t last_valid = k_uptime_get_32();
	uint32_t last_motion = last_valid, last_save = last_valid, last_notify = last_valid;
	uint32_t last_battery_notify = last_valid;
	k_sleep(K_MSEC(5));
	for (;;) {
		uint32_t now = k_uptime_get_32();
		if (!atomic_get(&connected) && atomic_get(&advertising_requested) &&
		    (uint32_t)(now - last_advertise) >= 1000U) {
			last_advertise = now;
			err = bt_le_adv_start(BT_LE_ADV_PARAM(BT_LE_ADV_OPT_CONNECTABLE, 800, 1600, NULL),
					     advertisement, ARRAY_SIZE(advertisement),
					     scan_response, ARRAY_SIZE(scan_response));
			if (!err || err == -EALREADY) { atomic_set(&advertising_requested, 0); }
		}
		if (!sensor_ready && (uint32_t)(now - last_sensor_retry) >= 1000U) {
			last_sensor_retry = now;
			sensor_ready = sensor_init() == 0;
			if (sensor_ready) { last_valid = now; }
		}
		struct hall_sample sample;
		err = sensor_ready ? sensor_read(&sample) : -ENODEV;
		k_mutex_lock(&state_lock, K_FOREVER);
		if (!err) {
			last_valid = now;
			current_angle = sample.angle_q4;
			flags &= ~SENSOR_FAULT;
			bool tracking = counter.tracking;
			enum rotation_result moved = rotation_update(&counter, sample.angle_q4, now);
			if (tracking && moved == ROTATION_REBASED) { flags |= SAMPLE_GAP; }
			if (moved == ROTATION_MOVED || moved == ROTATION_COUNTED) { last_motion = now; }
			if (moved == ROTATION_COUNTED) { flags |= UNSAVED; sequence++; }
		} else if (err != -EAGAIN || (uint32_t)(now - last_valid) > 100U) {
			flags |= SENSOR_FAULT;
			rotation_invalidate(&counter);
			sensor_ready = false;
		}
		int request = atomic_set(&control_request, 0);
		if (request == 1) {
			rotation_reset(&counter);
			flags = (flags & (SENSOR_FAULT | STORAGE_FAULT | LOW_BATTERY | BATTERY_FAULT)) | UNSAVED;
			sequence++;
		}
		bool dirty = flags & UNSAVED;
		k_mutex_unlock(&state_lock);
		if (dirty && (request || (uint32_t)(now - last_motion) >= 2000U ||
			      (uint32_t)(now - last_save) >= 60000U)) {
			/* A failed write is retried at most once per second. */
			if (request || (uint32_t)(now - last_save) >= 1000U) {
				save_counts(); last_save = now;
			}
		}
		if (atomic_get(&connected) && (uint32_t)(now - last_notify) >= 100U) {
			uint8_t data[20];
			encode_state(data);
			(void)bt_gatt_notify(NULL, &fidget_service.attrs[2], data, sizeof(data));
			last_notify = now;
		}
		if ((uint32_t)(now - last_battery_sample) >= BATTERY_SAMPLE_INTERVAL_MS) {
			refresh_battery();
			last_battery_sample = now;
		}
		if (atomic_get(&connected) && atomic_get(&battery_notifications) &&
		    (uint32_t)(now - last_battery_notify) >= 100U) {
			k_work_submit(&battery_notify_work);
			last_battery_notify = now;
		}
		k_sleep(K_MSEC(10));
	}
}
