from datetime import datetime, timedelta, timezone

CHINA_TZ = timezone(timedelta(hours=8))

now = datetime.now(CHINA_TZ)
start = now.replace(hour=0, minute=0, second=0, microsecond=0)
stop = start + timedelta(days=1)

start_str = start.strftime("%Y%m%d%H%M%S +0800")
stop_str  = stop.strftime("%Y%m%d%H%M%S +0800")
generated_on = now.strftime("%Y%m%d%H%M%S +0800")

epg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<tv generator-info-name="my-custom-epg" generated-on="{generated_on}">

  <channel id="AbudhabiSports.ae@MENA">
    <display-name>Abu Dhabi Sports</display-name>
    <icon src="https://i.postimg.cc/Nj4JQMTX/Picsart-25-10-04-11-52-31-346.png"/>
    <url>https://www.adsports.ae</url>
  </channel>

  <channel id="ShashaSports.kw@MENA">
    <display-name>SHASHA Sports</display-name>
    <icon src="https://i.postimg.cc/Y0VGd3cw/Picsart-25-10-05-20-04-57-624.png"/>
    <url>https://www.shasha.kw</url>
  </channel>

  <channel id="Thmanya.sa@MENA">
    <display-name>Thmanya</display-name>
    <icon src="https://iili.io/KhlVFeI.png"/>
    <url>https://www.thmanyah.com</url>
  </channel>

  <channel id="AsharqDocumentary.sa@MENA">
    <display-name>Asharq Documentary</display-name>
    <icon src="https://iili.io/KhlV35N.png"/>
    <url>https://www.asharqdocumentary.com</url>
  </channel>

  <channel id="AsharqDiscovery.sa@MENA">
    <display-name>Asharq Discovery</display-name>
    <icon src="https://iili.io/KhlV2Jp.png"/>
    <url>https://www.asharqdiscovery.com</url>
  </channel>

  <channel id="SSC.sa@MENA">
    <display-name>SSC</display-name>
    <icon src="https://iili.io/Kh0GpdQ.png"/>
    <url>https://www.ssc.com.sa</url>
  </channel>

  <channel id="SynSports.is@EU">
    <display-name>Syn Sports</display-name>
    <icon src="https://iili.io/Kh0Gtqb.png"/>
    <url>https://www.syn.is</url>
  </channel>

  <channel id="GulliArabic.me@MENA">
    <display-name>Gulli Arabic</display-name>
    <icon src="https://iili.io/Kh139SI.png"/>
    <url>https://www.gulliarabic.com</url>
  </channel>

  <programme start="{start_str}" stop="{stop_str}" channel="AbudhabiSports.ae@MENA">
    <title lang="ar">قناة الدوري الإيطالي</title>
  </programme>

  <programme start="{start_str}" stop="{stop_str}" channel="ShashaSports.kw@MENA">
    <title lang="ar">مباريات الدوري الإيطالي</title>
  </programme>

  <programme start="{start_str}" stop="{stop_str}" channel="Thmanya.sa@MENA">
    <title lang="ar">برامج وثائقية وحوارية</title>
  </programme>

  <programme start="{start_str}" stop="{stop_str}" channel="AsharqDocumentary.sa@MENA">
    <title lang="ar">وثائقيات تاريخية وثقافية</title>
  </programme>

  <programme start="{start_str}" stop="{stop_str}" channel="AsharqDiscovery.sa@MENA">
    <title lang="ar">برامج عن الطبيعة والعلوم</title>
  </programme>

  <programme start="{start_str}" stop="{stop_str}" channel="SSC.sa@MENA">
    <title lang="ar">أخبار الرياضة السعودية</title>
  </programme>

  <programme start="{start_str}" stop="{stop_str}" channel="SynSports.is@EU">
    <title lang="en">Icelandic Sports Highlights</title>
  </programme>

  <programme start="{start_str}" stop="{stop_str}" channel="GulliArabic.me@MENA">
    <title lang="ar">أفلام كرتون ومغامرات</title>
  </programme>

</tv>
'''

with open("epg_starzplay-sports.xml", "w", encoding="utf-8") as f:
    f.write(epg_content)

print("✅ 已生成 epg_starzplay-sports.xml （+0800 时区正确）")
