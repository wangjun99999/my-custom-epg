import requests
from datetime import datetime, timedelta, timezone

TZ8 = timezone(timedelta(hours=8))

def to_xmltv(dt):
    return dt.astimezone(TZ8).strftime("%Y%m%d%H%M%S +0800")

def fetch(url):
    return requests.get(url, timeout=10).json()

data = fetch("https://www.adsports.ae/api/epg/today")
data2 = fetch("https://www.adsports.ae/api/epg/tomorrow")

channels = {
    "ads1": ("AbuDhabiSports1.ae@MENA", "Abu Dhabi Sports 1"),
    "ads2": ("AbuDhabiSports2.ae@MENA", "Abu Dhabi Sports 2"),
}

programmes = []

for block in (data, data2):
    for ch in block["channels"]:
        if ch["id"] in channels:
            cid, name = channels[ch["id"]]
            for p in ch["programs"]:
                start = datetime.fromisoformat(p["start"])
                end   = datetime.fromisoformat(p["end"])
                programmes.append((cid, name, p["title"], start, end))

now = datetime.now(TZ8)

xml = []
xml.append('<?xml version="1.0" encoding="UTF-8"?>')
xml.append(f'<tv generator-info-name="my-custom-epg" generated-on="{now.strftime("%Y%m%d%H%M%S +0800")}">')

# channels
xml.append(f'''
  <channel id="AbuDhabiSports1.ae@MENA">
    <display-name>Abu Dhabi Sports 1</display-name>
    <icon src="https://i.postimg.cc/Nj4JQMTX/Picsart-25-10-04-11-52-31-346.png"/>
  </channel>
  <channel id="AbuDhabiSports2.ae@MENA">
    <display-name>Abu Dhabi Sports 2</display-name>
    <icon src="https://i.postimg.cc/Nj4JQMTX/Picsart-25-10-04-11-52-31-346.png"/>
  </channel>
''')

# programmes
for cid, name, title, start, end in sorted(programmes, key=lambda x: x[3]):
    xml.append(f'''
  <programme channel="{cid}" start="{to_xmltv(start)}" stop="{to_xmltv(end)}">
    <title lang="en">{title}</title>
  </programme>
''')

xml.append('</tv>')

with open("epg_abudhabi.xml", "w", encoding="utf-8") as f:
    f.write("\n".join(xml))

print("✅ Abu Dhabi Sports 1 & 2 EPG generated")
