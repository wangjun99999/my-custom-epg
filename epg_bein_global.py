import requests
from datetime import datetime, timedelta, timezone

REGIONS = ["mena","fr","apac","au","us","es","tr"]
TZ8 = timezone(timedelta(hours=8))

def to_xmltv(dt):
    return dt.astimezone(TZ8).strftime("%Y%m%d%H%M%S +0800")

channels = {}
programmes = []

for region in REGIONS:
    url = f"https://www.beinsports.com/{region}/api/epg/events"
    try:
        data = requests.get(url, timeout=15).json()
    except:
        continue

    for item in data.get("events", []):
        ch = item["channel"]
        cid = f"beIN.{region}.{ch['id']}"
        cname = f"{ch['name']} ({region.upper()})"
        channels[cid] = cname

        start = datetime.fromisoformat(item["startTime"].replace("Z","+00:00"))
        end   = datetime.fromisoformat(item["endTime"].replace("Z","+00:00"))

        programmes.append((cid, item["title"], start, end))

now = datetime.now(TZ8)

xml = []
xml.append('<?xml version="1.0" encoding="UTF-8"?>')
xml.append(f'<tv generator-info-name="my-custom-epg" generated-on="{now.strftime("%Y%m%d%H%M%S +0800")}">')

for cid, name in sorted(channels.items()):
    xml.append(f'''
  <channel id="{cid}">
    <display-name>{name}</display-name>
    <icon src="https://upload.wikimedia.org/wikipedia/commons/1/12/BeIN_Sports_logo.svg"/>
  </channel>
''')

for cid, title, start, end in sorted(programmes, key=lambda x: x[2]):
    xml.append(f'''
  <programme channel="{cid}" start="{to_xmltv(start)}" stop="{to_xmltv(end)}">
    <title>{title}</title>
  </programme>
''')

xml.append("</tv>")

with open("epg_bein_global.xml", "w", encoding="utf-8") as f:
    f.write("\n".join(xml))

print("✅ Global beIN EPG generated")
