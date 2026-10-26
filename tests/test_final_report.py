"""
test_final_report.py
Automated test suite for the redesigned portfolio-grade 3-page Power BI report:
`powerbi/upi_growth_analysis_final.pbip`
"""
import json
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

BASE_DIR = Path(r"D:\upi-growth-analysis")
POWERBI_DIR = BASE_DIR / "powerbi"
FINAL_PBIP = POWERBI_DIR / "upi_growth_analysis_final.pbip"
FINAL_REPORT_DIR = POWERBI_DIR / "upi_growth_analysis_final.Report"
FINAL_DATASET_DIR = POWERBI_DIR / "upi_growth_analysis_final.Dataset"
DEF_DIR = FINAL_REPORT_DIR / "definition"
PAGES_DIR = DEF_DIR / "pages"
REPORTS_DIR = BASE_DIR / "reports" / "python_eda"
CSV_MONTHLY = REPORTS_DIR / "monthly_metrics.csv"
CSV_FY = REPORTS_DIR / "financial_year_metrics.csv"


def test_final_project_structure():
    """Verify final PBIP project exists, points to final Dataset, and has correct pages."""
    assert FINAL_PBIP.exists(), "upi_growth_analysis_final.pbip is missing!"
    with open(FINAL_PBIP, "r", encoding="utf-8") as f:
        pbip_meta = json.load(f)
    assert pbip_meta["version"] == "1.0"

    pbir_file = FINAL_REPORT_DIR / "definition.pbir"
    assert pbir_file.exists(), "definition.pbir missing!"
    with open(pbir_file, "r", encoding="utf-8") as f:
        pbir_meta = json.load(f)
    assert "upi_growth_analysis_final.Dataset" in pbir_meta["datasetReference"]["byPath"]["path"]

    # Pages metadata
    pages_json = PAGES_DIR / "pages.json"
    assert pages_json.exists(), "pages.json missing!"
    with open(pages_json, "r", encoding="utf-8") as f:
        p_data = json.load(f)
    assert p_data["pageOrder"] == ["ExecutiveOverview", "GrowthAndAdoption", "FinancialYearPerformance"]
    assert p_data["activePageName"] == "ExecutiveOverview"

    # Version metadata
    version_json = DEF_DIR / "version.json"
    assert version_json.exists(), "definition/version.json missing in final report!"
    with open(version_json, "r", encoding="utf-8") as f:
        v_data = json.load(f)
    assert v_data["version"] == "2.0.0", f"Unexpected version in version.json: {v_data['version']}"
    assert "versionMetadata/1.0.0" in v_data["$schema"]

    # Platform properties
    platform_file = FINAL_REPORT_DIR / ".platform"
    assert platform_file.exists(), ".platform missing in final report!"
    with open(platform_file, "r", encoding="utf-8") as f:
        plat_data = json.load(f)
    assert plat_data["metadata"]["type"] == "Report"
    assert plat_data["metadata"]["displayName"] == "upi_growth_analysis_final"


