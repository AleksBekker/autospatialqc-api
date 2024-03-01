#!/usr/bin/env bash

source .env.secret

curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "abekker@bidmc.harvard.edu", "password": "'"$API_PASSWORD"'"}' -s \
  | jq -r ".access_token"
