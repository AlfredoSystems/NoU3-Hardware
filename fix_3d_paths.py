"""Rewrite broken 3D model paths in NoU3.kicad_pcb (run only while KiCad has the board CLOSED).

Usage:  python fix_pcb_3d_paths.py "C:/Users/Jacob/Documents/KiCad/NoU3-Hardware/NoU3.kicad_pcb"
Writes a backup next to the board (NoU3.kicad_pcb.bak-3dpaths) before touching it.
"""
import re, sys, shutil

ALF = "C:/Users/Jacob/Documents/KiCAD/KiCAD-Alfredo-Libraries/AlfredoFootprints.3dshapes"
# footprint name -> (new model path, offset xyz, rotate xyz)   offsets are baked into the STEPs, so all zero
FIX = {
    "AlfredoFootprints:USB_TYPE-C-31-M-12":          (f"{ALF}/USB_TYPE-C-31-M-12.step", "0 0 0", "0 0 0"),
    "AlfredoFootprints:TerminalBlock_Ningbo_2P_5mm": (f"{ALF}/TerminalBlock_Ningbo_2P_5mm.step", "0 0 0", "0 0 0"),
    "AlfredoFootprints:JST_SH_1x06_Vertical":        (f"{ALF}/JST_SH_1x06_Vertical.step", "0 0 0", "0 0 0"),
    "AlfredoFootprints:XKB5858-Z-75":                (f"{ALF}/XKB5858-Z-75.step", "0 0 0", "0 0 0"),
    "AlfredoFootprints:Button_SKRKAEE020":           (f"{ALF}/Button_SKRKAEE020.step", "0 0 0", "0 0 0"),
    "AlfredoFootprints:HR8833-0.6mm":                ("${KICAD10_3DMODEL_DIR}/Package_SO.3dshapes/HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm.step", "0 0 0", "0 0 0"),
    "AlfredoFootprints:LVF252A12":                   ("${KICAD10_3DMODEL_DIR}/Inductor_SMD.3dshapes/L_1008_2520Metric.step", None, None),
    "Package_DFN_QFN:VQFN-32-1EP_5x5mm_P0.5mm_EP3.5x3.5mm": ("${KICAD10_3DMODEL_DIR}/Package_DFN_QFN.3dshapes/QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm.step", None, None),
    "RF_Module:ESP32-S2-MINI-1":                     ("${KIPRJMOD}/3dmodels/ESP32-S3-MINI-1.step", None, None),
}

pcb = sys.argv[1]
raw = open(pcb, encoding="utf-8").read()
shutil.copy(pcb, pcb + ".bak-3dpaths")

def patch_footprint(m):
    name, body = m.group(1), m.group(2)
    if name not in FIX:
        return m.group(0)
    path, off, rot = FIX[name]
    def fix_model(mm):
        s = re.sub(r'\(model "[^"]*"', f'(model "{path}"', mm.group(0), count=1)
        if off is not None:
            s = re.sub(r'\(offset\s*\(xyz [^)]*\)\s*\)', f'(offset\n\t\t\t\t(xyz {off})\n\t\t\t)', s, count=1)
            s = re.sub(r'\(rotate\s*\(xyz [^)]*\)\s*\)', f'(rotate\n\t\t\t\t(xyz {rot})\n\t\t\t)', s, count=1)
        return s
    new_body, n = re.subn(r'\(model "[^"]*"(?:[^()]|\([^()]*(?:\([^()]*\)[^()]*)*\))*\)', fix_model, body)
    counts[name] = counts.get(name, 0) + n
    return f'\n\t(footprint "{name}"{new_body}\n\t)'

counts = {}
# lookahead for the trailing newline so back-to-back footprints are all matched
out = re.sub(r'\n\t\(footprint "([^"]+)"(.*?)\n\t\)(?=\n)', patch_footprint, raw, flags=re.S)
total_fp = len(re.findall(r'^\t\(footprint "', raw, flags=re.M))
print(f"{total_fp} footprints scanned")
open(pcb, "w", encoding="utf-8", newline="\n").write(out)
for k, v in counts.items():
    print(f"{v:3d} model path(s) fixed in {k}")
print("done; backup at", pcb + ".bak-3dpaths")
