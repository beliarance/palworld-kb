#!/bin/bash
# Fetch tier-list source pages for tier_lists.json (Palworld 1.0 KB project)
set -u
OUT="${1:-/private/tmp/claude-501/-Users-ivanzhilinskiy-Projects-Pal/b74f2727-1708-40db-bfca-173172863c58/scratchpad/pages}"
mkdir -p "$OUT"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

fetch() {
  url="$1"; name="$2"
  curl -sL -A "$UA" --max-time 40 -o "$OUT/$name" "$url"
  echo "$name $(wc -c < "$OUT/$name" | tr -d ' ')"
}

fetch "https://game8.co/games/Palworld/archives/440495" g8_mounts.html
fetch "https://game8.co/games/Palworld/archives/440516" g8_flying.html
fetch "https://game8.co/games/Palworld/archives/440547" g8_ground.html
fetch "https://game8.co/games/Palworld/archives/440432" g8_base.html
fetch "https://game8.co/games/Palworld/archives/440279" g8_combat.html
fetch "https://palworld.gg/tier-list/base-work" pgg_base.html
fetch "https://palworld.gg/tier-list/combat" pgg_combat.html
fetch "https://pindrop.gg/palworld/tier-list" pindrop.html
fetch "https://mobalytics.gg/news/guides/palworld-best-pals-1-0" mobalytics_10.html
fetch "https://palworld.wiki.gg/wiki/Fishing" wiki_fishing.html
