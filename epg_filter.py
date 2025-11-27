import requests
from xml.etree import ElementTree as ET
from xml.dom import minidom
import os
from datetime import datetime, timedelta
import re
import time

# -------------------------- 配置项 --------------------------
CHANNEL_TXT_FILE = "channel_list.txt"
RAW_EPG_URLS = [
    "https://epg.pw/xmltv/epg.xml",
    "https://raw.githubusercontent.com/zzq1234567890/epg/refs/heads/main/epgnew.xml",
    "https://raw.githubusercontent.com/myhomebox/EPG/refs/heads/main/output/4g.xml",
    "https://raw.githubusercontent.com/myhomebox/EPG/refs/heads/main/output/hami.xml",
    "https://raw.githubusercontent.com/nightah/daddylive/refs/heads/main/epgs/daddylive-channels-epg.xml",
    "https://raw.githubusercontent.com/AqFad2811/epg/main/epg.xml"
]
OUTPUT_FILE = "custom_epg.xml"
REQUEST_TIMEOUT = 30
MAX_RETRIES = 2
# ------------------------------------------------------------

def read_channel_list(txt_path):
    """读取频道列表 - 增强错误处理"""
    channel_dict = {}
    channel_id_map = {}  # 用于快速查找
    current_country = "默认"
    
    if not os.path.exists(txt_path):
        print(f"错误：频道列表文件 {txt_path} 不存在！")
        return channel_dict, channel_id_map

    try:
        with open(txt_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"读取文件失败：{e}")
        return channel_dict, channel_id_map

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
            
        # 检测国家分组行（不包含逗号的行）
        if "," not in line:
            current_country = line
            print(f"已识别国家分组：{current_country}")
            continue
            
        # 处理频道行
        fields = line.split(",")
        if len(fields) < 2:
            print(f"警告：第{line_num}行格式错误，已跳过：{line}")
            continue
            
        # 处理不同数量的字段
        tvg_id = fields[0].strip()
        tvg_name = fields[1].strip()
        remark = fields[2].strip() if len(fields) > 2 else ""
        
        key = f"{tvg_id}_{tvg_name}"
        channel_dict[key] = (tvg_id, tvg_name, current_country, remark)
        
        # 建立映射关系用于快速查找
        if tvg_id:
            channel_id_map[tvg_id] = key
        if tvg_name:
            channel_id_map[tvg_name] = key
            
        print(f"已读取频道：{tvg_name}（tvg-id：{tvg_id}，国家：{current_country}，备注：{remark}）")
    
    print(f"\n共读取到 {len(channel_dict)} 个频道")
    return channel_dict, channel_id_map

def get_epg_data(url, retries=MAX_RETRIES):
    """获取 EPG 数据 - 增加重试机制"""
    for attempt in range(retries):
        try:
            print(f"尝试获取 EPG 数据 ({attempt+1}/{retries})：{url}")
            response = requests.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            # 验证是否为有效的XML
            try:
                root = ET.fromstring(response.content)
                print(f"成功获取 EPG 数据，共 {len(root.findall('channel'))} 个频道")
                return root
            except ET.ParseError as e:
                print(f"XML 解析失败：{e}")
                if attempt == retries - 1:
                    return None
                
        except requests.exceptions.RequestException as e:
            print(f"获取EPG失败（尝试 {attempt+1}）：{e}")
            if attempt == retries - 1:
                return None
            time.sleep(2)  # 等待后重试
    
    return None

def filter_channels(epg_root, channel_dict, channel_id_map):
    """筛选频道与节目 - 优化匹配逻辑"""
    filtered_channels = []
    filtered_programmes = []
    
    # 用于记录已处理的频道ID，避免重复
    processed_channel_ids = set()
    
    for channel in epg_root.findall("channel"):
        channel_id = channel.get("id", "").strip()
        
        # 如果频道ID已经在处理过，跳过
        if channel_id in processed_channel_ids:
            continue
            
        # 查找频道名称
        channel_name = ""
        for dn in channel.findall("display-name"):
            if dn.text and dn.text.strip():
                channel_name = dn.text.strip()
                break
        
        # 检查是否匹配目标频道
        if (channel_id in channel_id_map) or (channel_name in channel_id_map):
            filtered_channels.append(channel)
            processed_channel_ids.add(channel_id)
            print(f"已筛选频道：{channel_name or channel_id}")

    # 筛选节目
    for programme in epg_root.findall("programme"):
        programme_channel = programme.get("channel", "").strip()
        if programme_channel in processed_channel_ids:
            filtered_programmes.append(programme)

    print(f"从当前源筛选到频道 {len(filtered_channels)} 个，节目 {len(filtered_programmes)} 条")
    return filtered_channels, filtered_programmes

