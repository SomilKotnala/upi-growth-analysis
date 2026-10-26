import os
import json

PAGES_DIR = r"D:\upi-growth-analysis\powerbi\upi_growth_analysis.Report\definition\pages"
pages_json = os.path.join(PAGES_DIR, "pages.json")
with open(pages_json, "r", encoding="utf-8") as f:
    pages_meta = json.load(f)

page_order = pages_meta.get("pageOrder", [])
print(f"Auditing Report Pages: {page_order}\n" + "=" * 60)

all_clean = True
for page_name in page_order:
    vis_dir = os.path.join(PAGES_DIR, page_name, "visuals")
    if not os.path.exists(vis_dir):
        print(f"Page {page_name}: No visuals directory found!")
        continue

    visuals = []
    for d in os.listdir(vis_dir):
        p = os.path.join(vis_dir, d, "visual.json")
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                pos = data["position"]
                visuals.append({
                    "name": data["name"],
                    "type": data["visual"]["visualType"],
                    "x": pos["x"],
                    "y": pos["y"],
                    "w": pos["width"],
                    "h": pos["height"],
                    "right": pos["x"] + pos["width"],
                    "bottom": pos["y"] + pos["height"]
                })

    visuals.sort(key=lambda v: (v["y"], v["x"]))
    print(f"\n--- Page: {page_name} (Total Visuals: {len(visuals)}) ---")
    for v in visuals:
        print(f"{v['name']:<28} | {v['type']:<22} | x={v['x']:<4} y={v['y']:<4} w={v['w']:<5} h={v['h']:<4} | right={v['right']:<5} bottom={v['bottom']:<5}")

    overlaps = []
    for i in range(len(visuals)):
        for j in range(i + 1, len(visuals)):
            v1 = visuals[i]
            v2 = visuals[j]
            if (v1["x"] < v2["right"] and v1["right"] > v2["x"] and
                v1["y"] < v2["bottom"] and v1["bottom"] > v2["y"]):
                overlaps.append((v1["name"], v2["name"]))

    canvas_w, canvas_h = 1280, 720
    out_of_bounds = []
    for v in visuals:
        if v["x"] < 0 or v["y"] < 0 or v["right"] > canvas_w or v["bottom"] > canvas_h:
            out_of_bounds.append(v["name"])

    print("Overlaps detected:", overlaps if overlaps else "NONE (All bounding boxes strictly disjoint)")
    print("Out-of-bounds detected:", out_of_bounds if out_of_bounds else "NONE (All visuals within 1280x720)")
    if overlaps or out_of_bounds:
        all_clean = False

print("\n" + "=" * 60)
print("AUDIT RESULT:", "ALL PAGES CLEAN AND VALIDATED" if all_clean else "ERRORS DETECTED")
