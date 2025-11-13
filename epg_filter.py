import requests
from xml.etree import ElementTree as ET
from xml.dom import minidom
import os
from datetime import datetime, timedelta
import re
import random

# -------------------------- 配置项 --------------------------
CHANNEL_TXT_FILE = "channel_list.txt"  # 频道列表文件
RAW_EPG_URLS = [
    "https://epg.pw/xmltv/epg.xml",
    "https://raw.githubusercontent.com/zzq12345/tvepg/refs/heads/main/epgziyong.xml",
    "https://raw.githubusercontent.com/myhomebox/EPG/refs/heads/main/output/4g.xml",
    "https://raw.githubusercontent.com/myhomebox/EPG/refs/heads/main/output/hami.xml",
    "https://raw.githubusercontent.com/nightah/daddylive/refs/heads/main/epgs/daddylive-channels-epg.xml",
    "https://raw.githubusercontent.com/AqFad2811/epg/main/epg.xml"
]
OUTPUT_FILE = "custom_epg.xml"
# ------------------------------------------------------------


def read_channel_list(txt_path):
    """读取频道列表"""
    channel_dict = {}
    current_country = None
    if not os.path.exists(txt_path):
        print(f"错误：频道列表文件 {txt_path} 不存在！")
        return channel_dict

    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "," not in line:
            current_country = line
            print(f"已识别国家分组：{current_country}")
            continue
        fields = line.split(",")
        if len(fields) != 3:
            print(f"警告：第{line_num}行格式错误，已跳过：{line}")
            continue
        tvg_id, tvg_name, remark = [x.strip() for x in fields]
        if not current_country:
            print(f"警告：第{line_num}行无所属国家，已跳过：{line}")
            continue
        key = f"{tvg_id}_{tvg_name}"
        channel_dict[key] = (tvg_id, tvg_name, current_country, remark)
        print(f"已读取频道：{tvg_name}（tvg-id：{tvg_id}，国家：{current_country}，备注：{remark}）")
    print(f"\n共读取到 {len(channel_dict)} 个频道")
    return channel_dict