def test_final_dax_measures_presence_and_values():
    """Verify TMDL measures and their mathematical evaluation."""
    tmdl_path = FINAL_DATASET_DIR / "definition" / "tables" / "MonthlyMetrics.tmdl"
    assert tmdl_path.exists(), "MonthlyMetrics.tmdl missing in final dataset!"
    content = tmdl_path.read_text(encoding="utf-8")

    expected_measures = [
        "Total Volume (Bn)",
        "Total Value (Lakh Cr INR)",
        "Weighted Avg Ticket Size (INR)",
        "Latest Bank Count",
        "Latest Month Volume YoY Growth %",
        "Latest Month Value YoY Growth %",
        "FY Volume (Bn)",
        "FY Value (Lakh Cr INR)",
        "FY Weighted Avg Ticket Size (INR)",
        "FY Closing Bank Count",
        "FY Opening Bank Count",
        "FY Months Available",
        "Network Expansion Multiple",
        "Scorecard FY Volume (Bn)",
        "Scorecard FY Value (Lakh Cr INR)",
        "Scorecard FY Weighted Avg Ticket Size (INR)",
        "Scorecard FY Closing Bank Count"
    ]
    for em in expected_measures:
        assert f"measure '{em}'" in content, f"Measure '{em}' missing in TMDL!"

    # Simulate calculations
    df_m = pd.read_csv(CSV_MONTHLY)
    df_fy = pd.read_csv(CSV_FY)

    # Cumulative Volume & Value
    tot_vol_bn = df_m["volume_mn"].sum() / 1000
    tot_val_lakh_cr = df_m["value_cr"].sum() / 100000
    weighted_ticket = (df_m["value_cr"].sum() / df_m["volume_mn"].sum()) * 10
    assert np.isclose(tot_vol_bn, 870.01, atol=1e-2)
    assert np.isclose(tot_val_lakh_cr, 1247.36, atol=1e-2)
    assert np.isclose(weighted_ticket, 1433.74, atol=1e-2)

    # FY 2025-26
    row_fy25 = df_fy[df_fy["fy_label"] == "2025-26"].iloc[0]
    assert np.isclose(row_fy25["total_volume_mn"] / 1000, 241.62, atol=1e-2)
    assert np.isclose(row_fy25["total_value_cr"] / 100000, 314.23, atol=1e-2)
    assert np.isclose(row_fy25["weighted_avg_ticket_size_inr"], 1300.54, atol=1e-2)
    assert row_fy25["closing_bank_count"] == 705

    # FY 2026-27 (Incomplete 6Mo)
    row_fy26 = df_fy[df_fy["fy_label"] == "2026-27"].iloc[0]
    assert np.isclose(row_fy26["total_volume_mn"] / 1000, 140.50, atol=1e-2)
    assert np.isclose(row_fy26["total_value_cr"] / 100000, 176.93, atol=1e-2)
    assert row_fy26["months_available"] == 6
    assert row_fy26["closing_bank_count"] == 756


