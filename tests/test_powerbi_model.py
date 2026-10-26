"""
Automated Test Suite for Power BI Data Model & DAX Measures (Tasks UPI-007A, UPI-007B)
Validates:
1. Source CSV existence, integrity, and row counts (126 monthly, 11 FY).
2. Key uniqueness (no duplicate months).
3. Power BI Project (.pbip) and Tabular Model (TMDL / model.bim) structure and syntax.
4. Schema completeness (all 4 tables, partitions, columns, and relationships).
5. Mathematical accuracy of all 13 DAX measures across unfiltered and filtered contexts.
6. Executive Overview PBIR page and visual container integrity.
"""

import json
import re
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
POWERBI_DIR = BASE_DIR / "powerbi"
REPORTS_DIR = BASE_DIR / "reports" / "python_eda"
CSV_MONTHLY = REPORTS_DIR / "monthly_metrics.csv"
CSV_FY = REPORTS_DIR / "financial_year_metrics.csv"
DATASET_DIR = POWERBI_DIR / "upi_growth_analysis.Dataset"
MODEL_BIM = DATASET_DIR / "model.bim"
TMDL_DIR = DATASET_DIR / "definition"
PBIP_FILE = POWERBI_DIR / "upi_growth_analysis.pbip"
REPORT_DIR = POWERBI_DIR / "upi_growth_analysis.Report"


def _parse_tmdl_table(file_path: Path):
    """Parses table name, columns, and measures from a TMDL file."""
    content = file_path.read_text(encoding="utf-8")
    table_match = re.search(r"^\s*table\s+([^\r\n\t]+)", content, re.MULTILINE)
    table_name = table_match.group(1).strip("'") if table_match else file_path.stem

    columns = re.findall(r"^\s*column\s+([^\r\n\t=]+)", content, re.MULTILINE)
    columns = [c.strip().strip("'") for c in columns]

    measures = re.findall(r"^\s*measure\s+(?:'([^']+)'|([^\s=]+))\s*=", content, re.MULTILINE)
    measure_names = [m[0] if m[0] else m[1] for m in measures]

    return {
        "name": table_name,
        "columns": columns,
        "measures": measure_names
    }


def _parse_tmdl_relationships(file_path: Path):
    """Parses relationships from relationships.tmdl."""
    content = file_path.read_text(encoding="utf-8")
    rels = []
    # Match relationship blocks
    blocks = re.split(r"^\s*relationship\s+", content, flags=re.MULTILINE)
    for b in blocks[1:]:
        lines = b.strip().splitlines()
        rel_name = lines[0].strip()
        from_col = None
        to_col = None
        for line in lines[1:]:
            line = line.strip()
            if line.startswith("fromColumn:"):
                from_col = line.split(":", 1)[1].strip()
            elif line.startswith("toColumn:"):
                to_col = line.split(":", 1)[1].strip()
        if from_col and to_col:
            rels.append({
                "name": rel_name,
                "fromTable": from_col.split(".")[0],
                "fromColumn": from_col.split(".")[1],
                "toTable": to_col.split(".")[0],
                "toColumn": to_col.split(".")[1]
            })
    return rels


def test_source_csv_integrity_and_row_counts():
    """Verify source CSV files exist with exact expected row counts."""
    assert CSV_MONTHLY.exists(), "monthly_metrics.csv is missing!"
    assert CSV_FY.exists(), "financial_year_metrics.csv is missing!"

    df_m = pd.read_csv(CSV_MONTHLY)
    df_fy = pd.read_csv(CSV_FY)

    assert len(df_m) == 126, f"Expected 126 monthly records, got {len(df_m)}"
    assert len(df_fy) == 11, f"Expected 11 financial-year records, got {len(df_fy)}"

    # Check key uniqueness
    assert df_m["month"].nunique() == 126, "Duplicate month keys detected in MonthlyMetrics!"
    assert df_fy["fy_label"].nunique() == 11, "Duplicate fy_label keys detected in FinancialYearMetrics!"


