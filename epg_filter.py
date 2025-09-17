import requests
from xml.etree import ElementTree as ET
from xml.dom import minidom
import os

# -------------------------- 配置项 --------------------------
# 频道列表TXT文件路径
CHANNEL_TXT_FILE = "channel_list.txt"
# 原始EPG链接
RAW_EPG_URLS = [
    "https://epg.pw/xmltv/epg_GB.xml",
    "https://github.com/sparkssssssssss/epg/blob/main/pp.xml",
    "https://raw.githubusercontent.com/AqFad2811/epg/main/epg.xml"
]
# 输出的自定义EPG文件名
OUTPUT_FILE = "custom_epg.xml"
# ------------------------------------------------------------

def read_channel_list(txt_path):
    """从TXT文件读取频道列表（支持国家分组格式）"""
    channel_dict = {}
    current_country = None  # 当前国家（从国家行获取）
    
    if not os.path.exists(txt_path):
        print(f"错误：频道列表文件 {txt_path} 不存在！")
        return channel_dict
    
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        # 跳过空行或注释行
        if not line or line.startswith("#"):
            continue
        
        # 识别国家行（判断是否为"国家名称+国家代码"格式，不含逗号）
        if "," not in line:
            current_country = line
            print(f"已识别国家分组：{current_country}")
            continue
        
        # 解析频道行（格式：tvg-id,tvg-name,备注）
        fields = line.split(",")
        if len(fields) != 3:
            print(f"警告：第{line_num}行格式错误（需3个字段），已跳过：{line}")
            continue
        
        # 提取字段
        tvg_id = fields[0].strip()
        tvg_name = fields[1].strip()
        remark = fields[2].strip()
        
        # 检查是否已设置国家
        if not current_country:
            print(f"警告：第{line_num}行无所属国家，已跳过：{line}")
            continue
        
        # 跳过tvg-id和tvg-name都为空的行
        if not tvg_id and not tvg_name:
            print(f"警告：第{line_num}行tvg-id和tvg-name均为空，已跳过：{line}")
            continue
        
        # 存储频道信息（包含国家）
        key = f"{tvg_id}_{tvg_name}"
        channel_dict[key] = (tvg_id, tvg_name, current_country, remark)
        print(f"已读取频道：{tvg_name}（tvg-id：{tvg_id}，国家：{current_country}，备注：{remark}）")
    
    print(f"\n共从TXT读取到 {len(channel_dict)} 个有效频道")
    return channel_dict

