import sys
import xml.etree.ElementTree as ET

src, out = sys.argv[1], sys.argv[2]

tree = ET.parse(src)
root = tree.getroot()

UUID_TO_MENA = {
    "5824C394-7211-4004-AC46-35BD58B9D1EE": "beINSports1.qa@MENA",
    "90E69FC7-AA8C-40F2-B35F-EBD174495F76": "beINSports3.qa@MENA",
    "D0546ED7-9DB2-4924-9E32-C4F077E7BFC7": "beINSports4.qa@MENA",
    "A5A48DB1-C00B-4DB9-9FC6-5E5F25C18830": "beINSports5.qa@MENA",
    "E56B0905-F99F-4DB1-931E-E6002B530867": "beINSports6.qa@MENA",
    "831591C8-DA65-4528-B837-0E5A147887FB": "beINSports7.qa@MENA",
    "9A424246-EC89-43C3-9239-AA3A40540F94": "beINSports8.qa@MENA",
    "1ACADCF1-DFAC-480B-872C-53D51FE1B45D": "beINSportsXtra1.qa@SD"
}

fixed = 0
for p in root.findall("programme"):
    cid = p.get("channel")
    if cid in UUID_TO_MENA:
        p.set("channel", UUID_TO_MENA[cid])
        fixed += 1

tree.write(out, encoding="utf-8", xml_declaration=True)
print(f"Relinked {fixed} programmes →", out)