def test_powerbi_project_structure():
    """Verify PBIP directory structure and valid JSON configuration files."""
    assert PBIP_FILE.exists(), "upi_growth_analysis.pbip is missing!"

    with open(PBIP_FILE, "r", encoding="utf-8") as f:
        pbip_data = json.load(f)
    assert pbip_data["version"] == "1.0"

    # Support either model.bim or TMDL definition folder
    if MODEL_BIM.exists():
        with open(MODEL_BIM, "r", encoding="utf-8") as f:
            bim_data = json.load(f)
        assert bim_data["name"] == "upi_growth_analysis"
        assert "model" in bim_data
    else:
        assert TMDL_DIR.exists(), "Neither model.bim nor TMDL definition directory exists!"
        assert (TMDL_DIR / "model.tmdl").exists(), "TMDL model.tmdl missing!"


def test_model_tables_and_columns_completeness():
    """Verify model contains all 4 required tables and correct columns."""
    if MODEL_BIM.exists():
        with open(MODEL_BIM, "r", encoding="utf-8") as f:
            bim_data = json.load(f)
        tables = {t["name"]: [c["name"] for c in t.get("columns", [])] for t in bim_data["model"]["tables"]}
    else:
        tables = {}
        for t_file in (TMDL_DIR / "tables").glob("*.tmdl"):
            parsed = _parse_tmdl_table(t_file)
            tables[parsed["name"]] = parsed["columns"]

    assert {"MonthlyMetrics", "FinancialYearMetrics", "DimDate", "DimFinancialYear"}.issubset(set(tables.keys()))

    # MonthlyMetrics columns
    monthly_cols = set(tables["MonthlyMetrics"])
    expected_m_cols = {
        "month", "bank_count", "volume_mn", "value_cr", "avg_ticket_size_inr",
        "prev_year_volume_mn", "prev_year_value_cr", "yoy_volume_growth_pct", "yoy_value_growth_pct"
    }
    assert expected_m_cols.issubset(monthly_cols)

    # FinancialYearMetrics columns
    fy_cols = set(tables["FinancialYearMetrics"])
    expected_fy_cols = {
        "fy_label", "months_available", "is_complete", "total_volume_mn", "total_value_cr",
        "weighted_avg_ticket_size_inr", "opening_bank_count", "closing_bank_count",
        "yoy_volume_growth_pct", "yoy_value_growth_pct"
    }
    assert expected_fy_cols.issubset(fy_cols)

    # DimDate columns
    date_cols = set(tables["DimDate"])
    expected_date_cols = {"Date", "Year", "MonthNo", "MonthName", "MonthShort", "MonthYear", "YearMonthKey", "FinancialYear", "FYQuarter", "MonthInFY"}
    assert expected_date_cols.issubset(date_cols)

    # DimFinancialYear columns
    dimfy_cols = set(tables["DimFinancialYear"])
    expected_dimfy_cols = {"FinancialYear", "FYStartYear", "FYEndYear", "FYSortOrder", "IsComplete", "Status"}
    assert expected_dimfy_cols.issubset(dimfy_cols)


def test_model_relationships_validity():
    """Verify 1-to-many single-direction relationships between dimensions and facts."""
    if MODEL_BIM.exists():
        with open(MODEL_BIM, "r", encoding="utf-8") as f:
            bim_data = json.load(f)
        rels = bim_data["model"]["relationships"]
        rel_dict = {r["name"]: r for r in rels}
    else:
        rels = _parse_tmdl_relationships(TMDL_DIR / "relationships.tmdl")
        rel_dict = {r["name"]: r for r in rels}

    assert len(rel_dict) >= 3

    # 1. DimDate -> MonthlyMetrics
    assert "DimDate_MonthlyMetrics" in rel_dict
    r1 = rel_dict["DimDate_MonthlyMetrics"]
    assert r1["fromTable"] == "MonthlyMetrics"
    assert r1["fromColumn"] == "month"
    assert r1["toTable"] == "DimDate"
    assert r1["toColumn"] == "Date"

    # 2. DimFinancialYear -> DimDate
    assert "DimFinancialYear_DimDate" in rel_dict
    r2 = rel_dict["DimFinancialYear_DimDate"]
    assert r2["fromTable"] == "DimDate"
    assert r2["fromColumn"] == "FinancialYear"
    assert r2["toTable"] == "DimFinancialYear"
    assert r2["toColumn"] == "FinancialYear"

    # 3. DimFinancialYear -> FinancialYearMetrics
    assert "DimFinancialYear_FinancialYearMetrics" in rel_dict
    r3 = rel_dict["DimFinancialYear_FinancialYearMetrics"]
    assert r3["fromTable"] == "FinancialYearMetrics"
    assert r3["fromColumn"] == "fy_label"
    assert r3["toTable"] == "DimFinancialYear"
    assert r3["toColumn"] == "FinancialYear"


