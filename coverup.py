import logging
import logging.handlers
import os

import requests
import random
import re
import unicodedata

import time
import math
import sys

import json
import datetime

from typing import List, Dict, Tuple
from urllib.parse import quote

try:
    GYM_PASSWORD = "12341234"
    GYM_USERNAME = "botgym3"
except KeyError:
    GYM_PASSWORD = ""
    GYM_USERNAME = ""



# ------------------------------
# Configuration / Constants
# ------------------------------

max_weights = [ 106, 109, 112, 115, 118, 122, 126, 130, 135, 141, 147, 153, 160, 167, 175, 200, 1000 ]
build_str = [ "very light", "light", "a little light", "normal", "a little heavy", "heavy", "very heavy" ]
divis_str = [ "Straw", "Junior-Fly", "Fly", "Super-Fly", "Bantam", "Super-Bantam", "Feather", "Super-Feather", "Light", "Super-Light", "Welter", "Super-Welter", "Middle", "Super-Middle", "Light-Heavy", "Cruiser", "Heavy" ]
style_str = [ "inside", "clinch", "feint", "counter", "ring", "ropes", "outside", "allout" ]
cut_str = [ "low", "normal", "high" ]

stats_str = [ "strength", "knockout punch", "speed", "agility", "chin", "conditioning" ]
train_str = [ "weights+(STR)", "heavy+bag+(KP)", "speed+bag+(SPD)", "jump+rope+(AGL)", "sparring+(CHN)", "road+work+(CND)" ]

DIVISIONS = [
    "Straw", "Junior-Fly", "Fly", "Super-Fly", "Bantam", "Super-Bantam", "Feather", "Super-Feather",
    "Light", "Super-Light", "Welter", "Super-Welter", "Middle", "Super-Middle", "Light-Heavy", "Cruiser", "Heavy"
]

fighter_builds = [
    { "STRENGTH": 0.45, "SPEED": 0.33, "AGILITY": 0.22, "CHIN": 19, "HEIGHT": 10, "COUNT": 3 }, # albino
    { "STRENGTH": 0.55, "SPEED": 0.30, "AGILITY": 0.15, "CHIN": 22, "HEIGHT":  7, "COUNT": 1 }, # zam
    { "STRENGTH": 0.46, "SPEED": 0.25, "AGILITY": 0.29, "CHIN": 18, "HEIGHT": 12, "COUNT": 2 }, # agl
    { "STRENGTH": 0.40, "SPEED": 0.29, "AGILITY": 0.31, "CHIN": 17, "HEIGHT": 13, "COUNT": 0 }, # bal
]


# ------------------------------
# Small helpers
# --------

def _parse_etc_params(etc: str) -> Dict[str, str]:
    """
    Convert a PHP-style query string like:
        "+team_id=123&foo=bar&+x=y"
    into a clean parameter dict.
    """
    params = {}
    if not etc:
        return params

    # Remove ONLY leading "+" from keys (like PHP logic)
    for part in etc.split("&"):
        if "=" not in part:
            continue

        key, value = part.split("=", 1)
        key = key.lstrip("+").strip()
        value = value.strip()

        if key:
            params[key] = value

    return params

def write_msg(
    command: str = "",
    etc: str = "",
    script: str = "query.fcgi",
):
    url = f"https://webl.vivi.com/cgi-bin/{script}"

    data = {
        **_parse_etc_params(etc),
        "username": GYM_USERNAME,
        "password": GYM_PASSWORD,
        "block_ad": "1",
        "command": command,
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36"
        ),
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    for attempt in range(7):
        time.sleep(2.75 + 15 * attempt)
        try:
            print(command, etc)
            resp = requests.post(url, data=data, headers=headers, timeout=10)
            resp.raise_for_status()
            if "eeeeee" not in resp.text:
                raise requests.RequestException("Invalid WeBL response content")
            return resp.text
        except requests.RequestException as e:
            if attempt == 6:
                print(f"[write_msg] FAILED after 7 attempts:  script={script}, command={command}, etc='{etc}'\n{e}", file=sys.stderr)
    
    return ""



# ------------------------------
# Main
# ------------------------------

if __name__ == "__main__":
    for word in write_msg("eko_retired_fighters").split("Activate</A>"):
        if "regional_champion" not in word and "challenger.gif" not in word and "champion.gif" not in word:
            for team_id in re.findall(r"team_id=([0-9]+)", word):
                write_msg("eko_activate", f"team_id={team_id}")
                break