def get_epg_data(url):
    """获取原始EPG的XML数据"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return ET.fromstring(response.content)
    except requests.exceptions.Timeout:
        print(f"获取EPG失败（{url}）：请求超时（30秒）")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"获取EPG失败（{url}）：HTTP错误 {e.response.status_code}")
        return None
    except Exception as e:
        print(f"获取EPG失败（{url}）：未知错误 {str(e)}")
        return None

def filter_channels(epg_root, channel_dict):
    """基于tvg-id/tvg-name筛选EPG频道和节目"""
    filtered_channels = []
    filtered_programmes = []
    target_tvg_ids = [info[0] for info in channel_dict.values() if info[0]]
    target_tvg_names = [info[1] for info in channel_dict.values() if info[1]]
    
    # 筛选频道
    for channel in epg_root.findall("channel"):
        current_tvg_id = channel.get("id", "").strip()
        current_tvg_name = ""
        display_names = channel.findall("display-name")
        for dn in display_names:
            if dn.text and dn.text.strip():
                current_tvg_name = dn.text.strip()
                break
        
        # 匹配逻辑：tvg-id或tvg-name匹配
        is_matched = (current_tvg_id in target_tvg_ids) or (current_tvg_name in target_tvg_names)
        if not is_matched:
            continue
        
        # 获取匹配频道的详细信息
        matched_info = None
        for info in channel_dict.values():
            if (info[0] == current_tvg_id) or (info[1] == current_tvg_name):
                matched_info = info
                break
        if matched_info:
            tvg_id, tvg_name, country, remark = matched_info
            print(f"已筛选频道：{tvg_name}（tvg-id：{tvg_id}，国家：{country}，备注：{remark}）")
        
        filtered_channels.append(channel)
    
    # 筛选节目
    filtered_tvg_ids = [ch.get("id", "").strip() for ch in filtered_channels if ch.get("id")]
    for programme in epg_root.findall("programme"):
        programme_tvg_id = programme.get("channel", "").strip()
        if programme_tvg_id in filtered_tvg_ids:
            filtered_programmes.append(programme)
    
    print(f"从当前EPG筛选到 {len(filtered_channels)} 个频道，{len(filtered_programmes)} 个节目")
    return filtered_channels, filtered_programmes

def generate_custom_epg(filtered_channels, filtered_programmes, epg_root):
    """生成自定义EPG XML文件"""
    if not filtered_channels:
        print("警告：无筛选到的频道，无法生成EPG文件！")
        return False
    
    tv_root = ET.Element("tv")
    # 复制原始EPG的属性
    for key, value in epg_root.attrib.items():
        tv_root.set(key, value)
    
    # 添加频道和节目
    for ch in filtered_channels:
        tv_root.append(ch)
    for prog in filtered_programmes:
        tv_root.append(prog)
    
    # 美化XML
    rough_string = ET.tostring(tv_root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
    
    # 保存文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    print(f"\n自定义EPG生成完成！文件：{OUTPUT_FILE}（频道数：{len(filtered_channels)}，节目数：{len(filtered_programmes)}）")
    return True

if __name__ == "__main__":
    print("="*50)
    print("开始执行自定义EPG筛选脚本")
    print("="*50)
    
    # 读取频道列表
    channel_dict = read_channel_list(CHANNEL_TXT_FILE)
    if not channel_dict:
        print("错误：未读取到任何有效频道，脚本终止！")
        exit(1)
    
    # 处理原始EPG
    all_filtered_channels = []
    all_filtered_programmes = []
    first_epg_root = None  # 用于获取XML根节点属性
    
    for url in RAW_EPG_URLS:
        print(f"\n" + "="*30)
        print(f"开始处理原始EPG链接：{url}")
        print("="*30)
        epg_root = get_epg_data(url)
        if not epg_root:
            print(f"跳过当前EPG链接：{url}")
            continue
        if not first_epg_root:
            first_epg_root = epg_root  # 记录第一个有效的EPG根节点
        
        chs, progs = filter_channels(epg_root, channel_dict)
        all_filtered_channels.extend(chs)
        all_filtered_programmes.extend(progs)
    
    # 去重处理
    print(f"\n" + "="*30)
    print("开始去重重复的频道和节目")
    print("="*30)
    
    # 频道去重（基于tvg-id）
    unique_channel_ids = set()
    unique_channels = []
    for ch in all_filtered_channels:
        ch_id = ch.get("id", "").strip()
        if ch_id not in unique_channel_ids:
            unique_channel_ids.add(ch_id)
            unique_channels.append(ch)
    
    # 节目去重（基于开始时间+频道id）
    unique_program_keys = set()
    unique_programmes = []
    for prog in all_filtered_programmes:
        prog_start = prog.get("start", "").strip()
        prog_channel = prog.get("channel", "").strip()
        prog_key = f"{prog_start}_{prog_channel}"
        if prog_key not in unique_program_keys:
            unique_program_keys.add(prog_key)
            unique_programmes.append(prog)
    
    print(f"去重后：频道数 {len(unique_channels)}（原{len(all_filtered_channels)}），节目数 {len(unique_programmes)}（原{len(all_filtered_programmes)}）")
    
    # 生成最终EPG
    if first_epg_root:
        generate_custom_epg(unique_channels, unique_programmes, first_epg_root)
    else:
        print("错误：未获取到任何有效的原始EPG数据，无法生成自定义EPG！")
    
    print(f"\n" + "="*50)
    print("脚本执行完成！")
    print("="*50)
