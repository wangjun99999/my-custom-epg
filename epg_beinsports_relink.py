import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# 读取 UUID → xmltv_id
uuid_map = {}

tree = ET.parse("epg_beinsports_channels.xml")
for ch in tree.findall("channel"):
    uuid = ch.get("site_id")
    xmltv = ch.get("xmltv_id")
    if uuid and xmltv:
        uuid_map[uuid] = xmltv

# 读取官方 EPG
epg = ET.parse("epg_beinsports_raw.xml")
root = epg.getroot()

# 建新 tv
new_tv = ET.Element("tv")

# 处理频道
for uuid, xmltv in uuid_map.items():
    ch = ET.SubElement(new_tv, "channel", {"id": xmltv})
    ET.SubElement(ch, "display-name").text = xmltv

# 处理节目
for p in root.findall("programme"):
    uuid = p.get("channel")
    if uuid not in uuid_map:
        continue

    start = p.get("start")
    stop = p.get("stop")

    def to_cst(t):
        dt = datetime.strptime(t[:14], "%Y%m%d%H%M%S") + timedelta(hours=8)
        return dt.strftime("%Y%m%d%H%M%S") + " +0800"

    p.set("channel", uuid_map[uuid])
    p.set("start", to_cst(start))
    p.set("stop", to_cst(stop))

    new_tv.append(p)

ET.ElementTree(new_tv).write("output/epg_beinsports.xml", encoding="utf-8", xml_declaration=True)
print("Generated output/epg_beinsports.xml")