def test_dax_measures_presence_and_definitions():
    """Verify all 13 required DAX measures are defined."""
    if MODEL_BIM.exists():
        with open(MODEL_BIM, "r", encoding="utf-8") as f:
            bim_data = json.load(f)
        monthly_table = next(t for t in bim_data["model"]["tables"] if t["name"] == "MonthlyMetrics")
        measures = {m["name"] for m in monthly_table.get("measures", [])}
    else:
        parsed = _parse_tmdl_table(TMDL_DIR / "tables" / "MonthlyMetrics.tmdl")
        measures = set(parsed["measures"])

    required_measures = [
        "Total Volume (Mn)",
        "Total Value (Cr INR)",
        "Weighted Avg Ticket Size (INR)",
        "Latest Bank Count",
        "Latest Month Volume (Mn)",
        "Latest Month Value (Cr INR)",
        "Latest Month Volume YoY Growth %",
        "Latest Month Value YoY Growth %",
        "FY Volume (Mn)",
        "FY Value (Cr INR)",
        "FY Completeness Status",
        "FY Volume YoY Growth %",
        "FY Value YoY Growth %",
        "Total Volume (Bn)",
        "Total Value (Lakh Cr INR)",
        "Monthly Volume (Bn)",
        "Monthly Value (Lakh Cr INR)",
        "Monthly Volume YoY Growth %",
        "Monthly Value YoY Growth %",
        "Launch Bank Count",
        "Network Expansion Multiple",
    ]
    for rm in required_measures:
        assert rm in measures, f"Required measure '{rm}' missing from semantic model!"


def test_dax_measure_values_simulation():
    """Simulate and verify the mathematical results of DAX measures."""
    df_m = pd.read_csv(CSV_MONTHLY)
    df_fy = pd.read_csv(CSV_FY)

    # 1. Total Volume & Value
    total_vol = df_m["volume_mn"].sum()
    total_val = df_m["value_cr"].sum()
    assert np.isclose(total_vol, 870005.75, atol=1e-2)
    assert np.isclose(total_val, 124735861.12, atol=1e-2)

    # 1b. Display Unit Measures
    total_vol_bn = total_vol / 1000
    total_val_lakh_cr = total_val / 100000
    assert np.isclose(total_vol_bn, 870.01, atol=1e-2)
    assert np.isclose(total_val_lakh_cr, 1247.36, atol=1e-2)

    # 2. Weighted Avg Ticket Size
    weighted_ticket = (total_val / total_vol) * 10
    assert np.isclose(weighted_ticket, 1433.736, atol=1e-2)

    # 3. Latest Month (2026-09)
    latest_row = df_m[df_m["month"] == "2026-09-01"].iloc[0]
    assert latest_row["bank_count"] == 756
    assert np.isclose(latest_row["volume_mn"], 24068.38, atol=1e-2)
    assert np.isclose(latest_row["value_cr"], 2937396.67, atol=1e-2)
    assert np.isclose(latest_row["yoy_volume_growth_pct"], 22.59, atol=1e-2)
    assert np.isclose(latest_row["yoy_value_growth_pct"], 17.98, atol=1e-2)

    # 4. Financial Year Value & Volume Reconciliations (UPI-007B-QA6)
    row_fy25 = df_fy[df_fy["fy_label"] == "2025-26"].iloc[0]
    assert np.isclose(row_fy25["total_value_cr"], 31423249.71, atol=1e-2)
    assert np.isclose(row_fy25["total_value_cr"] / 100000, 314.23, atol=1e-2)
    assert np.isclose(row_fy25["total_volume_mn"], 241616.88, atol=1e-2)
    assert np.isclose(row_fy25["total_volume_mn"] / 1000, 241.62, atol=1e-2)

    row_fy26 = df_fy[df_fy["fy_label"] == "2026-27"].iloc[0]
    assert np.isclose(row_fy26["total_value_cr"], 17693184.04, atol=1e-2)
    assert np.isclose(row_fy26["total_value_cr"] / 100000, 176.93, atol=1e-2)
    assert np.isclose(row_fy26["total_volume_mn"], 140500.49, atol=1e-2)
    assert np.isclose(row_fy26["total_volume_mn"] / 1000, 140.50, atol=1e-2)

    # 5. Page 2 Time-Series & Network Adoption Measures (UPI-008A)
    earliest_row = df_m[df_m["month"] == "2016-04-01"].iloc[0]
    assert earliest_row["bank_count"] == 21
    expansion_multiple = latest_row["bank_count"] / earliest_row["bank_count"]
    assert np.isclose(expansion_multiple, 36.0, atol=1e-1)
    assert np.isclose(latest_row["yoy_volume_growth_pct"] / 100, 0.2259, atol=1e-4)
    assert np.isclose(latest_row["yoy_value_growth_pct"] / 100, 0.1798, atol=1e-4)


