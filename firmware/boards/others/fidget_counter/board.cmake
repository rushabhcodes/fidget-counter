board_runner_args(jlink "--device=nRF52810_xxAA" "--speed=1000")
include(${ZEPHYR_BASE}/boards/common/jlink.board.cmake)
include(${ZEPHYR_BASE}/boards/common/openocd.board.cmake)
