import xml.etree.ElementTree as ET
import glob

id_map = {}

print("🔗 Loading beIN channel maps...")

for f in glob.glob("epg_beinsports/*.channels.xml"):
    print(" -", f)
    tree = ET.parse(f)
    root = tree.getroot()

    for ch in root.findall("channel"):
        cid = ch.attrib.get("id")
        name_node = ch.find("display-name")

        # 跳过不完整的 channel
        if not cid or name_node is None:
            continue

        name = name_node.text.strip()
        id_map[cid] = name

print("Loaded", len(id_map), "channels")

# 读取合并后的 EPG
tree = ET.parse("output/epg_beinsports.xml")
root = tree.getroot()

mapped = 0

# 重写 channel id
for ch in root.findall("channel"):
    old = ch.attrib.get("id")
    if old in id_map:
        ch.attrib["id"] = id_map[old]
        mapped += 1

# 重写 programme channel
for p in root.findall("programme"):
    old = p.attrib.get("channel")
    if old in id_map:
        p.attrib["channel"] = id_map[old]

tree.write("output/epg_beinsports_mapped.xml", encoding="utf-8", xml_declaration=True)

print("Mapped channels:", mapped)
print("Saved: output/epg_beinsports_mapped.xml")
