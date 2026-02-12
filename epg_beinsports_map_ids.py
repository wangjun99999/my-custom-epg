import xml.etree.ElementTree as ET
import glob

print("🔗 Loading beIN channel maps...")

id_map = {}

# 读取所有地区 channels.xml
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

# 读取合并后的原始 EPG
tree = ET.parse("output/epg_beinsports_raw.xml")
root = tree.getroot()

mapped = 0

# 替换 EPG 里的 channel id
for ch in root.findall("channel"):
    old = ch.attrib.get("id")
    if old in id_map:
        ch.attrib["id"] = id_map[old]
        mapped += 1

# 同步 programme 的 channel
for p in root.findall("programme"):
    old = p.attrib.get("channel")
    if old in id_map:
        p.attrib["channel"] = id_map[old]

print(f"Mapped channels: {mapped}")

tree.write("output/epg_beinsports_mapped.xml", encoding="utf-8", xml_declaration=True)
print("Saved: output/epg_beinsports_mapped.xml")
