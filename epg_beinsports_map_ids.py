import xml.etree.ElementTree as ET
import glob

print("🔗 Loading beIN channel maps...")

id_map = {}

for fn in glob.glob("epg_beinsports/*.channels.xml"):
    print(" -", fn)
    tree = ET.parse(fn)
    root = tree.getroot()

    for ch in root.findall(".//channel"):
        xmltv = ch.attrib.get("xmltv_id")
        if not xmltv:
            continue

        # 统一成小写用于匹配
        key = xmltv.lower()

        # 频道名
        name = ch.findtext("display-name", default=xmltv)

        id_map[key] = name

print("Loaded", len(id_map), "channels")

# --- 读取你抓好的 beIN EPG ---
epg = ET.parse("output/epg_beinsports.xml")
root = epg.getroot()

mapped = 0

for ch in root.findall("channel"):
    cid = ch.attrib.get("id", "").lower()

    if cid in id_map:
        ch.attrib["id"] = cid  # 确保id是xmltv_id
        mapped += 1

print("Mapped channels:", mapped)

epg.write("output/epg_beinsports_mapped.xml", encoding="utf-8", xml_declaration=True)
print("Saved: output/epg_beinsports_mapped.xml")
