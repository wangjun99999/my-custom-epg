import gzip
import shutil
import xml.etree.ElementTree as ET
import urllib.request
import os

EPG_URL = "https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz"
CHANNEL_LIST = "epg_share01_channels.txt"
OUTPUT_XML = "output/epg_share01.xml"
OUTPUT_GZ = "output/epg_share01.xml.gz"

os.makedirs("output", exist_ok=True)

print("Downloading epgshare01...")
urllib.request.urlretrieve(EPG_URL, "epg_share01_full.xml.gz")

print("Extracting...")
with gzip.open("epg_share01_full.xml.gz", "rb") as f_in:
    with open("epg_share01_full.xml", "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

print("Loading channel list...")
with open(CHANNEL_LIST, "r", encoding="utf-8") as f:
    wanted = set()
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            wanted.add(line)

print("Parsing XML...")
tree = ET.parse("epg_share01_full.xml")
root = tree.getroot()

channels = {}
for ch in root.findall("channel"):
    cid = ch.get("id")
    if cid in wanted:
        channels[cid] = ch

programmes = []
for p in root.findall("programme"):
    if p.get("channel") in wanted:
        programmes.append(p)

print(f"Kept {len(channels)} channels and {len(programmes)} programmes")

new_root = ET.Element("tv")

for ch in channels.values():
    new_root.append(ch)

for p in programmes:
    new_root.append(p)

new_tree = ET.ElementTree(new_root)
new_tree.write(OUTPUT_XML, encoding="utf-8", xml_declaration=True)

print("Compressing...")
with open(OUTPUT_XML, "rb") as f_in:
    with gzip.open(OUTPUT_GZ, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

print("Done!")
