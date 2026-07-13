#!/usr/bin/env python3
"""
Normalize image filenames under content/ for a Hugo static site.

Dry-run (default): prints every rename and deletion that would happen.
Execute (--execute): performs renames with git mv, deletions with git rm,
                     and updates all markdown references in index.md files.

Usage:
    python3 scripts/normalize_image_names.py            # dry-run
    python3 scripts/normalize_image_names.py --execute  # apply changes
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}

# ---------------------------------------------------------------------------
# Plan scope: the authoritative set of files covered by this batch.
# Only these files are processed in dry-run and execute mode.
# ---------------------------------------------------------------------------
PLAN_SCOPE: frozenset[str] = frozenset([
    # content/3d-prints/
    "content/3d-prints/3D_Printer_35.jpg",
    "content/3d-prints/3D_Printer_36.jpg",
    "content/3d-prints/3D_Printer_38.jpg",
    "content/3d-prints/3D_Printer_39.jpg",
    "content/3d-prints/3D_Printer_40.jpg",
    "content/3d-prints/3D_Printer_41.jpg",
    "content/3d-prints/3D_Printer_42.jpg",
    "content/3d-prints/3D_Printer_43.jpg",
    "content/3d-prints/3D_Printer_56.jpg",
    "content/3d-prints/3D_Printer_61.jpg",
    "content/3d-prints/3D_Printer_66.jpg",
    "content/3d-prints/3D_Printer_78.jpg",
    "content/3d-prints/3D_Printer_90.jpg",
    "content/3d-prints/3D_Printer_104.jpg",
    "content/3d-prints/3D_Printer_124.jpg",
    "content/3d-prints/3D_Printer_125.jpg",
    "content/3d-prints/3D_Printer_126.jpg",
    "content/3d-prints/3D_Printer_127.jpg",
    "content/3d-prints/3D_Printer_128.jpg",
    "content/3d-prints/3D_Printer_129.jpg",
    "content/3d-prints/3D_Printer_130.jpg",
    "content/3d-prints/3D_Printer_131.jpg",
    "content/3d-prints/3D_Printer_132.jpg",
    "content/3d-prints/P1270007.jpg",
    "content/3d-prints/P1270008.jpg",
    "content/3d-prints/dewalt-dust-shroud-01-scaled.jpg",
    # content/blog/2013-02-17-powered-subwoofers/
    "content/blog/2013-02-17-powered-subwoofers/powered-subwoofer-01-300x184.jpg",
    "content/blog/2013-02-17-powered-subwoofers/powered-subwoofer-08-1024x768.jpg",
    # content/blog/2014-01-05-subwoofer-for-car-and-house/
    "content/blog/2014-01-05-subwoofer-for-car-and-house/tube_subwoofer_01.jpg",
    "content/blog/2014-01-05-subwoofer-for-car-and-house/tube_subwoofer_02.jpg",
    "content/blog/2014-01-05-subwoofer-for-car-and-house/tube_subwoofer_03.jpg",
    # content/blog/2014-06-05-mazda2-subwoofer/
    "content/blog/2014-06-05-mazda2-subwoofer/mazda2-subwoofer-08-1024x683.jpg",
    # content/blog/2014-06-08-logitech-z340/
    "content/blog/2014-06-08-logitech-z340/Logitech-Z340-Mini-Din-Pinout.jpg",
    # content/blog/2014-07-07-scroll-wheel/
    "content/blog/2014-07-07-scroll-wheel/scroll-wheel-09-300x225.jpg",
    # content/blog/2014-10-20-cnc-summary/
    "content/blog/2014-10-20-cnc-summary/cnc_cnc_cut.jpg",
    "content/blog/2014-10-20-cnc-summary/cnc_computer_1.jpg",
    "content/blog/2014-10-20-cnc-summary/cnc_computer_2.jpg",
    "content/blog/2014-10-20-cnc-summary/cnc_coupler.jpg",
    "content/blog/2014-10-20-cnc-summary/cnc_driver.jpg",
    "content/blog/2014-10-20-cnc-summary/cnc_overall_1.jpg",
    "content/blog/2014-10-20-cnc-summary/cnc_overall_2.jpg",
    "content/blog/2014-10-20-cnc-summary/cnc_papers.jpg",
    "content/blog/2014-10-20-cnc-summary/cnc_parts.jpg",
    "content/blog/2014-10-20-cnc-summary/cnc_torsion-1024x768.jpg",
    "content/blog/2014-10-20-cnc-summary/cnc_x_backlash.jpg",
    "content/blog/2014-10-20-cnc-summary/cnc_x_motor.jpg",
    "content/blog/2014-10-20-cnc-summary/cnc_y_motor.jpg",
    "content/blog/2014-10-20-cnc-summary/cnc_z_gantry.jpg",
    # content/blog/2016-06-30-circuitmaker-shortcuts/
    "content/blog/2016-06-30-circuitmaker-shortcuts/PCBBackspace3.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/PCBCtrlA.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/PCBG.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/PCBR.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/PCBShiftS3.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/PCBShiftSpace2.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/PCBSpace2.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/PCBTab.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/SchC.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/SchCrtlTab.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/SchCtrlA.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/SchCtrlD.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/SchG.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/SchN.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/SchRotate.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/SchShiftSpace3.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/SchSpace2.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/SchT.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/SchTab.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/SchV.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/SchW.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/SchZ.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/shortcut_link.jpg",
    # content/blog/2016-07-08-kansas-i-70-vs-nebraska-i-80/
    "content/blog/2016-07-08-kansas-i-70-vs-nebraska-i-80/I-70.jpg",
    "content/blog/2016-07-08-kansas-i-70-vs-nebraska-i-80/I-80.jpg",
    "content/blog/2016-07-08-kansas-i-70-vs-nebraska-i-80/I70andI80.jpg",
    # content/blog/2016-08-21-motorcycle-brake-turn-light/
    "content/blog/2016-08-21-motorcycle-brake-turn-light/Brake-Light-1.jpg",
    "content/blog/2016-08-21-motorcycle-brake-turn-light/Brake-Light-2.jpg",
    "content/blog/2016-08-21-motorcycle-brake-turn-light/Brake-Light-3.jpg",
    "content/blog/2016-08-21-motorcycle-brake-turn-light/Brake-Light-4.jpg",
    "content/blog/2016-08-21-motorcycle-brake-turn-light/Brake-Light-5.jpg",
    # content/blog/2016-09-11-triangle-wave-generator/
    "content/blog/2016-09-11-triangle-wave-generator/triangle-wave-1.png",
    # content/blog/2016-12-04-how-to-check-lumix-lx100-shutter-count-graphic/
    "content/blog/2016-12-04-how-to-check-lumix-lx100-shutter-count-graphic/LX100-Check-Shutter-Count.jpg",
    "content/blog/2016-12-04-how-to-check-lumix-lx100-shutter-count-graphic/LX100-Check-Shutter-Count-2.jpg",
    # content/blog/2016-12-22-adding-18650s-to-video-light/
    "content/blog/2016-12-22-adding-18650s-to-video-light/Hot_Shoe_LED_Light_1.jpg",
    "content/blog/2016-12-22-adding-18650s-to-video-light/Hot_Shoe_LED_Light_3.jpg",
    "content/blog/2016-12-22-adding-18650s-to-video-light/Hot_Shoe_LED_Light_4.jpg",
    "content/blog/2016-12-22-adding-18650s-to-video-light/Hot_Shoe_LED_Light_6.jpg",
    "content/blog/2016-12-22-adding-18650s-to-video-light/Hot_Shoe_LED_Light_8.jpg",
    "content/blog/2016-12-22-adding-18650s-to-video-light/Hot_Shoe_LED_Light_9.jpg",
    # content/blog/2017-01-18-osprey-porter-46-vs-farpoint-40-side-by-side-photo-comparison/
    "content/blog/2017-01-18-osprey-porter-46-vs-farpoint-40-side-by-side-photo-comparison/osprey_porter_46_farpoint_40_1.jpg",
    "content/blog/2017-01-18-osprey-porter-46-vs-farpoint-40-side-by-side-photo-comparison/osprey_porter_46_farpoint_40_2.jpg",
    "content/blog/2017-01-18-osprey-porter-46-vs-farpoint-40-side-by-side-photo-comparison/osprey_porter_46_farpoint_40_3.jpg",
    "content/blog/2017-01-18-osprey-porter-46-vs-farpoint-40-side-by-side-photo-comparison/osprey_porter_46_farpoint_40_4.jpg",
    "content/blog/2017-01-18-osprey-porter-46-vs-farpoint-40-side-by-side-photo-comparison/osprey_porter_46_farpoint_40_5.jpg",
    "content/blog/2017-01-18-osprey-porter-46-vs-farpoint-40-side-by-side-photo-comparison/osprey_porter_46_farpoint_40_6.jpg",
    "content/blog/2017-01-18-osprey-porter-46-vs-farpoint-40-side-by-side-photo-comparison/osprey_porter_46_farpoint_40_7.jpg",
    "content/blog/2017-01-18-osprey-porter-46-vs-farpoint-40-side-by-side-photo-comparison/osprey_porter_46_farpoint_40_8.jpg",
    "content/blog/2017-01-18-osprey-porter-46-vs-farpoint-40-side-by-side-photo-comparison/osprey_porter_46_farpoint_40_9.jpg",
    "content/blog/2017-01-18-osprey-porter-46-vs-farpoint-40-side-by-side-photo-comparison/osprey_porter_46_farpoint_40_10.jpg",
    "content/blog/2017-01-18-osprey-porter-46-vs-farpoint-40-side-by-side-photo-comparison/osprey_porter_46_farpoint_40_11.jpg",
    "content/blog/2017-01-18-osprey-porter-46-vs-farpoint-40-side-by-side-photo-comparison/osprey_porter_46_farpoint_40_12.jpg",
    "content/blog/2017-01-18-osprey-porter-46-vs-farpoint-40-side-by-side-photo-comparison/osprey_porter_46_farpoint_40_13.jpg",
    "content/blog/2017-01-18-osprey-porter-46-vs-farpoint-40-side-by-side-photo-comparison/osprey_porter_46_farpoint_40_14.jpg",
    # content/blog/2017-02-21-lenovo-t450s-key-replacement/
    "content/blog/2017-02-21-lenovo-t450s-key-replacement/lenovo_t450s_key_replace_2.jpg",
    "content/blog/2017-02-21-lenovo-t450s-key-replacement/lenovo_t450s_key_replace_4.jpg",
    "content/blog/2017-02-21-lenovo-t450s-key-replacement/lenovo_t450s_key_replace_5.jpg",
    "content/blog/2017-02-21-lenovo-t450s-key-replacement/lenovo_t450s_key_replace_6.jpg",
    "content/blog/2017-02-21-lenovo-t450s-key-replacement/lenovo_t450s_key_replace_7.jpg",
    "content/blog/2017-02-21-lenovo-t450s-key-replacement/lenovo_t450s_key_replace_8.jpg",
    "content/blog/2017-02-21-lenovo-t450s-key-replacement/lenovo_t450s_key_replace_9.jpg",
    "content/blog/2017-02-21-lenovo-t450s-key-replacement/lenovo_t450s_key_replace_10.jpg",
    "content/blog/2017-02-21-lenovo-t450s-key-replacement/lenovo_t450s_key_replace_11.jpg",
    "content/blog/2017-02-21-lenovo-t450s-key-replacement/lenovo_t450s_key_replace_12.jpg",
    "content/blog/2017-02-21-lenovo-t450s-key-replacement/lenovo_t450s_key_replace_13.jpg",
    "content/blog/2017-02-21-lenovo-t450s-key-replacement/lenovo_t450s_key_replace_14.jpg",
    # content/blog/2017-03-15-making-cold-showers-a-habit/
    "content/blog/2017-03-15-making-cold-showers-a-habit/shower_1.jpg",
    # content/blog/2017-03-28-cheapest-sources-of-protein-calories-and-macros-comparison-tables/
    "content/blog/2017-03-28-cheapest-sources-of-protein-calories-and-macros-comparison-tables/hot_dogs_1.jpg",
    # content/blog/2017-04-04-tdk-trek-max-a34-teardown/
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_1.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_2.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_3.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_4.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_5.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_6.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_7.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_8.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_9-1024x685.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_10.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_11.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_12.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_13.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_14.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_15.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_16.jpg",
    "content/blog/2017-04-04-tdk-trek-max-a34-teardown/TDK_Trek_A34_17.jpg",
    # content/blog/2017-04-14-reflow-toaster-oven-build/
    "content/blog/2017-04-14-reflow-toaster-oven-build/Reflow_Oven_1.jpg",
    "content/blog/2017-04-14-reflow-toaster-oven-build/Reflow_Oven_2.jpg",
    "content/blog/2017-04-14-reflow-toaster-oven-build/Reflow_Oven_3.jpg",
    "content/blog/2017-04-14-reflow-toaster-oven-build/Reflow_Oven_4.jpg",
    "content/blog/2017-04-14-reflow-toaster-oven-build/Reflow_Oven_5.jpg",
    "content/blog/2017-04-14-reflow-toaster-oven-build/Reflow_Oven_6.jpg",
    "content/blog/2017-04-14-reflow-toaster-oven-build/Reflow_Oven_7.jpg",
    "content/blog/2017-04-14-reflow-toaster-oven-build/Reflow_Oven_8.jpg",
    "content/blog/2017-04-14-reflow-toaster-oven-build/Reflow_Oven_9.jpg",
    # content/blog/2017-04-22-make-your-own-pedialyte/
    "content/blog/2017-04-22-make-your-own-pedialyte/ORS_Recipe_1.jpg",
    "content/blog/2017-04-22-make-your-own-pedialyte/ORS_Recipe_2.jpg",
    "content/blog/2017-04-22-make-your-own-pedialyte/ORS_Recipe_3.jpg",
    # content/blog/2017-07-25-vientiane-laos-one-day/
    "content/blog/2017-07-25-vientiane-laos-one-day/IMG_20170708_105239.jpg",
    # content/blog/2017-08-24-chinese-visa-in-hanoi-vietnam/
    "content/blog/2017-08-24-chinese-visa-in-hanoi-vietnam/chinese_visa_1.jpg",
    "content/blog/2017-08-24-chinese-visa-in-hanoi-vietnam/chinese_visa_2.jpg",
    "content/blog/2017-08-24-chinese-visa-in-hanoi-vietnam/chinese_visa_3.jpg",
    "content/blog/2017-08-24-chinese-visa-in-hanoi-vietnam/chinese_visa_6.jpg",
    # content/blog/2017-09-25-zhangjiajie-park-map/
    "content/blog/2017-09-25-zhangjiajie-park-map/Zhangjiajie-National-Park-Map-1-1.jpg",
    "content/blog/2017-09-25-zhangjiajie-park-map/Zhangjiajie-National-Park-Map-2-1.jpg",
    # content/blog/2018-11-05-diy-prescription-dive-mask/
    "content/blog/2018-11-05-diy-prescription-dive-mask/scuba_goggles_1-1024x685.jpg",
    "content/blog/2018-11-05-diy-prescription-dive-mask/scuba_goggles_2-1024x685.jpg",
    "content/blog/2018-11-05-diy-prescription-dive-mask/scuba_goggles_3.jpg",
    "content/blog/2018-11-05-diy-prescription-dive-mask/scuba_goggles_4.jpg",
    # content/blog/2019-04-04-how-to-spot-a-counterfeit-motorola-razr-v3/
    "content/blog/2019-04-04-how-to-spot-a-counterfeit-motorola-razr-v3/Artboard-1.jpg",
    # content/blog/2020-05-11-nightlight-new-leds-and-pcb/
    "content/blog/2020-05-11-nightlight-new-leds-and-pcb/nightlight-01-1024x685.jpg",
    "content/blog/2020-05-11-nightlight-new-leds-and-pcb/nightlight-02-1024x685.jpg",
    "content/blog/2020-05-11-nightlight-new-leds-and-pcb/nightlight-03-1024x685.jpg",
    "content/blog/2020-05-11-nightlight-new-leds-and-pcb/nightlight-04-1024x685.jpg",
    # content/blog/2020-05-18-permanently-mounting-a-rearview-mirror/
    "content/blog/2020-05-18-permanently-mounting-a-rearview-mirror/rearview-mirror-01-1024x685.jpg",
    "content/blog/2020-05-18-permanently-mounting-a-rearview-mirror/rearview-mirror-02-1024x685.jpg",
    "content/blog/2020-05-18-permanently-mounting-a-rearview-mirror/rearview-mirror-03-1024x685.jpg",
    "content/blog/2020-05-18-permanently-mounting-a-rearview-mirror/rearview-mirror-04-1024x685.jpg",
    # content/blog/2023-03-11-london-good-delivery-bar-ingot-mold-drawings/
    "content/blog/2023-03-11-london-good-delivery-bar-ingot-mold-drawings/IMG_0431-scaled.jpg",
    # content/blog/2023-10-09-fabricating-a-frameless-cedar-gate/
    "content/blog/2023-10-09-fabricating-a-frameless-cedar-gate/frameless-gate-04-scaled.jpg",
    # content/projects/
    "content/projects/5V3AUPSR2_1.jpg",
    "content/projects/5V3AUPSR2_2.jpg",
    "content/projects/5V4AR1_1.jpg",
    "content/projects/5V4AR1_2.jpg",
    "content/projects/5V4AR1_3.jpg",
    "content/projects/Brake-Light-3.jpg",
    "content/projects/Brake-Light-4.jpg",
    "content/projects/Brake-Light-5.jpg",
    "content/projects/Reflow_Oven_4.jpg",
    "content/projects/Reflow_Oven_5.jpg",
    "content/projects/Reflow_Oven_6.jpg",
    "content/projects/Reflow_Oven_7.jpg",
    "content/projects/Reflow_Oven_8.jpg",
    "content/projects/cnc_computer_2.jpg",
    "content/projects/cnc_overall_2.jpg",
])

# ---------------------------------------------------------------------------
# Hardcoded overrides: relative path from repo root → new filename.
# Used for camera filenames, typo fixes, redundant-prefix removal, and other
# cases the algorithm cannot derive.
# ---------------------------------------------------------------------------
OVERRIDES: dict[str, str] = {
    # Camera filenames → descriptive names
    "content/3d-prints/P1270007.jpg": "3d-print-01.jpg",
    "content/3d-prints/P1270008.jpg": "3d-print-02.jpg",
    "content/blog/2017-07-25-vientiane-laos-one-day/IMG_20170708_105239.jpg": "vientiane-01.jpg",
    "content/blog/2023-03-11-london-good-delivery-bar-ingot-mold-drawings/IMG_0431-scaled.jpg":
        "london-ingot-mold-01.jpg",
    # Descriptive renames
    "content/blog/2019-04-04-how-to-spot-a-counterfeit-motorola-razr-v3/Artboard-1.jpg":
        "razr-v3-artboard.jpg",
    # Redundant prefix removal: cnc_cnc_cut → cnc-cut
    "content/blog/2014-10-20-cnc-summary/cnc_cnc_cut.jpg": "cnc-cut.jpg",
    # Zhangjiajie: trailing "-1" is redundant; title simplified
    "content/blog/2017-09-25-zhangjiajie-park-map/Zhangjiajie-National-Park-Map-1-1.jpg":
        "zhangjiajie-map-01.jpg",
    "content/blog/2017-09-25-zhangjiajie-park-map/Zhangjiajie-National-Park-Map-2-1.jpg":
        "zhangjiajie-map-02.jpg",
    # Typo fix: "Crtl" → "ctrl"
    "content/blog/2016-06-30-circuitmaker-shortcuts/SchCrtlTab.jpg": "sch-ctrl-tab.jpg",
    # CamelCase with embedded digits that don't decode algorithmically
    "content/blog/2016-07-08-kansas-i-70-vs-nebraska-i-80/I70andI80.jpg": "i-70-and-i-80.jpg",
}

# ---------------------------------------------------------------------------
# Files to delete (WP resize artefacts or unreferenced thumbnails).
# ---------------------------------------------------------------------------
FILES_TO_DELETE: list[str] = [
    "content/3d-prints/dewalt-dust-shroud-01-1024x768.jpg",
    "content/blog/2016-06-30-circuitmaker-shortcuts/CM-Shortcuts-Thumbnail-150x100.jpg",
]

# ---------------------------------------------------------------------------
# Markdown reference swaps required in specific index.md files.
# Applied in execute mode before the file containing the old name is deleted.
# ---------------------------------------------------------------------------
MD_REFERENCE_SWAPS: dict[str, dict[str, str]] = {
    "content/3d-prints/index.md": {
        "dewalt-dust-shroud-01-1024x768.jpg": "dewalt-dust-shroud-01.jpg",
    },
}


# ---------------------------------------------------------------------------
# Normalization algorithm
# ---------------------------------------------------------------------------

def camel_to_hyphen(name: str) -> str:
    """Convert CamelCase / PascalCase / all-caps-abbrev to hyphen-case.

    Returned string is already lowercased.

    Rules applied in order:
    1. lowercase → UPPERCASE transition  (e.g. shiftS  → shift-S)
    2. UPPERCASE-run → UPPERCASE+lowercase (e.g. PCBCtrl → PCB-Ctrl)
    3. UPPERCASE-run{2+} at end of string  (e.g. PCBG   → PCB-G)
    """
    s = re.sub(r'([a-z])([A-Z])', r'\1-\2', name)
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1-\2', s)
    s = re.sub(r'([A-Z]{2,})([A-Z])$', r'\1-\2', s)
    return s.lower()


def normalize_stem(stem: str) -> str:
    """Return the normalized version of a filename stem (without extension)."""
    # 1. CamelCase → hyphen-case (also lowercases)
    s = camel_to_hyphen(stem)
    # 2. Underscores → hyphens
    s = s.replace('_', '-')
    # 3. Strip WP size / thumbnail suffixes
    s = re.sub(r'-\d+x\d+$', '', s)
    s = re.sub(r'-thumbnail-\d+x\d+$', '', s)
    s = re.sub(r'-thumbnail$', '', s)
    s = re.sub(r'-scaled$', '', s)
    # 4. Zero-pad a single-digit number already preceded by a hyphen
    #    (e.g. brake-light-1 → brake-light-01).
    s = re.sub(r'-(\d)$', r'-0\1', s)
    # 5. Insert a hyphen between a trailing letter and its digit suffix when
    #    the digit was glued on via CamelCase (e.g. pcb-space2 → pcb-space-2).
    #    Only fires when the character immediately before the digits is a letter
    #    (not a hyphen), so it does not double-pad step-4 results.
    s = re.sub(r'([a-z])(\d+)$', r'\1-\2', s)
    # 6. Collapse multiple hyphens; strip leading/trailing
    s = re.sub(r'-+', '-', s)
    return s.strip('-')


def compute_new_name(rel: str, img_path: Path) -> str | None:
    """Return the new filename for *img_path*, or None if no rename is needed."""
    if rel in OVERRIDES:
        new_name = OVERRIDES[rel]
        return new_name if new_name != img_path.name else None
    new_stem = normalize_stem(img_path.stem)
    new_name = new_stem + img_path.suffix.lower()
    return new_name if new_name != img_path.name else None


# ---------------------------------------------------------------------------
# Build the rename list (scoped to PLAN_SCOPE)
# ---------------------------------------------------------------------------

def build_renames() -> list[tuple[Path, str]]:
    """Return sorted list of (old_path, new_filename) for all in-scope renames."""
    to_delete = {ROOT / p for p in FILES_TO_DELETE}
    renames: list[tuple[Path, str]] = []
    for rel in sorted(PLAN_SCOPE):
        img = ROOT / rel
        if not img.exists():
            continue
        if img in to_delete:
            continue
        new_name = compute_new_name(rel, img)
        if new_name is not None:
            renames.append((img, new_name))
    return renames


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------

def dry_run() -> None:
    renames = build_renames()

    print("=== Renames ===")
    for old, new in renames:
        print(f"  {old.relative_to(ROOT)} → {new}")

    print("\n=== Deletes ===")
    for p in FILES_TO_DELETE:
        exists = (ROOT / p).exists()
        marker = "" if exists else " [FILE NOT FOUND]"
        print(f"  DELETE {p}{marker}")

    # Sanity-check: report plan-scope entries that are missing on disk
    missing = [r for r in sorted(PLAN_SCOPE) if not (ROOT / r).exists()]
    if missing:
        print("\n=== PLAN SCOPE MISSING ON DISK ===")
        for r in missing:
            print(f"  {r}")

    # Conflict detection: multiple sources → same target path
    target_map: dict[Path, list[Path]] = {}
    for old, new in renames:
        target = old.parent / new
        target_map.setdefault(target, []).append(old)
    conflicts = {t: srcs for t, srcs in target_map.items() if len(srcs) > 1}
    if conflicts:
        print("\n=== CONFLICTS ===")
        for target, srcs in conflicts.items():
            print(f"  {target.relative_to(ROOT)} ← {[str(s.relative_to(ROOT)) for s in srcs]}")

    print(f"\nTotal renames: {len(renames)}")
    print(f"Total deletes: {len(FILES_TO_DELETE)}")


# ---------------------------------------------------------------------------
# Execute mode
# ---------------------------------------------------------------------------

def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def _update_md_references(md_path: Path, rename_map: dict[str, str]) -> None:
    """Replace all occurrences of old image filenames with new ones in *md_path*."""
    text = md_path.read_text(encoding="utf-8")
    changed = False
    for old_name, new_name in rename_map.items():
        if old_name in text:
            text = text.replace(old_name, new_name)
            changed = True
            print(f"  updated ref in {md_path.relative_to(ROOT)}: {old_name} → {new_name}")
    if changed:
        md_path.write_text(text, encoding="utf-8")


def execute() -> None:
    """Apply all renames (git mv), deletes (git rm), and markdown updates."""
    renames = build_renames()
    to_delete_paths = {ROOT / p for p in FILES_TO_DELETE}

    # Build per-directory reference-update map for markdown fixup.
    dir_rename_map: dict[Path, dict[str, str]] = {}
    for old, new in renames:
        d = old.parent
        dir_rename_map.setdefault(d, {})[old.name] = new
    # Add explicit swaps (e.g. dewalt 1024x768 → 01 before the 1024x768 file is deleted)
    for md_rel, swaps in MD_REFERENCE_SWAPS.items():
        md_path = ROOT / md_rel
        d = md_path.parent
        dir_rename_map.setdefault(d, {}).update(swaps)

    # Step 1: Update markdown references (index.md files + any other .md files)
    #         Do this before deletions so dead references are fixed first.
    for md in sorted(CONTENT.rglob("*.md")):
        d = md.parent
        swaps = dir_rename_map.get(d)
        if swaps:
            _update_md_references(md, swaps)

    # Step 2: git rm files to delete
    for p_rel in FILES_TO_DELETE:
        p = ROOT / p_rel
        if p.exists():
            print(f"  git rm {p_rel}")
            _run(["git", "rm", "-f", str(p)])
        else:
            print(f"  SKIP (not found): {p_rel}")

    # Step 3: git mv all renames; handle case where target already exists
    for old, new_name in renames:
        new_path = old.parent / new_name
        if new_path.exists() and new_path != old:
            # Target exists (e.g. non-scaled version alongside -scaled).
            # Remove the existing target so git mv can proceed.
            print(f"  git rm (existing target): {new_path.relative_to(ROOT)}")
            _run(["git", "rm", "-f", str(new_path)])
        print(f"  git mv {old.relative_to(ROOT)} → {new_name}")
        _run(["git", "mv", str(old), str(new_path)])

    print(f"\nDone. {len(renames)} renames, {len(FILES_TO_DELETE)} deletes.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    if "--execute" in sys.argv:
        execute()
    else:
        dry_run()


if __name__ == "__main__":
    main()
