import sys
import xml.etree.ElementTree as ET
import re

src, out = sys.argv[1], sys.argv[2]

tree = ET.parse(src)
root = tree.getroot()

# ========== display-name → real beIN IPTV id ==========
NAME_MAP = {
    # Main channels
    "beIN SPORTS 1": "beINSports1.qa@MENA",
    "beIN SPORTS 2": "beINSports2.qa@MENA",
    "beIN SPORTS 3": "beINSports3.qa@MENA",
    "beIN SPORTS 4": "beINSports4.qa@MENA",
    "beIN SPORTS 5": "beINSports5.qa@MENA",
    "beIN SPORTS 6": "beINSports6.qa@MENA",
    "beIN SPORTS 7": "beINSports7.qa@MENA",
    "beIN SPORTS 8": "beINSports8.qa@MENA",
    "beIN SPORTS 9": "beINSports9.qa@MENA",

    # MAX
    "beIN SPORTS MAX 1": "beINSportsMax1.qa@MENA",
    "beIN SPORTS MAX 2": "beINSportsMax2.qa@MENA",
    "beIN SPORTS MAX 3": "beINSportsMax3.qa@MENA",
    "beIN SPORTS MAX 4": "beINSportsMax4.qa@MENA",
    "beIN SPORTS MAX 5": "beINSportsMax5.qa@MENA",
    "beIN SPORTS MAX 6": "beINSportsMax6.qa@MENA",

    # XTRA
    "beIN SPORTS XTRA 1": "beINSportsXtra1.qa@SD",
    "beIN SPORTS XTRA 2": "beINSportsXtra2.qa@SD",
    "beIN SPORTS XTRA 3": "beINSportsXtra3.qa@SD",
    "beIN SPORTS XTRA 4": "beINSportsXtra4.qa@SD",
    "beIN SPORTS XTRA 5": "beINSportsXtra5.qa@SD",
    "beIN SPORTS XTRA 6": "beINSportsXtra6.qa@SD",
    "beIN SPORTS XTRA 7": "beINSportsXtra7.qa@SD",
    "beIN SPORTS XTRA 8": "beINSportsXtra8.qa@SD",
    "beIN SPORTS XTRA 9": "beINSportsXtra9.qa@SD",

    # AFC
    "beIN SPORTS 1 AFC": "beINSportsAFC1.qa@SD",
    "beIN SPORTS 2 AFC": "beINSportsAFC2.qa@SD",
    "beIN SPORTS 3 AFC": "beINSportsAFC3.qa@SD",
    "beIN SPORTS 4 AFC": "beINSports4AFC.qa@SD",
    "beIN SPORTS 5 AFC": "beINSports5AFC.qa@SD",
    "beIN SPORTS 6 AFC": "beINSports6AFC.qa@SD",

    # Others
    "beIN SPORTS NBA": "beINSportsNBA.qa@SD",
    "beIN SPORTS NEWS": "beINSportsNews.qa@SD",

    # French
    "beIN SPORTS FR 1": "beINSportsFR1.qa@SD",
    "beIN SPORTS FR 2": "beINSportsFR2.qa@SD",
}

# Build UUID → real id map
uuid_map = {}

for ch in root.findall("channel"):
    name = ch.findtext("display-name")
    if name in NAME_MAP:
        uuid_map[ch.get("id")] = NAME_MAP[name]
        ch.set("id", NAME_MAP[name])

# Rewrite programme channel ids
for p in root.findall("programme"):
    cid = p.get("channel")
    if cid in uuid_map:
        p.set("channel", uuid_map[cid])

tree.write(out, encoding="utf-8", xml_declaration=True)
print("Mapped →", out)
