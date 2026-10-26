"""
Power BI Data Model Builder for UPI Growth Analysis (Task UPI-007A)
Generates the complete Power BI Project (.pbip) semantic model, including:
- 4 Tables: MonthlyMetrics, FinancialYearMetrics, DimDate, DimFinancialYear
- Data Types, Format Strings, and M Partitions connecting to CSV outputs
- One-to-Many single-direction relationships
- 11 Core DAX Measures matching verified mathematical specifications
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports" / "python_eda"
POWERBI_DIR = BASE_DIR / "powerbi"
DATASET_DIR = POWERBI_DIR / "upi_growth_analysis.Dataset"
REPORT_DIR = POWERBI_DIR / "upi_growth_analysis.Report"

CSV_MONTHLY = (REPORTS_DIR / "monthly_metrics.csv").resolve()
CSV_FY = (REPORTS_DIR / "financial_year_metrics.csv").resolve()

# Escape backslashes for Power Query M strings
M_PATH_MONTHLY = str(CSV_MONTHLY).replace("\\", "\\\\")
M_PATH_FY = str(CSV_FY).replace("\\", "\\\\")


def build_model_bim() -> dict:
    """Construct TMSL/BIM JSON data model representation."""

    # ------------------------------------------------------------------------
    # 1. MonthlyMetrics Table
    # ------------------------------------------------------------------------
    m_expr_monthly = [
        "let",
        f'    Source = Csv.Document(File.Contents("{M_PATH_MONTHLY}"),[Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
        '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
        '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"month", type date}, {"bank_count", Int64.Type}, {"volume_mn", type number}, {"value_cr", type number}, {"avg_ticket_size_inr", type number}, {"prev_year_volume_mn", type number}, {"prev_year_value_cr", type number}, {"yoy_volume_growth_pct", type number}, {"yoy_value_growth_pct", type number}})',
        "in",
        '    #"Changed Type"'
    ]

    monthly_columns = [
        {"name": "month", "dataType": "dateTime", "formatString": "yyyy-MM-dd", "sourceColumn": "month", "summarizeBy": "none"},
        {"name": "bank_count", "dataType": "int64", "formatString": "#,##0", "sourceColumn": "bank_count", "summarizeBy": "none"},
        {"name": "volume_mn", "dataType": "double", "formatString": "#,##0.00", "sourceColumn": "volume_mn", "summarizeBy": "sum"},
        {"name": "value_cr", "dataType": "double", "formatString": "#,##0.00", "sourceColumn": "value_cr", "summarizeBy": "sum"},
        {"name": "avg_ticket_size_inr", "dataType": "double", "formatString": "₹#,##0.00", "sourceColumn": "avg_ticket_size_inr", "summarizeBy": "none"},
        {"name": "prev_year_volume_mn", "dataType": "double", "formatString": "#,##0.00", "sourceColumn": "prev_year_volume_mn", "summarizeBy": "sum"},
        {"name": "prev_year_value_cr", "dataType": "double", "formatString": "#,##0.00", "sourceColumn": "prev_year_value_cr", "summarizeBy": "sum"},
        {"name": "yoy_volume_growth_pct", "dataType": "double", "formatString": "0.00", "sourceColumn": "yoy_volume_growth_pct", "summarizeBy": "none"},
        {"name": "yoy_value_growth_pct", "dataType": "double", "formatString": "0.00", "sourceColumn": "yoy_value_growth_pct", "summarizeBy": "none"},
    ]

    measures = [
        {
            "name": "Total Volume (Mn)",
            "expression": "SUM(MonthlyMetrics[volume_mn])",
            "formatString": "#,##0.00",
            "description": "Total transaction volume across the selected context in millions of transactions."
        },
        {
            "name": "Total Value (Cr INR)",
            "expression": "SUM(MonthlyMetrics[value_cr])",
            "formatString": "₹#,##0.00",
            "description": "Total transaction value across the selected context in crore Indian rupees."
        },
        {
            "name": "Weighted Avg Ticket Size (INR)",
            "expression": (
                "VAR _Vol = [Total Volume (Mn)]\n"
                "VAR _Val = [Total Value (Cr INR)]\n"
                "RETURN\n"
                "    IF(_Vol > 0, DIVIDE(_Val, _Vol) * 10, BLANK())"
            ),
            "formatString": "₹#,##0.00",
            "description": "Weighted average transaction size in INR: (Total Value Cr / Total Volume Mn) * 10."
        },
        {
            "name": "Latest Bank Count",
            "expression": (
                "VAR _LatestDate = CALCULATE(MAX(MonthlyMetrics[month]), REMOVEFILTERS(MonthlyMetrics))\n"
                "RETURN\n"
                "    CALCULATE(\n"
                "        MAX(MonthlyMetrics[bank_count]),\n"
                "        MonthlyMetrics[month] = _LatestDate\n"
                "    )"
            ),
            "formatString": "#,##0",
            "description": "Latest verified number of live member banks on the UPI network (as of September 2026)."
        },
        {
            "name": "Latest Month Volume (Mn)",
            "expression": (
                "VAR _LatestDate = CALCULATE(MAX(MonthlyMetrics[month]), REMOVEFILTERS(MonthlyMetrics))\n"
                "RETURN\n"
                "    CALCULATE(\n"
                "        [Total Volume (Mn)],\n"
                "        MonthlyMetrics[month] = _LatestDate\n"
                "    )"
            ),
            "formatString": "#,##0.00",
            "description": "Transaction volume for the most recent available month (September 2026: 24,068.38M)."
        },
        {
            "name": "Latest Month Value (Cr INR)",
            "expression": (
                "VAR _LatestDate = CALCULATE(MAX(MonthlyMetrics[month]), REMOVEFILTERS(MonthlyMetrics))\n"
                "RETURN\n"
                "    CALCULATE(\n"
                "        [Total Value (Cr INR)],\n"
                "        MonthlyMetrics[month] = _LatestDate\n"
                "    )"
            ),
            "formatString": "₹#,##0.00",
            "description": "Transaction value for the most recent available month (September 2026: ₹2,937,396.67 Cr)."
        },
        {
            "name": "Latest Month Volume YoY Growth %",
            "expression": (
                "VAR _LatestDate = CALCULATE(MAX(MonthlyMetrics[month]), REMOVEFILTERS(MonthlyMetrics))\n"
                "RETURN\n"
                "    CALCULATE(\n"
                "        SELECTEDVALUE(MonthlyMetrics[yoy_volume_growth_pct]),\n"
                "        MonthlyMetrics[month] = _LatestDate\n"
                "    ) / 100"
            ),
            "formatString": "0.00%",
            "description": "Year-over-year volume growth for the latest month (+22.59% for September 2026)."
        },
        {
            "name": "Latest Month Value YoY Growth %",
            "expression": (
                "VAR _LatestDate = CALCULATE(MAX(MonthlyMetrics[month]), REMOVEFILTERS(MonthlyMetrics))\n"
                "RETURN\n"
                "    CALCULATE(\n"
                "        SELECTEDVALUE(MonthlyMetrics[yoy_value_growth_pct]),\n"
                "        MonthlyMetrics[month] = _LatestDate\n"
                "    ) / 100"
            ),
            "formatString": "0.00%",
            "description": "Year-over-year value growth for the latest month (+17.98% for September 2026)."
        },
        {
            "name": "FY Volume (Mn)",
            "expression": "SUM(FinancialYearMetrics[total_volume_mn])",
            "formatString": "#,##0.00",
            "description": "Aggregated transaction volume from financial-year metrics table in millions."
        },
        {
            "name": "FY Value (Cr INR)",
            "expression": "SUM(FinancialYearMetrics[total_value_cr])",
            "formatString": "₹#,##0.00",
            "description": "Aggregated transaction value from financial-year metrics table in crore rupees."
        },
        {
            "name": "FY Completeness Status",
            "expression": (
                "IF(\n"
                "    HASONEVALUE(DimFinancialYear[FinancialYear]),\n"
                "    VAR _IsComp = SELECTEDVALUE(DimFinancialYear[IsComplete])\n"
                "    RETURN IF(_IsComp, \"Complete (12 Months)\", \"Incomplete (6 Months)\"),\n"
                "    \"Multiple Financial Years\"\n"
                ")"
            ),
            "description": "Indicates whether the filtered financial year has a complete 12-month baseline or partial data."
        },
        {
            "name": "FY Volume YoY Growth %",
            "expression": (
                "IF(\n"
                "    HASONEVALUE(DimFinancialYear[FinancialYear]),\n"
                "    VAR _IsComp = SELECTEDVALUE(DimFinancialYear[IsComplete])\n"
                "    VAR _Growth = SELECTEDVALUE(FinancialYearMetrics[yoy_volume_growth_pct])\n"
                "    RETURN\n"
                "        IF(_IsComp && NOT(ISBLANK(_Growth)), _Growth / 100, BLANK()),\n"
                "    BLANK()\n"
                ")"
            ),
            "formatString": "0.00%",
            "description": "Financial year volume YoY growth percentage. Returns blank for incomplete FY 2026-27 or baseline years."
        },
        {
            "name": "FY Value YoY Growth %",
            "expression": (
                "IF(\n"
                "    HASONEVALUE(DimFinancialYear[FinancialYear]),\n"
                "    VAR _IsComp = SELECTEDVALUE(DimFinancialYear[IsComplete])\n"
                "    VAR _Growth = SELECTEDVALUE(FinancialYearMetrics[yoy_value_growth_pct])\n"
                "    RETURN\n"
                "        IF(_IsComp && NOT(ISBLANK(_Growth)), _Growth / 100, BLANK()),\n"
                "    BLANK()\n"
                ")"
            ),
            "formatString": "0.00%",
            "description": "Financial year value YoY growth percentage. Returns blank for incomplete FY 2026-27 or baseline years."
        }
    ]

    table_monthly = {
        "name": "MonthlyMetrics",
        "columns": monthly_columns,
        "partitions": [
            {
                "name": "MonthlyMetrics-Partition",
                "mode": "import",
                "source": {"type": "m", "expression": m_expr_monthly}
            }
        ],
        "measures": measures
    }

    # ------------------------------------------------------------------------
    # 2. FinancialYearMetrics Table
    # ------------------------------------------------------------------------
    m_expr_fy = [
        "let",
        f'    Source = Csv.Document(File.Contents("{M_PATH_FY}"),[Delimiter=",", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
        '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
        '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"fy_label", type text}, {"months_available", Int64.Type}, {"is_complete", type logical}, {"total_volume_mn", type number}, {"total_value_cr", type number}, {"weighted_avg_ticket_size_inr", type number}, {"opening_bank_count", Int64.Type}, {"closing_bank_count", Int64.Type}, {"yoy_volume_growth_pct", type number}, {"yoy_value_growth_pct", type number}})',
        "in",
        '    #"Changed Type"'
    ]

    fy_columns = [
        {"name": "fy_label", "dataType": "string", "sourceColumn": "fy_label", "summarizeBy": "none"},
        {"name": "months_available", "dataType": "int64", "formatString": "#,##0", "sourceColumn": "months_available", "summarizeBy": "none"},
        {"name": "is_complete", "dataType": "boolean", "sourceColumn": "is_complete", "summarizeBy": "none"},
        {"name": "total_volume_mn", "dataType": "double", "formatString": "#,##0.00", "sourceColumn": "total_volume_mn", "summarizeBy": "sum"},
        {"name": "total_value_cr", "dataType": "double", "formatString": "#,##0.00", "sourceColumn": "total_value_cr", "summarizeBy": "sum"},
        {"name": "weighted_avg_ticket_size_inr", "dataType": "double", "formatString": "₹#,##0.00", "sourceColumn": "weighted_avg_ticket_size_inr", "summarizeBy": "none"},
        {"name": "opening_bank_count", "dataType": "int64", "formatString": "#,##0", "sourceColumn": "opening_bank_count", "summarizeBy": "none"},
        {"name": "closing_bank_count", "dataType": "int64", "formatString": "#,##0", "sourceColumn": "closing_bank_count", "summarizeBy": "none"},
        {"name": "yoy_volume_growth_pct", "dataType": "double", "formatString": "0.00", "sourceColumn": "yoy_volume_growth_pct", "summarizeBy": "none"},
        {"name": "yoy_value_growth_pct", "dataType": "double", "formatString": "0.00", "sourceColumn": "yoy_value_growth_pct", "summarizeBy": "none"},
    ]

    table_fy = {
        "name": "FinancialYearMetrics",
        "columns": fy_columns,
        "partitions": [
            {
                "name": "FinancialYearMetrics-Partition",
                "mode": "import",
                "source": {"type": "m", "expression": m_expr_fy}
            }
        ]
    }

    # ------------------------------------------------------------------------
    # 3. DimDate Table
    # ------------------------------------------------------------------------
    m_expr_dimdate = [
        "let",
        '    StartDate = #date(2016, 4, 1),',
        '    MonthCount = 126,',
        '    MonthList = List.Generate(() => 0, each _ < MonthCount, each _ + 1, each Date.AddMonths(StartDate, _)),',
        '    #"Converted to Table" = Table.FromList(MonthList, Splitter.SplitByNothing(), {"Date"}, null, ExtraValues.Error),',
        '    #"Changed Type" = Table.TransformColumnTypes(#"Converted to Table",{{"Date", type date}}),',
        '    #"Added Year" = Table.AddColumn(#"Changed Type", "Year", each Date.Year([Date]), Int64.Type),',
        '    #"Added MonthNo" = Table.AddColumn(#"Added Year", "MonthNo", each Date.Month([Date]), Int64.Type),',
        '    #"Added MonthName" = Table.AddColumn(#"Added MonthNo", "MonthName", each Date.MonthName([Date]), type text),',
        '    #"Added MonthShort" = Table.AddColumn(#"Added MonthName", "MonthShort", each Date.ToText([Date], "MMM"), type text),',
        '    #"Added MonthYear" = Table.AddColumn(#"Added MonthShort", "MonthYear", each Date.ToText([Date], "MMM yyyy"), type text),',
        '    #"Added YearMonthKey" = Table.AddColumn(#"Added MonthYear", "YearMonthKey", each Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),',
        '    #"Added FinancialYear" = Table.AddColumn(#"Added YearMonthKey", "FinancialYear", each if Date.Month([Date]) >= 4 then Text.From(Date.Year([Date])) & "-" & Text.End(Text.From(Date.Year([Date]) + 1), 2) else Text.From(Date.Year([Date]) - 1) & "-" & Text.End(Text.From(Date.Year([Date])), 2), type text),',
        '    #"Added FYQuarter" = Table.AddColumn(#"Added FinancialYear", "FYQuarter", each if List.Contains({4,5,6}, Date.Month([Date])) then "Q1" else if List.Contains({7,8,9}, Date.Month([Date])) then "Q2" else if List.Contains({10,11,12}, Date.Month([Date])) then "Q3" else "Q4", type text),',
        '    #"Added MonthInFY" = Table.AddColumn(#"Added FYQuarter", "MonthInFY", each if Date.Month([Date]) >= 4 then Date.Month([Date]) - 3 else Date.Month([Date]) + 9, Int64.Type)',
        "in",
        '    #"Added MonthInFY"'
    ]

    dimdate_columns = [
        {"name": "Date", "dataType": "dateTime", "formatString": "yyyy-MM-dd", "sourceColumn": "Date", "summarizeBy": "none"},
        {"name": "Year", "dataType": "int64", "formatString": "0000", "sourceColumn": "Year", "summarizeBy": "none"},
        {"name": "MonthNo", "dataType": "int64", "formatString": "00", "sourceColumn": "MonthNo", "summarizeBy": "none"},
        {"name": "MonthName", "dataType": "string", "sourceColumn": "MonthName", "summarizeBy": "none"},
        {"name": "MonthShort", "dataType": "string", "sourceColumn": "MonthShort", "summarizeBy": "none"},
        {"name": "MonthYear", "dataType": "string", "sourceColumn": "MonthYear", "sortByColumn": "YearMonthKey", "summarizeBy": "none"},
        {"name": "YearMonthKey", "dataType": "int64", "formatString": "0", "sourceColumn": "YearMonthKey", "summarizeBy": "none"},
        {"name": "FinancialYear", "dataType": "string", "sourceColumn": "FinancialYear", "summarizeBy": "none"},
        {"name": "FYQuarter", "dataType": "string", "sourceColumn": "FYQuarter", "summarizeBy": "none"},
        {"name": "MonthInFY", "dataType": "int64", "formatString": "00", "sourceColumn": "MonthInFY", "summarizeBy": "none"},
    ]

    table_dimdate = {
        "name": "DimDate",
        "columns": dimdate_columns,
        "partitions": [
            {
                "name": "DimDate-Partition",
                "mode": "import",
                "source": {"type": "m", "expression": m_expr_dimdate}
            }
        ]
    }

    # ------------------------------------------------------------------------
    # 4. DimFinancialYear Table
    # ------------------------------------------------------------------------
    m_expr_dimfy = [
        "let",
        '    Years = {2016..2026},',
        '    #"Converted to Table" = Table.FromList(Years, Splitter.SplitByNothing(), {"FYStartYear"}, null, ExtraValues.Error),',
        '    #"Changed Type" = Table.TransformColumnTypes(#"Converted to Table",{{"FYStartYear", Int64.Type}}),',
        '    #"Added FYEndYear" = Table.AddColumn(#"Changed Type", "FYEndYear", each [FYStartYear] + 1, Int64.Type),',
        '    #"Added FinancialYear" = Table.AddColumn(#"Added FYEndYear", "FinancialYear", each Text.From([FYStartYear]) & "-" & Text.End(Text.From([FYEndYear]), 2), type text),',
        '    #"Added FYSortOrder" = Table.AddColumn(#"Added FinancialYear", "FYSortOrder", each [FYStartYear] - 2015, Int64.Type),',
        '    #"Added IsComplete" = Table.AddColumn(#"Added FYSortOrder", "IsComplete", each [FYStartYear] < 2026, type logical),',
        '    #"Added Status" = Table.AddColumn(#"Added IsComplete", "Status", each if [FYStartYear] < 2026 then "Complete" else "Incomplete (6 Mo)", type text)',
        "in",
        '    #"Added Status"'
    ]

    dimfy_columns = [
        {"name": "FinancialYear", "dataType": "string", "sourceColumn": "FinancialYear", "sortByColumn": "FYSortOrder", "summarizeBy": "none"},
        {"name": "FYStartYear", "dataType": "int64", "formatString": "0000", "sourceColumn": "FYStartYear", "summarizeBy": "none"},
        {"name": "FYEndYear", "dataType": "int64", "formatString": "0000", "sourceColumn": "FYEndYear", "summarizeBy": "none"},
        {"name": "FYSortOrder", "dataType": "int64", "formatString": "0", "sourceColumn": "FYSortOrder", "summarizeBy": "none"},
        {"name": "IsComplete", "dataType": "boolean", "sourceColumn": "IsComplete", "summarizeBy": "none"},
        {"name": "Status", "dataType": "string", "sourceColumn": "Status", "summarizeBy": "none"},
    ]

    table_dimfy = {
        "name": "DimFinancialYear",
        "columns": dimfy_columns,
        "partitions": [
            {
                "name": "DimFinancialYear-Partition",
                "mode": "import",
                "source": {"type": "m", "expression": m_expr_dimfy}
            }
        ]
    }

    # ------------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------------
    relationships = [
        {
            "name": "DimDate_MonthlyMetrics",
            "fromTable": "MonthlyMetrics",
            "fromColumn": "month",
            "toTable": "DimDate",
            "toColumn": "Date",
            "crossFilteringBehavior": "oneDirection",
            "isActive": True
        },
        {
            "name": "DimFinancialYear_DimDate",
            "fromTable": "DimDate",
            "fromColumn": "FinancialYear",
            "toTable": "DimFinancialYear",
            "toColumn": "FinancialYear",
            "crossFilteringBehavior": "oneDirection",
            "isActive": True
        },
        {
            "name": "DimFinancialYear_FinancialYearMetrics",
            "fromTable": "FinancialYearMetrics",
            "fromColumn": "fy_label",
            "toTable": "DimFinancialYear",
            "toColumn": "FinancialYear",
            "crossFilteringBehavior": "oneDirection",
            "isActive": True
        }
    ]

    bim_model = {
        "name": "upi_growth_analysis",
        "compatibilityLevel": 1567,
        "model": {
            "culture": "en-US",
            "dataAccessOptions": {
                "legacyRedirects": True,
                "returnErrorValuesAsNull": True
            },
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "tables": [table_monthly, table_fy, table_dimdate, table_dimfy],
            "relationships": relationships,
            "annotations": [
                {
                    "name": "PBI_QueryOrder",
                    "value": '["MonthlyMetrics","FinancialYearMetrics","DimDate","DimFinancialYear"]'
                }
            ]
        }
    }
    return bim_model


def export_powerbi_project():
    """Create directory structure and all necessary Power BI Project files."""
    POWERBI_DIR.mkdir(parents=True, exist_ok=True)
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. upi_growth_analysis.pbip
    pbip_file = POWERBI_DIR / "upi_growth_analysis.pbip"
    pbip_data = {
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": "upi_growth_analysis.Report"
                }
            }
        ],
        "settings": {}
    }
    with open(pbip_file, "w", encoding="utf-8") as f:
        json.dump(pbip_data, f, indent=2)
    print(f"Created: {pbip_file.relative_to(BASE_DIR)}")

    # 2. definition.pbidataset
    pbidataset_file = DATASET_DIR / "definition.pbidataset"
    dataset_data = {
        "version": "1.0",
        "settings": {}
    }
    with open(pbidataset_file, "w", encoding="utf-8") as f:
        json.dump(dataset_data, f, indent=2)
    print(f"Created: {pbidataset_file.relative_to(BASE_DIR)}")

    # 3. model.bim
    bim_file = DATASET_DIR / "model.bim"
    bim_data = build_model_bim()
    with open(bim_file, "w", encoding="utf-8") as f:
        json.dump(bim_data, f, indent=2)
    print(f"Created: {bim_file.relative_to(BASE_DIR)}")

    # 4. definition.pbir
    pbir_file = REPORT_DIR / "definition.pbir"
    report_def_data = {
        "version": "1.0",
        "datasetReference": {
            "byPath": {
                "path": "../upi_growth_analysis.Dataset"
            },
            "byConnection": None
        }
    }
    with open(pbir_file, "w", encoding="utf-8") as f:
        json.dump(report_def_data, f, indent=2)
    print(f"Created: {pbir_file.relative_to(BASE_DIR)}")

    # 5. report.json
    report_json_file = REPORT_DIR / "report.json"
    report_json_data = {
        "config": json.dumps({
            "version": "5.53",
            "themeCollection": {
                "baseTheme": {
                    "name": "CY24SU02",
                    "version": "5.53",
                    "type": 2
                }
            },
            "activeSectionIndex": 0,
            "defaultDrillFilterOtherVisuals": True
        }),
        "layoutOptimization": 0,
        "resourcePackages": [],
        "sections": [
            {
                "name": "Section_DataModel",
                "displayName": "UPI Data Model Summary",
                "filters": "[]",
                "height": 720,
                "width": 1280,
                "visualContainers": []
            }
        ]
    }
    with open(report_json_file, "w", encoding="utf-8") as f:
        json.dump(report_json_data, f, indent=2)
    print(f"Created: {report_json_file.relative_to(BASE_DIR)}")


def export_standalone_scripts():
    """Export readable standalone M and DAX scripts for transparency and manual inspection."""
    # DAX file
    dax_path = POWERBI_DIR / "dax_measures.dax"
    dax_content = """/*
===============================================================================
UPI GROWTH ANALYSIS — CORE DAX MEASURES SPECIFICATION
Project: D:\\upi-growth-analysis\\powerbi\\upi_growth_analysis.pbip
Compatibility: Power BI Desktop / Analysis Services Tabular Model
===============================================================================
*/

