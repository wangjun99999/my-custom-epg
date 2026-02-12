import gzip
import shutil
import xml.etree.ElementTree as ET

CHANNEL_FILE = "/app/channels/epg_share01_channels.txt"
FULL_EPG = "/app/data/full.xml.gz"
OUT_XML = "/app/data/epg_share01.xml"
OUT_GZ = "/app/data/epg_share01.xml.gz"

with open(CHANNEL_FILE, "r", encoding="utf-8") as f:
    wanted = set()
    for line in f:
        line=line.strip()
        if line and not line.startswith("#"):
            wanted.add(line)

print("Loading full epg...")
with gzip.open(FULL_EPG, "rb") as f:
    tree = ET.parse(f)

root = tree.getroot()

channels = {}
programmes = []

for ch in root.findall("channel"):
    if ch.get("id") in wanted:
        channels[ch.get("id")] = ch

for p in root.findall("programme"):
    if p.get("channel") in wanted:
        programmes.append(p)

new_root = ET.Element("tv")

for ch in channels.values():
    new_root.append(ch)

for p in programmes:
    new_root.append(p)

ET.ElementTree(new_root).write(OUT_XML, encoding="utf-8", xml_declaration=True)

with open(OUT_XML,"rb") as f:
    with gzip.open(OUT_GZ,"wb") as g:
        g.write(f.read())

print("EPG generated")
