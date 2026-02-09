import sys
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta
import re

src, out = sys.argv[1], sys.argv[2]
tree = ET.parse(src)
root = tree.getroot()

pat = re.compile(r"(\d{14})(?:\s*([+-]\d{4}))?")

def fix(t):
    m = pat.match(t)
    if not m: return t
    dt = datetime.strptime(m.group(1), "%Y%m%d%H%M%S")
    tz = m.group(2)
    if tz:
        sign = 1 if tz[0]=="+" else -1
        off = sign*(int(tz[1:3]) + int(tz[3:5])/60)
        dt = dt - timedelta(hours=off)
    # now UTC → +8
    dt = dt + timedelta(hours=8)
    return dt.strftime("%Y%m%d%H%M%S +0800")

for p in root.findall("programme"):
    for k in ("start","stop"):
        p.set(k, fix(p.get(k)))

tree.write(out, encoding="utf-8", xml_declaration=True)
print("TZ fixed →", out)
