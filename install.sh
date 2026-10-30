#!/bin/sh
set -eu
cd "$(dirname "$0")"

if [ -n "${PREFIX:-}" ] && [ -d "$PREFIX/bin" ]; then
  destination="$PREFIX/bin"
else
  destination="$HOME/.local/bin"
fi

mkdir -p "$destination"
cp maze "$destination/maze"
chmod 755 "$destination/maze"
printf 'Installed: %s/maze\n' "$destination"
if ! command -v maze >/dev/null 2>&1; then
  printf 'Add %s to PATH if it is not already there.\n' "$destination"
fi