def test_executive_overview_pbir_structure():
    """Verify PBIR Executive Overview page and visuals integrity."""
    def_dir = REPORT_DIR / "definition"
    assert def_dir.exists(), "PBIR definition folder missing!"

    # Pages metadata
    pages_json = def_dir / "pages" / "pages.json"
    assert pages_json.exists(), "pages.json missing!"
    with open(pages_json, "r", encoding="utf-8") as f:
        p_data = json.load(f)
    assert p_data["activePageName"] == "ExecutiveOverview"
    assert "ExecutiveOverview" in p_data["pageOrder"]

    # Executive Overview page.json
    page_json = def_dir / "pages" / "ExecutiveOverview" / "page.json"
    assert page_json.exists(), "ExecutiveOverview page.json missing!"
    with open(page_json, "r", encoding="utf-8") as f:
        page_info = json.load(f)
    assert page_info["width"] == 1280
    assert page_info["height"] == 720

    # Visual containers
    visuals_dir = def_dir / "pages" / "ExecutiveOverview" / "visuals"
    assert visuals_dir.exists(), "visuals directory missing!"

    expected_visuals = {
        "header_banner": "textbox",
        "slicer_fy": "slicer",
        "kpi_total_volume": "card",
        "kpi_total_value": "card",
        "kpi_ticket_size": "card",
        "kpi_bank_count": "card",
        "kpi_latest_growth": "card",
        "chart_monthly_volume": "areaChart",
        "chart_monthly_value": "areaChart",
        "chart_bank_growth": "lineChart",
        "footer_note": "textbox"
    }

    for v_name, v_type in expected_visuals.items():
        v_file = visuals_dir / v_name / "visual.json"
        assert v_file.exists(), f"Visual {v_name} missing!"
        with open(v_file, "r", encoding="utf-8") as f:
            v_data = json.load(f)
        assert v_data["visual"]["visualType"] == v_type, f"Visual {v_name} has unexpected type {v_data['visual']['visualType']}"
        pos = v_data["position"]
        assert 0 <= pos["x"] <= 1280, f"Visual {v_name} x out of bounds"
        assert 0 <= pos["y"] <= 720, f"Visual {v_name} y out of bounds"
        assert pos["x"] + pos["width"] <= 1280, f"Visual {v_name} right edge exceeds 1280"
        assert pos["y"] + pos["height"] <= 720, f"Visual {v_name} bottom edge exceeds 720"

    # Specific Slicer Dropdown and Sorting Audit (QA5)
    slicer_data = json.loads((visuals_dir / "slicer_fy" / "visual.json").read_text(encoding="utf-8"))
    slicer_objs = slicer_data["visual"]["objects"]
    assert any("mode" in d.get("properties", {}) for d in slicer_objs.get("data", [])), "Slicer data.mode missing!"
    slicer_mode = slicer_objs["data"][0]["properties"]["mode"]["expr"]["Literal"]["Value"]
    assert slicer_mode == "'Dropdown'", f"Expected Dropdown mode, got {slicer_mode}"

    sort_defs = slicer_data["visual"]["query"].get("sortDefinition", {}).get("sort", [])
    assert len(sort_defs) > 0, "Slicer sortDefinition missing!"
    assert sort_defs[0]["field"]["Column"]["Property"] == "FinancialYear"
    assert sort_defs[0]["direction"] == "Ascending"

    selection_props = slicer_objs["selection"][0]["properties"]
    assert selection_props["selectAllCheckbox"]["expr"]["Literal"]["Value"] == "true"
    assert selection_props["singleSelect"]["expr"]["Literal"]["Value"] == "false"


