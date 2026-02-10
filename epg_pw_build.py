import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

EPG_URL = "https://epg.pw/xmltv/epg.xml"

wanted = []

with open("epg_pw_channels.txt", "r", encoding="utf-8") as f:
    for line in f:
        if "|" in line:
            tvg_id, tvg_name, note = [x.strip() for x in line.split("|")]
            wanted.append((tvg_id.lower(), tvg_name.lower(), note))

print("Loading epg.pw...")
xml = requests.get(EPG_URL).content
root = ET.fromstring(xml)

out = ET.Element("tv")
valid = set()

# 匹配 channel
for ch in root.findall("channel"):
    cid = ch.attrib["id"].lower()
    names = [d.text.lower() for d in ch.findall("display-name")]

    for tvg_id, tvg_name, note in wanted:
        if tvg_id == cid and tvg_name in names:
            new = ET.SubElement(out, "channel", id=ch.attrib["id"])
            for d in ch.findall("display-name"):
                ET.SubElement(new, "display-name").text = d.text
            ET.SubElement(new, "display-name").text = note
            valid.add(ch.attrib["id"])

print("Matched channels:", len(valid))

def bj(t):
    dt = datetime.strptime(t[:14], "%Y%m%d%H%M%S")
    dt += timedelta(hours=8)
    return dt.strftime("%Y%m%d%H%M%S") + " +0800"

for p in root.findall("programme"):
    if p.attrib["channel"] in valid:
        new = ET.SubElement(out, "programme")
        new.attrib["channel"] = p.attrib["channel"]
        new.attrib["start"] = bj(p.attrib["start"])
        new.attrib["stop"] = bj(p.attrib["stop"])
        for c in p:
            new.append(c)

ET.ElementTree(out).write("output/epg_pw.xml", encoding="utf-8", xml_declaration=True)
print("Done")
