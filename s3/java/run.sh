#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")"

./gradlew run --args="$*"
