import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

SRC = "output/epg_beinsports_raw.xml"
DST = "output/epg_beinsports.xml"

tree = ET.parse(SRC)
root = tree.getroot()

# beIN 所有地区时间 → UTC → 北京时间
CST = timezone(timedelta(hours=8))

def convert(ts):
    # 20260210120000 +0000
    dt = datetime.strptime(ts[:14], "%Y%m%d%H%M%S")
    tz = ts[15:]
    if tz == "+0000":
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.replace(tzinfo=timezone.utc)
    dt = dt.astimezone(CST)
    return dt.strftime("%Y%m%d%H%M%S +0800")

for p in root.findall("programme"):
    p.attrib["start"] = convert(p.attrib["start"])
    p.attrib["stop"] = convert(p.attrib["stop"])

tree.write(DST, encoding="utf-8", xml_declaration=True)

print("Saved Beijing time EPG:", DST)
