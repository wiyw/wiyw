#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
PATH="$(pwd)/scripts/demo-bin:$PATH" vhs scripts/demo.tape
