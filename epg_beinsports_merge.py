import glob
import xml.etree.ElementTree as ET
from collections import defaultdict

print("🔗 Loading regional XML files...")

files = glob.glob("tmp/*.xml")
if not files:
    raise SystemExit("❌ No tmp/*.xml files found")

channels = {}
programmes = []

def norm(name):
    return name.strip().lower().replace(" ", "_")

for file in files:
    print(" -", file)
    tree = ET.parse(file)
    root = tree.getroot()

    for ch in root.findall("channel"):
        name = ch.findtext("display-name", "unknown")
        cid = norm(name)

        if cid not in channels:
            new_ch = ET.Element("channel", id=cid)
            dn = ET.SubElement(new_ch, "display-name")
            dn.text = name
            channels[cid] = new_ch

    for p in root.findall("programme"):
        name = p.findtext("title", "")
        chname = root.find("channel/display-name")
        if chname is not None:
            cid = norm(chname.text)
        else:
            cid = p.attrib.get("channel", "unknown")

        p.attrib["channel"] = cid
        programmes.append(p)

# 排序
programmes.sort(key=lambda x: x.attrib["start"])

# 输出 XMLTV
tv = ET.Element("tv")

for ch in channels.values():
    tv.append(ch)

for p in programmes:
    tv.append(p)

ET.ElementTree(tv).write(
    "output/epg_beinsports_raw.xml",
    encoding="utf-8",
    xml_declaration=True
)

print("✅ Merged to output/epg_beinsports_raw.xml")
