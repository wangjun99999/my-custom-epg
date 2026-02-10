import xml.etree.ElementTree as ET
import sys

epg_in = sys.argv[1]      # sites epg (UUID channels)
map_file = sys.argv[2]   # channel map xml
epg_out = sys.argv[3]    # final epg

# 1. 读取映射：UUID -> [xmltv_id, xmltv_id, ...]
uuid_map = {}

tree = ET.parse(map_file)
root = tree.getroot()

for ch in root.findall("channel"):
    uuid = ch.get("site_id")
    xmltv = ch.get("xmltv_id")
    if uuid and xmltv:
        uuid_map.setdefault(uuid, []).append(xmltv)

print(f"Loaded {len(uuid_map)} UUID mappings")

# 2. 读取 EPG
epg_tree = ET.parse(epg_in)
tv = epg_tree.getroot()

new_programmes = []

for p in tv.findall("programme"):
    old = p.get("channel")
    if old in uuid_map:
        for new_id in uuid_map[old]:
            np = ET.fromstring(ET.tostring(p))
            np.set("channel", new_id)
            new_programmes.append(np)
    else:
        # 没映射的直接丢掉
        pass

# 3. 删除原有 programme
for p in tv.findall("programme"):
    tv.remove(p)

# 4. 写入新的 programme
for p in new_programmes:
    tv.append(p)

epg_tree.write(epg_out, encoding="utf-8", xml_declaration=True)

print("UUID relink done →", epg_out)
