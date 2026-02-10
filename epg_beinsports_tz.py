import sys, re

src = "output/epg_beinsports_raw.xml"
out = "output/epg_beinsports.xml"

data = open(src, encoding="utf-8").read()
data = re.sub(r' ([+-]\d{4})"', ' +0800"', data)

open(out, "w", encoding="utf-8").write(data)
print("Saved", out)