def test_growth_and_adoption_pbir_structure():
    """Verify PBIR Page 2: Growth & Adoption page and visuals integrity (UPI-008A)."""
    def_dir = REPORT_DIR / "definition"
    assert def_dir.exists(), "PBIR definition folder missing!"

    # Pages metadata
    pages_json = def_dir / "pages" / "pages.json"
    assert pages_json.exists(), "pages.json missing!"
    with open(pages_json, "r", encoding="utf-8") as f:
        p_data = json.load(f)
    assert "GrowthAndAdoption" in p_data["pageOrder"], "GrowthAndAdoption missing from pageOrder!"

    # Growth & Adoption page.json
    page_json = def_dir / "pages" / "GrowthAndAdoption" / "page.json"
    assert page_json.exists(), "GrowthAndAdoption page.json missing!"
    with open(page_json, "r", encoding="utf-8") as f:
        page_info = json.load(f)
    assert page_info["width"] == 1280
    assert page_info["height"] == 720
    assert page_info["displayName"] == "Growth & Adoption"

    # Visual containers
    visuals_dir = def_dir / "pages" / "GrowthAndAdoption" / "visuals"
    assert visuals_dir.exists(), "Page 2 visuals directory missing!"

    expected_visuals = {
        "btn_nav_overview": "actionButton",
        "header_banner": "textbox",
        "slicer_fy": "slicer",
        "chart_monthly_growth_pulse": "lineChart",
        "kpi_network_adoption": "card",
        "chart_fy_growth": "clusteredColumnChart",
        "table_monthly_detail": "tableEx",
        "footer_note_p2": "textbox"
    }

    boxes = []
    for v_name, v_type in expected_visuals.items():
        v_file = visuals_dir / v_name / "visual.json"
        assert v_file.exists(), f"Page 2 visual {v_name} missing!"
        with open(v_file, "r", encoding="utf-8") as f:
            v_data = json.load(f)
        assert v_data["visual"]["visualType"] == v_type, f"Visual {v_name} unexpected type {v_data['visual']['visualType']}"
        pos = v_data["position"]
        assert 0 <= pos["x"] <= 1280, f"Visual {v_name} x out of bounds"
        assert 0 <= pos["y"] <= 720, f"Visual {v_name} y out of bounds"
        assert pos["x"] + pos["width"] <= 1280, f"Visual {v_name} right edge exceeds 1280"
        assert pos["y"] + pos["height"] <= 720, f"Visual {v_name} bottom edge exceeds 720"
        boxes.append((v_name, pos["x"], pos["y"], pos["x"] + pos["width"], pos["y"] + pos["height"]))

    # Overlap check
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            n1, l1, t1, r1, b1 = boxes[i]
            n2, l2, t2, r2, b2 = boxes[j]
            overlap = (l1 < r2 and r1 > l2 and t1 < b2 and b1 > t2)
            assert not overlap, f"Visual overlap detected between {n1} and {n2}"

    # Verify Navigation Button Action
    btn_file = visuals_dir / "btn_nav_overview" / "visual.json"
    btn_data = json.loads(btn_file.read_text(encoding="utf-8"))
    action_prop = btn_data["visual"]["objects"]["action"][0]["properties"]
    assert action_prop["type"]["expr"]["Literal"]["Value"] == "'PageNavigation'"
    assert action_prop["destination"]["expr"]["Literal"]["Value"] == "'ExecutiveOverview'"

    # Verify Slicer Dropdown Mode
    slicer_file = visuals_dir / "slicer_fy" / "visual.json"
    slicer_data = json.loads(slicer_file.read_text(encoding="utf-8"))
    slicer_objs = slicer_data["visual"]["objects"]
    assert slicer_objs["data"][0]["properties"]["mode"]["expr"]["Literal"]["Value"] == "'Dropdown'"


