#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
FIDGET_TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$FIDGET_TEST_DIR"' EXIT HUP INT TERM
cc -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined -g \
  -Iinclude src/rotation_counter.c src/tmag3001_frame.c tests/test_logic.c \
  -o "$FIDGET_TEST_DIR/test_logic"
"$FIDGET_TEST_DIR/test_logic"
python3 -m py_compile tools/verify_build.py tools/flash.py tools/client.py
