#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
set -eu
root=$(git rev-parse --show-toplevel)
exec python3 "$root/tools/gate.py"
