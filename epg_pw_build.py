import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import os

EPG_URL = "https://epg.pw/xmltv/epg.xml"

wanted = []

# 读取 epg_pw_channels.txt
with open("epg_pw_channels.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(",", 2)
        if len(parts) == 3:
            epg_id = parts[0].strip()
            real_name = parts[1].strip()
            note = parts[2].strip()   # 仅备注，不进入 XML
            wanted.append((epg_id, real_name))

print("Loading epg.pw...")
xml = requests.get(EPG_URL, timeout=60).content
root = ET.fromstring(xml)

out = ET.Element("tv")

# 建立 epg.pw 索引
epg_by_id = {}
epg_by_name = {}

for ch in root.findall("channel"):
    cid = ch.attrib["id"]
    names = [d.text.strip() for d in ch.findall("display-name") if d.text]
    epg_by_id[cid] = names
    for n in names:
        epg_by_name[n.lower()] = cid

# 匹配
valid = {}   # cid -> real_name

for epg_id, real_name in wanted:
    if epg_id in epg_by_id:
        valid[epg_id] = real_name
    elif real_name.lower() in epg_by_name:
        valid[epg_by_name[real_name.lower()]] = real_name

print("Matched channels:", len(valid))

# 输出 channel（只输出 epg.pw 的真实名）
for cid, real_name in valid.items():
    ch = ET.SubElement(out, "channel", id=cid)
    ET.SubElement(ch, "display-name").text = real_name

# UTC → 北京时间
def bj(t):
    # t = "20260210003500 +0000"
    base = t[:14]
    dt = datetime.strptime(base, "%Y%m%d%H%M%S")
    dt += timedelta(hours=8)
    return dt.strftime("%Y%m%d%H%M%S") + " +0800"

# 输出节目（保持原始时区）
for p in root.findall("programme"):
    cid = p.attrib.get("channel")
    if cid in valid:
        new = ET.SubElement(out, "programme")
        new.attrib["channel"] = cid
        new.attrib["start"] = bj(p.attrib["start"])
        new.attrib["stop"] = bj(p.attrib["stop"])

        for c in p:
            new.append(c)

# 写文件
os.makedirs("output", exist_ok=True)
ET.ElementTree(out).write("output/epg_pw.xml", encoding="utf-8", xml_declaration=True)

import gzip
import shutil

with open("output/epg_pw.xml", "rb") as f_in:
    with gzip.open("output/epg_pw.xml.gz", "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

print("Done.")
print("output/epg_pw.xml")
print("output/epg_pw.xml.gz")
