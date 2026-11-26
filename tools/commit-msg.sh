#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
set -eu
LC_ALL=C awk '
  NR != 1 || length($0) > 50 || $0 !~ /^[a-z0-9][a-z0-9 ._-]*$/ || $0 ~ /[. ]$/ {bad=1}
  END {if (NR != 1 || bad) {print "expected one lowercase subject of at most 50 characters"; exit 1}}
' "$1"