// --- 1. CORE TRANSACTION AGGREGATES ---

[Total Volume (Mn)] = 
SUM(MonthlyMetrics[volume_mn])
/* Format: #,##0.00 | Total transaction volume in millions */

[Total Value (Cr INR)] = 
SUM(MonthlyMetrics[value_cr])
/* Format: ₹#,##0.00 | Total transaction value in crore rupees */

[Weighted Avg Ticket Size (INR)] = 
VAR _Vol = [Total Volume (Mn)]
VAR _Val = [Total Value (Cr INR)]
RETURN
    IF(
        _Vol > 0,
        DIVIDE(_Val, _Vol) * 10,
        BLANK()
    )
/* Format: ₹#,##0.00 | Weighted average transaction size in INR */


// --- 2. LATEST MONTH KPIS (RESOLVES TO SEPTEMBER 2026) ---

[Latest Bank Count] = 
VAR _LatestDate = CALCULATE(MAX(MonthlyMetrics[month]), REMOVEFILTERS(MonthlyMetrics))
RETURN
    CALCULATE(
        MAX(MonthlyMetrics[bank_count]),
        MonthlyMetrics[month] = _LatestDate
    )
/* Format: #,##0 | Latest bank count (756 member banks) */

[Latest Month Volume (Mn)] = 
VAR _LatestDate = CALCULATE(MAX(MonthlyMetrics[month]), REMOVEFILTERS(MonthlyMetrics))
RETURN
    CALCULATE(
        [Total Volume (Mn)],
        MonthlyMetrics[month] = _LatestDate
    )