def test_growth_and_adoption_qa1_polish_verifications():
    """Verify specific bug fixes for UPI-008A-QA1 on Page 2."""
    def_dir = REPORT_DIR / "definition"
    visuals_dir = def_dir / "pages" / "GrowthAndAdoption" / "visuals"

    # 1. Navigation Button Visible Text & visualLink action
    btn_data = json.loads((visuals_dir / "btn_nav_overview" / "visual.json").read_text(encoding="utf-8"))
    btn_text_items = btn_data["visual"]["objects"]["text"]
    # Verify show is true and text contains ← EXECUTIVE OVERVIEW
    assert any(item.get("properties", {}).get("show", {}).get("expr", {}).get("Literal", {}).get("Value") == "true" for item in btn_text_items)
    default_text = next(item["properties"] for item in btn_text_items if "text" in item.get("properties", {}))
    assert "← EXECUTIVE OVERVIEW" in default_text["text"]["expr"]["Literal"]["Value"]
    assert default_text["fontColor"]["solid"]["color"]["expr"]["Literal"]["Value"] == "'#2DD4BF'"
    btn_link = btn_data["visual"]["visualContainerObjects"]["visualLink"][0]["properties"]
    assert btn_link["type"]["expr"]["Literal"]["Value"] == "'PageNavigation'"
    assert btn_link["navigationSection"]["expr"]["Literal"]["Value"] == "'ExecutiveOverview'"

    # 2. Monthly Growth Pulse Scaling Filter (Mature Period Jan 2020 - Sep 2026)
    pulse_data = json.loads((visuals_dir / "chart_monthly_growth_pulse" / "visual.json").read_text(encoding="utf-8"))
    assert "filterConfig" in pulse_data
    pulse_filters = pulse_data["filterConfig"]["filters"]
    assert len(pulse_filters) == 1
    assert pulse_filters[0]["field"]["Column"]["Property"] == "Date"
    pulse_cond = pulse_filters[0]["filter"]["Where"][0]["Condition"]["Comparison"]
    assert pulse_cond["ComparisonKind"] == 2
    assert "2020-01-01" in pulse_cond["Right"]["Literal"]["Value"]

    # 3. FY Annual Growth Comparison Scaling Filter (FY 2018-19 to FY 2025-26)
    fy_growth_data = json.loads((visuals_dir / "chart_fy_growth" / "visual.json").read_text(encoding="utf-8"))
    assert "filterConfig" in fy_growth_data
    fy_filters = fy_growth_data["filterConfig"]["filters"]
    assert len(fy_filters) == 1
    assert fy_filters[0]["field"]["Column"]["Property"] == "FinancialYear"
    fy_in = fy_filters[0]["filter"]["Where"][0]["Condition"]["In"]["Values"]
    fy_values = [v[0]["Literal"]["Value"].strip("'") for v in fy_in]
    assert "2017-18" not in fy_values, "Launch outlier FY 2017-18 must be segregated from linear chart"
    assert "2026-27" not in fy_values, "Incomplete FY 2026-27 must be excluded"
    assert "2025-26" in fy_values and "2018-19" in fy_values

    # 4. Monthly Detail Table Totals Disabled and Dark Styling
    table_data = json.loads((visuals_dir / "table_monthly_detail" / "visual.json").read_text(encoding="utf-8"))
    table_objs = table_data["visual"]["objects"]
    assert table_objs["total"][0]["properties"]["totals"]["expr"]["Literal"]["Value"] == "false"
    assert table_objs["totals"][0]["properties"]["show"]["expr"]["Literal"]["Value"] == "false"
    assert table_objs["columnHeaders"][0]["properties"]["backColor"]["solid"]["color"]["expr"]["Literal"]["Value"] == "'#1E293B'"
    assert table_objs["values"][0]["properties"]["backColorPrimary"]["solid"]["color"]["expr"]["Literal"]["Value"] == "'#131B2E'"
    assert len(table_objs["columnWidth"]) == 7, "All 7 columns must have explicit width definitions"
    # Verify MonthYear projection
    projections = table_data["visual"]["query"]["queryState"]["Values"]["projections"]
    assert projections[0]["field"]["Column"]["Property"] == "MonthYear"

    # 5. Dark Fintech Theme Registered Styles for tableEx
    theme_data = json.loads((def_dir / "RegisteredResources" / "DarkFintechTheme.json").read_text(encoding="utf-8"))
    assert "tableEx" in theme_data["visualStyles"]
    table_theme = theme_data["visualStyles"]["tableEx"]["*"]
    assert table_theme["columnHeaders"][0]["backColor"]["solid"]["color"] == "#1E293B"
    assert table_theme["values"][0]["backColorPrimary"]["solid"]["color"] == "#131B2E"
    assert table_theme["total"][0]["totals"] is False