def test_final_all_pages_geometry_and_disjointness():
    """Verify that every visual across all 3 pages has 0 overlaps and strictly fits 1280x720."""
    pages = ["ExecutiveOverview", "GrowthAndAdoption", "FinancialYearPerformance"]
    for page_name in pages:
        page_dir = PAGES_DIR / page_name
        vis_dir = page_dir / "visuals"
        assert vis_dir.exists(), f"Visuals directory missing for {page_name}"

        visuals = []
        for d in vis_dir.iterdir():
            if d.is_dir() and (d / "visual.json").exists():
                with open(d / "visual.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                pos = data["position"]
                visuals.append({
                    "name": data["name"],
                    "x": pos["x"],
                    "y": pos["y"],
                    "w": pos["width"],
                    "h": pos["height"],
                    "right": pos["x"] + pos["width"],
                    "bottom": pos["y"] + pos["height"]
                })

        assert len(visuals) >= 8, f"Page {page_name} has too few visuals ({len(visuals)})"

        # Check bounds
        for v in visuals:
            assert v["x"] >= 0, f"{page_name} / {v['name']} negative x: {v['x']}"
            assert v["y"] >= 0, f"{page_name} / {v['name']} negative y: {v['y']}"
            assert v["right"] <= 1280, f"{page_name} / {v['name']} exceeds canvas width: {v['right']} > 1280"
            assert v["bottom"] <= 720, f"{page_name} / {v['name']} exceeds canvas height: {v['bottom']} > 720"
            # Ensure safety margin from bottom
            assert v["bottom"] <= 714, f"{page_name} / {v['name']} bottom {v['bottom']} too close to edge"

        # Check disjointness (0 overlaps)
        for i in range(len(visuals)):
            for j in range(i + 1, len(visuals)):
                v1 = visuals[i]
                v2 = visuals[j]
                overlap = (v1["x"] < v2["right"] and v1["right"] > v2["x"] and
                           v1["y"] < v2["bottom"] and v1["bottom"] > v2["y"])
                assert not overlap, f"Overlap detected on page {page_name} between {v1['name']} and {v2['name']}"


def test_final_navigation_header_consistency():
    """Verify that all 3 pages feature the unified 3-button navigation header and dropdown slicer."""
    pages = [
        ("ExecutiveOverview", "btn_nav_p1"),
        ("GrowthAndAdoption", "btn_nav_p2"),
        ("FinancialYearPerformance", "btn_nav_p3")
    ]
    for page_name, active_btn in pages:
        vis_dir = PAGES_DIR / page_name / "visuals"
        # Check all 3 buttons present
        for b_name in ["btn_nav_p1", "btn_nav_p2", "btn_nav_p3"]:
            b_file = vis_dir / b_name / "visual.json"
            assert b_file.exists(), f"{b_name} missing on {page_name}"
            with open(b_file, "r", encoding="utf-8") as f:
                b_data = json.load(f)
            assert b_data["visual"]["visualType"] == "actionButton"
            action = b_data["visual"]["objects"]["action"][0]["properties"]
            assert action["type"]["expr"]["Literal"]["Value"] == "'PageNavigation'"
            link = b_data["visual"]["visualContainerObjects"]["visualLink"][0]["properties"]
            assert link["type"]["expr"]["Literal"]["Value"] == "'PageNavigation'"

            # Verify active styling
            text_items = b_data["visual"]["objects"]["text"]
            default_text = next(item["properties"] for item in text_items if "text" in item.get("properties", {}))
            if b_name == active_btn:
                assert default_text["fontColor"]["solid"]["color"]["expr"]["Literal"]["Value"] == "'#2DD4BF'"
            else:
                assert default_text["fontColor"]["solid"]["color"]["expr"]["Literal"]["Value"] == "'#CBD5E1'"

        # Check Slicer
        slicer_file = vis_dir / "slicer_fy" / "visual.json"
        assert slicer_file.exists(), f"slicer_fy missing on {page_name}"
        with open(slicer_file, "r", encoding="utf-8") as f:
            s_data = json.load(f)
        s_objs = s_data["visual"]["objects"]
        assert s_objs["data"][0]["properties"]["mode"]["expr"]["Literal"]["Value"] == "'Dropdown'"
        assert s_objs["selection"][0]["properties"]["selectAllCheckbox"]["expr"]["Literal"]["Value"] == "true"
        # Verify internal field caption FinancialYear is hidden
        assert s_objs["header"][0]["properties"]["show"]["expr"]["Literal"]["Value"] == "false"
        # Verify clean visible title FINANCIAL YEAR
        s_vco = s_data["visual"]["visualContainerObjects"]
        assert s_vco["title"][0]["properties"]["text"]["expr"]["Literal"]["Value"] == "'FINANCIAL YEAR'"
        # Verify dropdown styling properties
        assert s_objs["dropdown"][0]["properties"]["background"]["solid"]["color"]["expr"]["Literal"]["Value"] == "'#131B2E'"
        assert s_objs["dropdown"][0]["properties"]["borderColor"]["solid"]["color"]["expr"]["Literal"]["Value"] == "'#2A374E'"
        assert s_objs["items"][0]["properties"]["fontColor"]["solid"]["color"]["expr"]["Literal"]["Value"] == "'#F3F6FC'"
        # Verify height is 60px
        assert s_data["position"]["height"] == 60


def test_final_page3_scorecard_matrix():
    """Verify Page 3 Scorecard Matrix table structure, deliberate width (888px), and adjacent analytical panel."""
    vis_dir = PAGES_DIR / "FinancialYearPerformance" / "visuals"
    table_file = vis_dir / "table_fy_scorecard" / "visual.json"
    assert table_file.exists(), "table_fy_scorecard missing on Page 3!"
    with open(table_file, "r", encoding="utf-8") as f:
        t_data = json.load(f)

    assert t_data["position"]["width"] == 888, f"Expected table width 888px, got {t_data['position']['width']}"
    t_vis = t_data["visual"]
    assert t_vis["visualType"] == "tableEx"
    projections = t_vis["query"]["queryState"]["Values"]["projections"]
    assert len(projections) == 10, f"Expected 10 columns in scorecard matrix, got {len(projections)}"

    t_objs = t_vis["objects"]
    # Verify autoSizeColumnWidth is false
    assert t_objs["columnHeaders"][0]["properties"]["autoSizeColumnWidth"]["expr"]["Literal"]["Value"] == "false"
    # Verify totals disabled
    assert t_objs["total"][0]["properties"]["totals"]["expr"]["Literal"]["Value"] == "false"
    assert t_objs["totals"][0]["properties"]["show"]["expr"]["Literal"]["Value"] == "false"

    # Verify column widths sum to 888px (exact match to table width)
    col_widths = t_objs["columnWidth"]
    assert len(col_widths) == 10
    total_w = sum(float(c["properties"]["width"]["expr"]["Literal"]["Value"].replace("D", "")) for c in col_widths)
    assert np.isclose(total_w, 888.0, atol=1.0), f"Expected column width sum 888px, got {total_w}"

    # Verify adjacent analytical panel in freed space (x: 924, w: 332, h: 234)
    panel_file = vis_dir / "panel_fy_trajectory" / "visual.json"
    assert panel_file.exists(), "panel_fy_trajectory missing on Page 3!"
    with open(panel_file, "r", encoding="utf-8") as f:
        p_data = json.load(f)
    assert p_data["position"]["x"] == 924
    assert p_data["position"]["width"] == 332
    assert p_data["position"]["height"] == 234
    p_runs = p_data["visual"]["objects"]["general"][0]["properties"]["paragraphs"][0]["textRuns"]
    p_text = "".join(r["value"] for r in p_runs)
    assert "140.50 Bn" in p_text
    assert "₹176.93 Lakh Cr" in p_text
    assert "705" in p_text and "756" in p_text


def test_final_scorecard_kpi_cards_and_subtitles():
    """Verify Page 3 KPI cards use Scorecard measures and concise non-truncated subtitles."""
    vis_dir = PAGES_DIR / "FinancialYearPerformance" / "visuals"
    expected_kpis = {
        "kpi_fy_latest_vol": (
            "MonthlyMetrics.Scorecard FY Volume (Bn)",
            "ANNUAL VOLUME (BILLION)",
            "FY25–26: 241.62 Bn | FY26–27 H1: 140.50 Bn (6 mo)"
        ),
        "kpi_fy_latest_val": (
            "MonthlyMetrics.Scorecard FY Value (Lakh Cr INR)",
            "ANNUAL VALUE (LAKH CR)",
            "FY25–26: ₹314.23L Cr | FY26–27 H1: ₹176.93L Cr (6 mo)"
        ),
        "kpi_fy_ticket": (
            "MonthlyMetrics.Scorecard FY Weighted Avg Ticket Size (INR)",
            "AVG TICKET SIZE (INR)",
            "FY25–26: ₹1,300.54 | FY26–27 H1: ₹1,259.30"
        ),
        "kpi_fy_banks": (
            "MonthlyMetrics.Scorecard FY Closing Bank Count",
            "CLOSING MEMBER BANKS",
            "FY25–26 close: 705 | Sep 2026: 756"
        )
    }
    for kpi_name, (expected_measure, expected_title, expected_exact_sub) in expected_kpis.items():
        kpi_file = vis_dir / kpi_name / "visual.json"
        assert kpi_file.exists(), f"{kpi_name} missing on Page 3"
        with open(kpi_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        proj = data["visual"]["query"]["queryState"]["Values"]["projections"][0]
        assert proj["queryRef"] == expected_measure
        vco = data["visual"]["visualContainerObjects"]
        title_val = vco["title"][0]["properties"]["text"]["expr"]["Literal"]["Value"].replace("'", "")
        sub_val = vco["subTitle"][0]["properties"]["text"]["expr"]["Literal"]["Value"].replace("'", "")
        assert title_val == expected_title
        assert sub_val == expected_exact_sub, f"Expected exact subtitle '{expected_exact_sub}', got '{sub_val}'"

    # Verify Page 3 Chart subtitles (exact micro-fix strings)
    expected_chart_subs = {
        "chart_fy_volume": "FY16–17: 0.02 Bn | FY25–26: 241.62 Bn | FY26–27 H1: 140.50 Bn",
        "chart_fy_value": "FY16–17: ₹0.07L Cr | FY25–26: ₹314.23L Cr | FY26–27 H1: ₹176.93L Cr",
        "chart_fy_ticket_trend": "FY16–17: ₹3,892.58 | FY25–26: ₹1,300.54 | FY26–27 H1: ₹1,259.30"
    }
    for chart_name, expected_sub in expected_chart_subs.items():
        chart_file = vis_dir / chart_name / "visual.json"
        assert chart_file.exists(), f"{chart_name} missing on Page 3"
        with open(chart_file, "r", encoding="utf-8") as f:
            c_data = json.load(f)
        c_sub = c_data["visual"]["visualContainerObjects"]["subTitle"][0]["properties"]["text"]["expr"]["Literal"]["Value"].replace("'", "")
        assert c_sub == expected_sub, f"Expected exact chart subtitle '{expected_sub}', got '{c_sub}'"

    # Verify Page 3 footer has exact requested text and no scrollbar overflow
    footer_file = vis_dir / "footer_note_p3" / "visual.json"
    assert footer_file.exists(), "footer_note_p3 missing on Page 3"
    with open(footer_file, "r", encoding="utf-8") as f:
        f_data = json.load(f)
    f_text = f_data["visual"]["objects"]["general"][0]["properties"]["paragraphs"][0]["textRuns"][0]["value"]
    assert "Source: NPCI UPI statistics, Apr 2016–Sep 2026." in f_text
    assert "FY 2026–27 is partial (Apr–Sep, six months); incomplete-year YoY is withheld." in f_text



def test_final_page1_and_page2_polish_verifications():
    """Verify Page 1 factual precision and Page 2 table width allocation."""
    # Page 1 bank chart subtitle
    p1_vis = PAGES_DIR / "ExecutiveOverview" / "visuals"
    with open(p1_vis / "chart_bank_growth" / "visual.json", "r", encoding="utf-8") as f:
        bg_data = json.load(f)
    bg_sub = bg_data["visual"]["visualContainerObjects"]["subTitle"][0]["properties"]["text"]["expr"]["Literal"]["Value"]
    assert "Apr 2016" in bg_sub, f"Expected Apr 2016 in bank chart subtitle, got: {bg_sub}"

    # Page 1 key facts textbox
    with open(p1_vis / "textbox_facts" / "visual.json", "r", encoding="utf-8") as f:
        tf_data = json.load(f)
    runs = tf_data["visual"]["objects"]["general"][0]["properties"]["paragraphs"][1]["textRuns"]
    full_tf_text = "".join(r["value"] for r in runs)
    assert "Trillion equivalent" not in full_tf_text, "Found confusing Trillion equivalent text!"
    assert "micropayment" not in full_tf_text.lower(), "Found unsupported causal micropayment claim!"

    # Page 2 table column widths sum to 1232px
    p2_vis = PAGES_DIR / "GrowthAndAdoption" / "visuals"
    with open(p2_vis / "table_monthly_detail" / "visual.json", "r", encoding="utf-8") as f:
        t2_data = json.load(f)
    t2_widths = t2_data["visual"]["objects"]["columnWidth"]
    assert len(t2_widths) == 7
    total_w2 = sum(float(c["properties"]["width"]["expr"]["Literal"]["Value"].replace("D", "")) for c in t2_widths)
    assert np.isclose(total_w2, 1232.0, atol=1.0), f"Expected Page 2 table column width sum 1232px, got {total_w2}"

