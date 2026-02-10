import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import os

EPG_URL = "https://epg.pw/xmltv/epg.xml"

wanted = []

with open("epg_pw_channels.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(",", 2)
        if len(parts) == 3:
            wanted.append((parts[0].strip(), parts[1].strip().lower(), parts[2].strip()))

print("Loading epg.pw...")
xml = requests.get(EPG_URL).content
root = ET.fromstring(xml)

out = ET.Element("tv")
valid = {}

# 建 epg.pw 索引
epg_by_id = {}
epg_by_name = {}

for ch in root.findall("channel"):
    cid = ch.attrib["id"]
    names = [d.text.strip() for d in ch.findall("display-name")]
    epg_by_id[cid] = names
    for n in names:
        epg_by_name[n.lower()] = cid

# 进行匹配
for src_id, src_name, note in wanted:
    if src_id in epg_by_id:
        valid[src_id] = note
    elif src_name in epg_by_name:
        valid[epg_by_name[src_name]] = note

print("Matched channels:", len(valid))

# 输出频道
for cid, note in valid.items():
    ch = ET.SubElement(out, "channel", id=cid)
    for n in epg_by_id[cid]:
        ET.SubElement(ch, "display-name").text = n
    ET.SubElement(ch, "display-name").text = note

def bj(t):
    dt = datetime.strptime(t[:14], "%Y%m%d%H%M%S")
    dt += timedelta(hours=8)
    return dt.strftime("%Y%m%d%H%M%S") + " +0800"

# 输出节目
for p in root.findall("programme"):
    if p.attrib["channel"] in valid:
        new = ET.SubElement(out, "programme")
        new.attrib["channel"] = p.attrib["channel"]
        new.attrib["start"] = bj(p.attrib["start"])
        new.attrib["stop"] = bj(p.attrib["stop"])
        for c in p:
            new.append(c)

os.makedirs("output", exist_ok=True)
ET.ElementTree(out).write("output/epg_pw.xml", encoding="utf-8", xml_declaration=True)

print("Done.")
