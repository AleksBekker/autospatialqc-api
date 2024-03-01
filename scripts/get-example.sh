#!/usr/bin/env sh

TOKEN=$(scripts/login.sh)
curl "http://localhost:5000/sample?assay=cosmx&tissue=LMet2" \
  -H "Authorization: Bearer $TOKEN"