def get_epg_data(url):
    """获取 EPG 数据"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return ET.fromstring(response.content)
    except Exception as e:
        print(f"获取EPG失败（{url}）：{e}")
        return None


def filter_channels(epg_root, channel_dict):
    """筛选频道与节目"""
    filtered_channels = []
    filtered_programmes = []
    target_tvg_ids = [info[0] for info in channel_dict.values() if info[0]]
    target_tvg_names = [info[1] for info in channel_dict.values() if info[1]]

    for channel in epg_root.findall("channel"):
        current_tvg_id = channel.get("id", "").strip()
        current_tvg_name = ""
        for dn in channel.findall("display-name"):
            if dn.text and dn.text.strip():
                current_tvg_name = dn.text.strip()
                break
        if (current_tvg_id in target_tvg_ids) or (current_tvg_name in target_tvg_names):
            filtered_channels.append(channel)
            print(f"已筛选频道：{current_tvg_name or current_tvg_id}")

    filtered_tvg_ids = [ch.get("id", "").strip() for ch in filtered_channels if ch.get("id")]
    for programme in epg_root.findall("programme"):
        if programme.get("channel", "").strip() in filtered_tvg_ids:
            filtered_programmes.append(programme)

    print(f"筛选到频道 {len(filtered_channels)} 个，节目 {len(filtered_programmes)} 条")
    return filtered_channels, filtered_programmes


# ---------------- 智能检测时区部分 ----------------
def detect_epg_time_offset(programmes):
    """
    自动检测 EPG 源的时区偏移量
    通过随机抽样节目时间判断是否为北京时间 (+8) 或 UTC (0)
    """
    offsets = []
    sample = random.sample(programmes, min(len(programmes), 30)) if programmes else []
    now_local = datetime.utcnow() + timedelta(hours=8)

    for p in sample:
        start = p.get("start", "")
        match = re.match(r"(\d{14})\s*([+-]\d{4})?", start)
        if not match:
            continue
        dt_part, tz_part = match.groups()
        tz_part = tz_part or "+0000"
        try:
            dt = datetime.strptime(dt_part, "%Y%m%d%H%M%S")
        except:
            continue

        # 判断时区差距
        diff_hours = (dt - now_local).total_seconds() / 3600.0
        if abs(diff_hours) < 2:  # 已是北京时间
            offsets.append(8)
        elif abs(diff_hours - 8) < 2 or abs(diff_hours + 8) < 2:  # UTC
            offsets.append(0)

    if not offsets:
        print("⚠️ 未能确定 EPG 源时区，默认按 UTC 处理。")
        return 0
    avg_offset = round(sum(offsets) / len(offsets))
    print(f"⚙️ 自动检测 EPG 源时区：UTC+{avg_offset}")
    return avg_offset


def adjust_programme_time_to_china(programmes):
    """
    自动检测并转换节目时间为中国时区 (+0800)
    """
    if not programmes:
        return
    detected_offset = detect_epg_time_offset(programmes)
    if detected_offset == 8:
        print("✅ 检测到源 EPG 已是北京时间 (+0800)，无需调整。")
        return

    for p in programmes:
        for attr in ['start', 'stop']:
            t = p.get(attr)
            if not t:
                continue
            match = re.match(r"(\d{14})\s*([+-]\d{4})?", t)
            if not match:
                continue
            dt_part, tz_part = match.groups()
            tz_part = tz_part or "+0000"
            try:
                dt = datetime.strptime(dt_part, "%Y%m%d%H%M%S")
            except ValueError:
                continue

            sign = 1 if tz_part.startswith("+") else -1
            offset_hours = int(tz_part[1:3])
            offset_minutes = int(tz_part[3:])
            total_offset = sign * (offset_hours + offset_minutes / 60)

            dt_utc = dt - timedelta(hours=total_offset)
            dt_china = dt_utc + timedelta(hours=8)
            new_time = dt_china.strftime("%Y%m%d%H%M%S") + " +0800"
            p.set(attr, new_time)

    print("⏰ 所有节目时间已统一转换为北京时间 (+0800)")
# ------------------------------------------------------------


def generate_custom_epg(filtered_channels, filtered_programmes, epg_root):
    """生成输出 EPG 文件"""
    tv_root = ET.Element("tv")
    for key, value in epg_root.attrib.items():
        tv_root.set(key, value)

    for ch in filtered_channels:
        tv_root.append(ch)
    for prog in filtered_programmes:
        tv_root.append(prog)

    rough_string = ET.tostring(tv_root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    print(f"\n✅ EPG 已生成：{OUTPUT_FILE}")


# ---------------- 主程序 ----------------
if __name__ == "__main__":
    print("="*60)
    print("开始执行自定义 EPG 生成脚本（含智能时区检测）")
    print("="*60)

    channel_dict = read_channel_list(CHANNEL_TXT_FILE)
    if not channel_dict:
        print("未读取到有效频道，终止。")
        exit(1)

    all_filtered_channels = []
    all_filtered_programmes = []
    first_epg_root = None

    for url in RAW_EPG_URLS:
        print(f"\n开始处理：{url}")
        epg_root = get_epg_data(url)
        if not epg_root:
            continue
        if not first_epg_root:
            first_epg_root = epg_root
        chs, progs = filter_channels(epg_root, channel_dict)
        all_filtered_channels.extend(chs)
        all_filtered_programmes.extend(progs)

    # 去重
    unique_channels = {ch.get("id", "").strip(): ch for ch in all_filtered_channels}.values()
    unique_programmes = []
    seen_prog_keys = set()
    for prog in all_filtered_programmes:
        key = f"{prog.get('channel','')}_{prog.get('start','')}"
        if key not in seen_prog_keys:
            seen_prog_keys.add(key)
            unique_programmes.append(prog)

    print(f"\n去重后频道 {len(unique_channels)} 个，节目 {len(unique_programmes)} 条")

    # 智能调整时区
    adjust_programme_time_to_china(unique_programmes)

    if first_epg_root:
        generate_custom_epg(unique_channels, unique_programmes, first_epg_root)
    else:
        print("未获取到有效 EPG 数据，无法生成。")

    print("="*60)
    print("脚本执行完成 ✅ 所有节目时间已确保为中国时区 (+0800)")
    print("="*60)
