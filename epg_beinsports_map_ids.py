import xml.etree.ElementTree as ET
import glob

# 读取所有 channel 映射
id_map = {}

for f in glob.glob("epg_beinsports/*.channels.xml"):
    tree = ET.parse(f)
    root = tree.getroot()

    for ch in root.findall("channel"):
        cid = ch.attrib["id"]
        name = ch.find("display-name").text.strip()
        id_map[cid] = name

print("Loaded", len(id_map), "beIN channels")

# 读取 EPG
tree = ET.parse("output/epg_beinsports.xml")
root = tree.getroot()

# 重写 channel id
for ch in root.findall("channel"):
    old = ch.attrib["id"]
    if old in id_map:
        ch.attrib["id"] = id_map[old]

# 重写 programme 的 channel
for p in root.findall("programme"):
    old = p.attrib["channel"]
    if old in id_map:
        p.attrib["channel"] = id_map[old]

tree.write("output/epg_beinsports_mapped.xml", encoding="utf-8", xml_declaration=True)

print("Saved: output/epg_beinsports_mapped.xml")
