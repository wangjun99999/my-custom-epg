import xml.etree.ElementTree as ET
import glob
from collections import defaultdict

print("🔗 Loading beIN channel maps...")

name_to_xmltv = {}

for fn in glob.glob("epg_beinsports/*.channels.xml"):
    print(" -", fn)
    tree = ET.parse(fn)
    root = tree.getroot()

    for ch in root.findall(".//channel"):
        xmltv = ch.attrib.get("xmltv_id")
        name = ch.findtext("display-name")

        if not xmltv or not name:
            continue

        key = name.strip().lower()
        name_to_xmltv[key] = xmltv

print("Loaded", len(name_to_xmltv), "channel names")

# --- 读取 EPG ---
epg = ET.parse("output/epg_beinsports.xml")
root = epg.getroot()

# 建立 UUID → display-name 映射
uuid_to_name = {}

for p in root.findall("programme"):
    uuid = p.attrib.get("channel")
    disp = p.findtext("display-name")

    if uuid and disp:
        uuid_to_name[uuid] = disp.strip().lower()

# 重建 channel 列表
new_channels = {}
mapped = 0

for uuid, name in uuid_to_name.items():
    if name in name_to_xmltv:
        xmltv = name_to_xmltv[name]
        new_channels[xmltv] = name
        mapped += 1

print("Mapped channels:", mapped)

# 构建新 EPG
new_root = ET.Element("tv")

# 写 channels
for xmltv, name in new_channels.items():
    ch = ET.SubElement(new_root, "channel", id=xmltv)
    ET.SubElement(ch, "display-name").text = name

# 写 programmes
for p in root.findall("programme"):
    uuid = p.attrib.get("channel")
    name = uuid_to_name.get(uuid)

    if not name:
        continue

    xmltv = name_to_xmltv.get(name)
    if not xmltv:
        continue

    p.attrib["channel"] = xmltv
    new_root.append(p)

ET.ElementTree(new_root).write("output/epg_beinsports_mapped.xml", encoding="utf-8", xml_declaration=True)
print("Saved: output/epg_beinsports_mapped.xml")