/* Format: #,##0.00 | Latest month volume (24,068.38M) */

[Latest Month Value (Cr INR)] = 
VAR _LatestDate = CALCULATE(MAX(MonthlyMetrics[month]), REMOVEFILTERS(MonthlyMetrics))
RETURN
    CALCULATE(
        [Total Value (Cr INR)],
        MonthlyMetrics[month] = _LatestDate
    )
/* Format: ₹#,##0.00 | Latest month value (₹2,937,396.67 Cr) */

[Latest Month Volume YoY Growth %] = 
VAR _LatestDate = CALCULATE(MAX(MonthlyMetrics[month]), REMOVEFILTERS(MonthlyMetrics))
RETURN
    CALCULATE(
        SELECTEDVALUE(MonthlyMetrics[yoy_volume_growth_pct]),
        MonthlyMetrics[month] = _LatestDate
    ) / 100
/* Format: 0.00% | Latest YoY volume growth (+22.59%) */

[Latest Month Value YoY Growth %] = 
VAR _LatestDate = CALCULATE(MAX(MonthlyMetrics[month]), REMOVEFILTERS(MonthlyMetrics))
RETURN
    CALCULATE(
        SELECTEDVALUE(MonthlyMetrics[yoy_value_growth_pct]),
        MonthlyMetrics[month] = _LatestDate
    ) / 100
