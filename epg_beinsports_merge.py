import glob
import xml.etree.ElementTree as ET
from collections import defaultdict

print("🔗 Loading regional XML files...")

files = glob.glob("tmp/*.xml")
if not files:
    raise SystemExit("❌ No tmp/*.xml files found")

# 存储
channels = {}
programmes = defaultdict(dict)  # {channel_id: {(start, stop, title): programme}}

for file in files:
    print(" -", file)
    tree = ET.parse(file)
    root = tree.getroot()

    # channels
    for ch in root.findall("channel"):
        cid = ch.attrib["id"]
        if cid not in channels:
            channels[cid] = ch

    # programmes
    for p in root.findall("programme"):
        cid = p.attrib["channel"]
        key = (p.attrib["start"], p.attrib["stop"], p.findtext("title", ""))
        programmes[cid][key] = p   # 自动去重

# 生成新 XML
tv = ET.Element("tv")

# 写 channels
for ch in channels.values():
    tv.append(ch)

# 写 programmes（按时间排序）
for cid in sorted(programmes.keys()):
    plist = list(programmes[cid].values())
    plist.sort(key=lambda p: p.attrib["start"])
    for p in plist:
        tv.append(p)

# 输出
tree = ET.ElementTree(tv)
tree.write("output/epg_beinsports_raw.xml", encoding="utf-8", xml_declaration=True)

print("✅ Merged to output/epg_beinsports_raw.xml")
