# diagnostic_and_fix_epg.py
import requests
from xml.etree import ElementTree as ET
from datetime import datetime, timedelta
import re
import random
import sys

EPG_URL = "https://epg.pw/xmltv/epg.xml"
SAMPLE_COUNT = 80  # 抽样数量（越多越准，但慢）
LOOKAHEAD_HOURS = 48  # 判断"近期节目"的时间窗口

re_time = re.compile(r"^(\d{14})(?:\s*([+-]\d{4}))?$")

def fetch_epg_root(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        return root
    except Exception as e:
        print("抓取/解析失败：", e)
        return None

def parse_programme_time_attr(time_str):
    """
    返回 (datetime, tz_offset_hours_or_None)
    tz_offset_hours_or_None: 如果字符串里有 +ZZZZ 则返回偏移小时（如 +0900 -> 9），否则返回 None
    """
    if not time_str:
        return None, None
    m = re_time.match(time_str.strip())
    if not m:
        return None, None
    dt_part, tz = m.groups()
    try:
        dt = datetime.strptime(dt_part, "%Y%m%d%H%M%S")
    except:
        return None, None
    if tz:
        sign = 1 if tz[0] == "+" else -1
        hh = int(tz[1:3])
        mm = int(tz[3:5])
        offset = sign * (hh + mm/60.0)
        return dt, offset
    else:
        return dt, None

def analyze_root(root, sample_count=SAMPLE_COUNT):
    progs = root.findall("programme")
    if not progs:
        print("没有找到 programme 元素")
        return None

    # 随机抽样
    sample = random.sample(progs, min(len(progs), sample_count))
    now_utc = datetime.utcnow()
    now_local = now_utc + timedelta(hours=8)

    stats = {"with_tz":0, "no_tz":0, "no_tz_like_local":0, "no_tz_like_utc":0, "ambiguous":0}
    examples = []

    for p in sample:
        start_raw = p.get("start","").strip()
        dt, tz = parse_programme_time_attr(start_raw)
        if not dt:
            continue
        if tz is not None:
            stats["with_tz"] += 1
            # compute dt in local time for example
            dt_utc = dt - timedelta(hours=tz)
            dt_china = dt_utc + timedelta(hours=8)
            examples.append(("with_tz", start_raw, dt_china.strftime("%Y%m%d%H%M%S +0800")))
            continue
        # 无 tz 情况 —— 需要判断它更像是本地时间还是 UTC
        stats["no_tz"] += 1
        # consider programmes within next LOOKAHEAD_HOURS (relative to now_local)
        # compute difference between dt and now_local
        diff_hours_local = (dt - now_local).total_seconds() / 3600.0
        diff_hours_utc = (dt - now_utc).total_seconds() / 3600.0

        # if dt is within ±LOOKAHEAD_HOURS and close to now_local -> likely already local
        if abs(diff_hours_local) < 24:
            stats["no_tz_like_local"] += 1
            examples.append(("no_tz_local", start_raw, dt.strftime("%Y%m%d%H%M%S (assume local) -> %s" % (dt.strftime("%Y%m%d%H%M%S")+" +0800"))))
        elif abs(diff_hours_utc) < 24:
            stats["no_tz_like_utc"] += 1
            # show what it becomes if we treat as UTC and convert to +8
            dt_china = dt + timedelta(hours=8)
            examples.append(("no_tz_utc", start_raw, dt_china.strftime("%Y%m%d%H%M%S +0800")))
        else:
            stats["ambiguous"] += 1
            examples.append(("ambiguous", start_raw, "ambiguous"))
    return stats, examples

def decide_and_fix(root, do_fix=True):
    progs = root.findall("programme")
    if not progs:
        print("未找到 programme 元素，退出")
        return root, "no_programme"

    stats, examples = analyze_root(root)
    if stats is None:
        print("分析失败")
        return root, "analyze_failed"

    print("=== 分析结果（抽样） ===")
    for k,v in stats.items():
        print(f"{k}: {v}")
    print("\n部分示例（类型, 源时间, 转换/推断结果）：")
    for e in examples[:30]:
        print(e)

    # 决策规则（保守一点）：
    # - 如果大多数(no_tz_like_local) > no_tz_like_utc，则认为无时区字段时已经是本地时间 -> 不做转换
    # - 否则将无时区视为 UTC，需要 +8 转换
    no_tz_local = stats.get("no_tz_like_local",0)
    no_tz_utc = stats.get("no_tz_like_utc",0)
    with_tz = stats.get("with_tz",0)
    decision = None
    if no_tz_local + 0.0 > no_tz_utc + 0.0:
        decision = "source_no_tz_are_local"
    elif no_tz_utc > no_tz_local:
        decision = "source_no_tz_are_utc"
    elif with_tz > 0 and no_tz_utc == 0 and no_tz_local == 0:
        decision = "mostly_with_tz"
    else:
        # ambiguous fallback: if major part have tz -> honor tz, else assume local (保守)
        if with_tz > (no_tz_local + no_tz_utc):
            decision = "mostly_with_tz"
        else:
            decision = "ambiguous_assume_local"

    print("\n== 决策建议：", decision)

    if not do_fix:
        return root, decision

    # 执行修正：只有当决策显示 source_no_tz_are_utc 或 mostly_with_tz（且 tz 为 +0000）时，才进行 +8 修正
    converted = 0
    if decision in ("source_no_tz_are_utc", "mostly_with_tz"):
        for p in progs:
            for attr in ("start","stop"):
                t = p.get(attr)
                if not t:
                    continue
                dt, tz = parse_programme_time_attr(t)
                if dt is None:
                    continue
                if tz is None:
                    # treat as UTC and convert
                    new_dt = dt + timedelta(hours=8)
                    p.set(attr, new_dt.strftime("%Y%m%d%H%M%S") + " +0800")
                    converted += 1
                else:
                    # if tz != 8, normalize to +0800
                    if abs(tz - 8.0) > 0.01:
                        # compute UTC then to china
                        dt_utc = dt - timedelta(hours=tz)
                        dt_china = dt_utc + timedelta(hours=8)
                        p.set(attr, dt_china.strftime("%Y%m%d%H%M%S") + " +0800")
                        converted += 1
    else:
        print("按决策不做批量转换（保守模式）。如果你确认需要强制转换，请设置 do_fix=True 并调用 force_convert()。")

    print(f"\n已转换 {converted} 个时间属性（如果为0，说明没有需要转换的项）")
    return root, decision

def save_root(root, path="custom_debug_epg.xml"):
    rough = ET.tostring(root, encoding="utf-8")
    # minimal pretty
    with open(path, "wb") as f:
        f.write(rough)
    print("已保存到：", path)

if __name__ == "__main__":
    root = fetch_epg_root(EPG_URL)
    if not root:
        sys.exit(1)
    root_after, decision = decide_and_fix(root, do_fix=True)
    save_root(root_after, "custom_epg_epgpw_debug.xml")
    print("完成。决策:", decision)
    print("请检查 custom_epg_epgpw_debug.xml 的 program 元素 (start/stop) 是否已变为 ... +0800")
