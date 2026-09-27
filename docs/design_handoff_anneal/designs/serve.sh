#!/usr/bin/env bash
# Serves the design files over http (the .dc.html mockups fetch their runtime, so file:// won't work).
cd "$(dirname "$0")" && echo "open http://localhost:4173/anneal-screens.html" && python3 -m http.server 4173
