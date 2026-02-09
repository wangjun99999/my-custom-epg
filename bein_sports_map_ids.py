import sys
import xml.etree.ElementTree as ET
import re

src, out = sys.argv[1], sys.argv[2]

tree = ET.parse(src)
root = tree.getroot()

def map_id(old):
    """
    beinsports.com_mena-en.bein_sports_1  -> beIN1.mena
    beinsports.com_us-en.bein_sports_en_2 -> beIN2.us
    """
    m = re.search(r'beinsports\.com_(\w+).*bein_sports.*?(\d+)', old)
    if not m:
        return old
    region, num = m.group(1), m.group(2)
    region = region.split('-')[0]   # mena-en -> mena
    return f"beIN{num}.{region}"

# channel
for ch in root.findall("channel"):
    cid = ch.get("id")
    new = map_id(cid)
    if new != cid:
        ch.set("id", new)

# programme
for p in root.findall("programme"):
    cid = p.get("channel")
    new = map_id(cid)
    if new != cid:
        p.set("channel", new)

tree.write(out, encoding="utf-8", xml_declaration=True)
print("Mapped →", out)
