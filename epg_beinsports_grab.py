import requests

URL = "https://www.beinsports.com/epg/epg.xml"

r = requests.get(URL, timeout=30)
r.raise_for_status()

with open("epg_beinsports_raw.xml", "wb") as f:
    f.write(r.content)

print("Downloaded beIN official EPG")