/* Format: 0.00% | Latest YoY value growth (+17.98%) */


// --- 3. FINANCIAL-YEAR LEVEL MEASURES ---

[FY Volume (Mn)] = 
SUM(FinancialYearMetrics[total_volume_mn])
/* Format: #,##0.00 | Aggregated financial-year volume */

[FY Value (Cr INR)] = 
SUM(FinancialYearMetrics[total_value_cr])
/* Format: ₹#,##0.00 | Aggregated financial-year value */

[FY Completeness Status] = 
IF(
    HASONEVALUE(DimFinancialYear[FinancialYear]),
    VAR _IsComp = SELECTEDVALUE(DimFinancialYear[IsComplete])
    RETURN IF(_IsComp, "Complete (12 Months)", "Incomplete (6 Months)"),
    "Multiple Financial Years"
)
/* String status clearly tagging partial FY 2026-27 */

[FY Volume YoY Growth %] = 
IF(
    HASONEVALUE(DimFinancialYear[FinancialYear]),
    VAR _IsComp = SELECTEDVALUE(DimFinancialYear[IsComplete])
    VAR _Growth = SELECTEDVALUE(FinancialYearMetrics[yoy_volume_growth_pct])
    RETURN
        IF(_IsComp && NOT(ISBLANK(_Growth)), _Growth / 100, BLANK()),
    BLANK()
)
/* Format: 0.00% | Financial year volume growth percentage (blank for FY 26-27 or baseline) */

