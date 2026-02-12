import xml.etree.ElementTree as ET
import glob
import re

print("🔗 Loading beIN channel maps...")

id_map = {}

# 读取所有 channels.xml
for f in glob.glob("epg_beinsports/*.channels.xml"):
    print(" -", f)
    tree = ET.parse(f)
    root = tree.getroot()

    for ch in root.findall("channel"):
        site_id = ch.attrib.get("site_id")
        xmltv_id = ch.attrib.get("xmltv_id")

        if site_id and xmltv_id:
            id_map[site_id] = xmltv_id

print(f"Loaded {len(id_map)} channel IDs")

# 读取 EPG
tree = ET.parse("output/epg_beinsports_raw.xml")
root = tree.getroot()

mapped = 0

def normalize(epg_id):
    # 去掉 beinsports.com / 区域前缀
    # beinsports.com_mena-en_UUID → UUID
    return epg_id.split("_")[-1]

# 替换 channel
for ch in root.findall("channel"):
    old = ch.attrib.get("id")
    if not old:
        continue

    key = normalize(old)

    if key in id_map:
        ch.attrib["id"] = id_map[key]
        mapped += 1

# 替换 programme
for p in root.findall("programme"):
    old = p.attrib.get("channel")
    if not old:
        continue

    key = normalize(old)

    if key in id_map:
        p.attrib["channel"] = id_map[key]

print(f"Mapped channels: {mapped}")

tree.write("output/epg_beinsports_mapped.xml", encoding="utf-8", xml_declaration=True)
print("Saved: output/epg_beinsports_mapped.xml")