def adjust_programme_time_to_china(programmes):
    """强制转换节目时间为中国时区 (+0800) - 优化版本"""
    if not programmes:
        return

    adjusted_count = 0
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

            # 将所有时间统一视为 UTC，再加 8 小时
            dt_china = dt + timedelta(hours=8)
            new_time = dt_china.strftime("%Y%m%d%H%M%S") + " +0800"
            p.set(attr, new_time)
            adjusted_count += 1

    print(f"⏰ 已转换 {adjusted_count} 个节目时间属性为北京时间 (+0800)")

def remove_duplicate_channels(channels):
    """去除重复频道"""
    unique_channels = {}
    for channel in channels:
        channel_id = channel.get("id", "").strip()
        if channel_id and channel_id not in unique_channels:
            unique_channels[channel_id] = channel
    return list(unique_channels.values())

def remove_duplicate_programmes(programmes):
    """去除重复节目"""
    unique_programmes = []
    seen_prog_keys = set()
    
    for prog in programmes:
        channel = prog.get('channel', '')
        start = prog.get('start', '')
        stop = prog.get('stop', '')
        title_elem = prog.find('title')
        title = title_elem.text if title_elem is not None and title_elem.text else ''
        
        # 使用更精确的键来去重
        key = f"{channel}_{start}_{stop}_{title}"
        if key not in seen_prog_keys:
            seen_prog_keys.add(key)
            unique_programmes.append(prog)
            
    return unique_programmes

def generate_custom_epg(filtered_channels, filtered_programmes):
    """生成输出 EPG 文件"""
    # 创建新的XML根元素
    tv_root = ET.Element("tv")
    tv_root.set("source-info-name", "Custom EPG Generator")
    tv_root.set("generator-info-name", "EPG Merge Script")
    tv_root.set("generated-on", datetime.now().strftime("%Y%m%d%H%M%S"))
    
    # 添加频道
    for ch in filtered_channels:
        tv_root.append(ch)
    
    # 添加节目
    for prog in filtered_programmes:
        tv_root.append(prog)
    
    # 生成格式化的XML
    rough_string = ET.tostring(tv_root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
    
    # 保存文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    
    print(f"\n✅ EPG 已生成：{OUTPUT_FILE}")
    print(f"   包含频道：{len(filtered_channels)} 个")
    print(f"   包含节目：{len(filtered_programmes)} 条")

def main():
    print("="*60)
    print("开始执行自定义 EPG 生成脚本（强制中国时区）")
    print("="*60)

    # 读取频道列表
    channel_dict, channel_id_map = read_channel_list(CHANNEL_TXT_FILE)
    if not channel_dict:
        print("未读取到有效频道，终止。")
        return

    all_filtered_channels = []
    all_filtered_programmes = []
    successful_sources = 0

    # 处理每个EPG源
    for url in RAW_EPG_URLS:
        print(f"\n{'='*50}")
        print(f"开始处理源：{url}")
        
        epg_root = get_epg_data(url)
        if not epg_root:
            continue
            
        chs, progs = filter_channels(epg_root, channel_dict, channel_id_map)
        all_filtered_channels.extend(chs)
        all_filtered_programmes.extend(progs)
        successful_sources += 1
        
        print(f"当前源处理完成")

    if successful_sources == 0:
        print("错误：所有EPG源都无法访问！")
        return

    # 去重处理
    print(f"\n正在进行去重处理...")
    print(f"去重前：频道 {len(all_filtered_channels)} 个，节目 {len(all_filtered_programmes)} 条")
    
    unique_channels = remove_duplicate_channels(all_filtered_channels)
    unique_programmes = remove_duplicate_programmes(all_filtered_programmes)
    
    print(f"去重后：频道 {len(unique_channels)} 个，节目 {len(unique_programmes)} 条")

    # 强制调整时区为北京时间
    adjust_programme_time_to_china(unique_programmes)

    # 生成最终EPG文件
    generate_custom_epg(unique_channels, unique_programmes)

    print("="*60)
    print("脚本执行完成 ✅")
    print(f"成功处理 {successful_sources}/{len(RAW_EPG_URLS)} 个EPG源")
    print("所有节目时间已确保为中国时区 (+0800)")
    print("="*60)

if __name__ == "__main__":
    main()
