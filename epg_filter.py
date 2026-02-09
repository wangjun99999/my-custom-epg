import requests
from xml.etree import ElementTree as ET
from xml.dom import minidom
import os
from datetime import datetime, timedelta, timezone
import re
import time

# -------------------------- 配置项 --------------------------
CHANNEL_TXT_FILE = "channel_list.txt"
RAW_EPG_URLS = [
    "https://epg.pw/xmltv/epg.xml",
    "https://epg.112114.xyz/pp.xml",
    "https://raw.githubusercontent.com/zzq1234567890/epg/refs/heads/main/epgziyong.xml",
    "http://epg.cdn.loc.cc/xml",
    "https://raw.githubusercontent.com/myhomebox/EPG/refs/heads/main/output/4g.xml",
    "https://raw.githubusercontent.com/myhomebox/EPG/refs/heads/main/output/hami.xml",
    "https://raw.githubusercontent.com/nightah/daddylive/refs/heads/main/epgs/daddylive-channels-epg.xml",
    "https://raw.githubusercontent.com/AqFad2811/epg/main/epg.xml"
]
OUTPUT_FILE = "custom_epg.xml"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 2
# ------------------------------------------------------------


CHINA_TZ = timezone(timedelta(hours=8))


# ---------------- 读取频道列表 ----------------
def read_channel_list(txt_path):
    channel_dict = {}
    channel_id_map = {}
    current_country = "默认"

    if not os.path.exists(txt_path):
        print(f"❌ 频道列表文件不存在：{txt_path}")
        return channel_dict, channel_id_map

    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if "," not in line:
            current_country = line
            continue

        fields = line.split(",")
        if len(fields) < 2:
            continue

        tvg_id = fields[0].strip()
        tvg_name = fields[1].strip()
        remark = fields[2].strip() if len(fields) > 2 else ""

        key = f"{tvg_id}_{tvg_name}"
        channel_dict[key] = (tvg_id, tvg_name, current_country, remark)

        if tvg_id:
            channel_id_map[tvg_id] = key
        if tvg_name:
            channel_id_map[tvg_name] = key

    print(f"✅ 读取频道数量：{len(channel_dict)}")
    return channel_dict, channel_id_map


# ---------------- 拉取EPG ----------------
def get_epg_data(url):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"🌐 获取 EPG（{attempt}/{MAX_RETRIES}）：{url}")
            r = requests.get(url, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            return ET.fromstring(r.content)
        except Exception as e:
            print(f"⚠️ 获取失败：{e}")
            time.sleep(2)
    return None


# ---------------- 频道过滤 ----------------
def filter_channels(epg_root, channel_dict, channel_id_map):
    filtered_channels = []
    filtered_programmes = []
    matched_channel_ids = set()

    for ch in epg_root.findall("channel"):
        cid = ch.get("id", "").strip()
        cname = ""
        for dn in ch.findall("display-name"):
            if dn.text:
                cname = dn.text.strip()
                break

        if cid in channel_id_map or cname in channel_id_map:
            filtered_channels.append(ch)
            matched_channel_ids.add(cid)

    for p in epg_root.findall("programme"):
        if p.get("channel") in matched_channel_ids:
            filtered_programmes.append(p)

    print(f"🎯 匹配频道 {len(filtered_channels)}，节目 {len(filtered_programmes)}")
    return filtered_channels, filtered_programmes


# ---------------- 核心：时间统一到 +0800 ----------------
def normalize_programme_times(programmes):
    """
    规则：
    - 带 +ZZZZ → 严格按原时区转成 +0800
    - 不带时区 → 本来就是北京时间，只补 +0800
    """
    count = 0

    for p in programmes:
        for attr in ("start", "stop"):
            raw = p.get(attr)
            if not raw:
                continue

            # 情况1：带时区
            m = re.match(r"(\d{14})\s*([+-]\d{4})", raw)
            if m:
                dt_part, tz_part = m.groups()
                base_dt = datetime.strptime(dt_part, "%Y%m%d%H%M%S")

                sign = 1 if tz_part[0] == "+" else -1
                hh = int(tz_part[1:3])
                mm = int(tz_part[3:5])
                src_tz = timezone(timedelta(hours=sign * hh, minutes=sign * mm))

                dt = base_dt.replace(tzinfo=src_tz)
                dt_cn = dt.astimezone(CHINA_TZ)

                p.set(attr, dt_cn.strftime("%Y%m%d%H%M%S +0800"))
                count += 1
                continue

            # 情况2：不带时区（已是北京时间）
            m2 = re.match(r"(\d{14})", raw)
            if m2:
                p.set(attr, m2.group(1) + " +0800")
                count += 1

    print(f"⏰ 时间统一完成：{count} 个字段 → +0800")


# ---------------- 去重 ----------------
def remove_duplicate_channels(channels):
    uniq = {}
    for ch in channels:
        cid = ch.get("id")
        if cid and cid not in uniq:
            uniq[cid] = ch
    return list(uniq.values())


def remove_duplicate_programmes(programmes):
    uniq = []
    seen = set()
    for p in programmes:
        key = (
            p.get("channel"),
            p.get("start"),
            p.get("stop"),
            (p.findtext("title") or "").strip()
        )
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    return uniq


# ---------------- 生成最终XML ----------------
def generate_custom_epg(channels, programmes):
    tv = ET.Element("tv")
    tv.set("generator-info-name", "my-custom-epg")

    # 🔥 关键修复：generated-on 也必须是 +0800
    tv.set("generated-on", datetime.now(CHINA_TZ).strftime("%Y%m%d%H%M%S +0800"))

    for ch in channels:
        tv.append(ch)
    for p in programmes:
        tv.append(p)

    xml_bytes = ET.tostring(tv, encoding="utf-8")
    pretty = minidom.parseString(xml_bytes).toprettyxml(
        indent="  ", encoding="utf-8"
    ).decode("utf-8")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(pretty)

    print(f"✅ 已生成 {OUTPUT_FILE}")


# ---------------- 主流程 ----------------
def main():
    print("🚀 开始生成自定义 EPG（统一中国时区 +0800）")

    channel_dict, channel_id_map = read_channel_list(CHANNEL_TXT_FILE)
    if not channel_dict:
        print("❌ 无有效频道，终止")
        return

    all_channels = []
    all_programmes = []

    for url in RAW_EPG_URLS:
        root = get_epg_data(url)
        if not root:
            continue

        chs, progs = filter_channels(root, channel_dict, channel_id_map)
        all_channels.extend(chs)
        all_programmes.extend(progs)

    if not all_channels:
        print("❌ 未匹配到任何频道")
        return

    all_channels = remove_duplicate_channels(all_channels)
    all_programmes = remove_duplicate_programmes(all_programmes)

    normalize_programme_times(all_programmes)
    generate_custom_epg(all_channels, all_programmes)

    print("🎉 完成，EPG 时间已 100% 对齐北京时间")


if __name__ == "__main__":
    main()
