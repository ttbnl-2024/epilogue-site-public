#!/usr/bin/env bash

cd "$(dirname "$0")"

# Due to whitenoise, we need to dupe the static files
# Yes, could turn it off but I also turned my brain off.

WGET_SETTINGS=$(echo \
  --force-directories \
  --max-redirect=1 \
  --html-extension \
  --restrict-file-names=windows \
  --retry-on-http-error=500 \
  --tries=3 \
  --domains localhost \
  --no-parent \
  --no-check-certificate \
  --reject "*&quot;*" \
  )

rm -rf localhost+8000

wget --recursive ${WGET_SETTINGS} http://localhost:8000