[FY Value YoY Growth %] = 
IF(
    HASONEVALUE(DimFinancialYear[FinancialYear]),
    VAR _IsComp = SELECTEDVALUE(DimFinancialYear[IsComplete])
    VAR _Growth = SELECTEDVALUE(FinancialYearMetrics[yoy_value_growth_pct])
    RETURN
        IF(_IsComp && NOT(ISBLANK(_Growth)), _Growth / 100, BLANK()),
    BLANK()
)
/* Format: 0.00% | Financial year value growth percentage (blank for FY 26-27 or baseline) */
"""
    with open(dax_path, "w", encoding="utf-8") as f:
        f.write(dax_content)
    print(f"Created: {dax_path.relative_to(BASE_DIR)}")

    # Power Query M files
    m_dir = POWERBI_DIR / "powerquery"
    m_dir.mkdir(parents=True, exist_ok=True)

    # MonthlyMetrics.m
    with open(m_dir / "MonthlyMetrics.m", "w", encoding="utf-8") as f:
        f.write('let\n'
                f'    Source = Csv.Document(File.Contents("{M_PATH_MONTHLY}"),[Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n'
                '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n'
                '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"month", type date}, {"bank_count", Int64.Type}, {"volume_mn", type number}, {"value_cr", type number}, {"avg_ticket_size_inr", type number}, {"prev_year_volume_mn", type number}, {"prev_year_value_cr", type number}, {"yoy_volume_growth_pct", type number}, {"yoy_value_growth_pct", type number}})\n'
                'in\n'
                '    #"Changed Type"\n')

    # FinancialYearMetrics.m
    with open(m_dir / "FinancialYearMetrics.m", "w", encoding="utf-8") as f:
        f.write('let\n'
                f'    Source = Csv.Document(File.Contents("{M_PATH_FY}"),[Delimiter=",", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n'
                '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),\n'
                '    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"fy_label", type text}, {"months_available", Int64.Type}, {"is_complete", type logical}, {"total_volume_mn", type number}, {"total_value_cr", type number}, {"weighted_avg_ticket_size_inr", type number}, {"opening_bank_count", Int64.Type}, {"closing_bank_count", Int64.Type}, {"yoy_volume_growth_pct", type number}, {"yoy_value_growth_pct", type number}})\n'
                'in\n'
                '    #"Changed Type"\n')

    # DimDate.m
    with open(m_dir / "DimDate.m", "w", encoding="utf-8") as f:
        f.write("""let
    StartDate = #date(2016, 4, 1),
    MonthCount = 126,
    MonthList = List.Generate(() => 0, each _ < MonthCount, each _ + 1, each Date.AddMonths(StartDate, _)),
    #"Converted to Table" = Table.FromList(MonthList, Splitter.SplitByNothing(), {"Date"}, null, ExtraValues.Error),
    #"Changed Type" = Table.TransformColumnTypes(#"Converted to Table",{{"Date", type date}}),
    #"Added Year" = Table.AddColumn(#"Changed Type", "Year", each Date.Year([Date]), Int64.Type),
    #"Added MonthNo" = Table.AddColumn(#"Added Year", "MonthNo", each Date.Month([Date]), Int64.Type),
    #"Added MonthName" = Table.AddColumn(#"Added MonthNo", "MonthName", each Date.MonthName([Date]), type text),
    #"Added MonthShort" = Table.AddColumn(#"Added MonthName", "MonthShort", each Date.ToText([Date], "MMM"), type text),
    #"Added MonthYear" = Table.AddColumn(#"Added MonthShort", "MonthYear", each Date.ToText([Date], "MMM yyyy"), type text),
    #"Added YearMonthKey" = Table.AddColumn(#"Added MonthYear", "YearMonthKey", each Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    #"Added FinancialYear" = Table.AddColumn(#"Added YearMonthKey", "FinancialYear", each if Date.Month([Date]) >= 4 then Text.From(Date.Year([Date])) & "-" & Text.End(Text.From(Date.Year([Date]) + 1), 2) else Text.From(Date.Year([Date]) - 1) & "-" & Text.End(Text.From(Date.Year([Date])), 2), type text),
    #"Added FYQuarter" = Table.AddColumn(#"Added FinancialYear", "FYQuarter", each if List.Contains({4,5,6}, Date.Month([Date])) then "Q1" else if List.Contains({7,8,9}, Date.Month([Date])) then "Q2" else if List.Contains({10,11,12}, Date.Month([Date])) then "Q3" else "Q4", type text),
    #"Added MonthInFY" = Table.AddColumn(#"Added FYQuarter", "MonthInFY", each if Date.Month([Date]) >= 4 then Date.Month([Date]) - 3 else Date.Month([Date]) + 9, Int64.Type)
