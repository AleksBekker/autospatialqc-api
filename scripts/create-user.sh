#!/usr/bin/env sh

TOKEN=$(scripts/login.sh)
curl "http://localhost:5000/create-user" -s \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "email": "alekso.bekker@gmail.com", "password": "some password", "first_name": "Al", "last_name": "Bek",
      "permissions": ["get_sample"]}'