in
    #"Added MonthInFY"
""")

    # DimFinancialYear.m
    with open(m_dir / "DimFinancialYear.m", "w", encoding="utf-8") as f:
        f.write("""let
    Years = {2016..2026},
    #"Converted to Table" = Table.FromList(Years, Splitter.SplitByNothing(), {"FYStartYear"}, null, ExtraValues.Error),
    #"Changed Type" = Table.TransformColumnTypes(#"Converted to Table",{{"FYStartYear", Int64.Type}}),
    #"Added FYEndYear" = Table.AddColumn(#"Changed Type", "FYEndYear", each [FYStartYear] + 1, Int64.Type),
    #"Added FinancialYear" = Table.AddColumn(#"Added FYEndYear", "FinancialYear", each Text.From([FYStartYear]) & "-" & Text.End(Text.From([FYEndYear]), 2), type text),
    #"Added FYSortOrder" = Table.AddColumn(#"Added FinancialYear", "FYSortOrder", each [FYStartYear] - 2015, Int64.Type),
    #"Added IsComplete" = Table.AddColumn(#"Added FYSortOrder", "IsComplete", each [FYStartYear] < 2026, type logical),
    #"Added Status" = Table.AddColumn(#"Added IsComplete", "Status", each if [FYStartYear] < 2026 then "Complete" else "Incomplete (6 Mo)", type text)
in
    #"Added Status"
""")
    print(f"Created standalone Power Query M scripts in: {m_dir.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    print("=" * 60)
    print("Generating Power BI Project (.pbip) Semantic Model...")
    print("=" * 60)
    export_powerbi_project()
    export_standalone_scripts()
    print("\n[SUCCESS] Power BI project definition generated successfully.")
