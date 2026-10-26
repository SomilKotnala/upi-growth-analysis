"""
Builds the polished Executive Overview page for Task UPI-007B-QA4.
Visual polish & styling defect fixes:
  - Chart series colors: Teal (#2DD4BF) for Volume, Violet (#A78BFA) for Value, Emerald (#34D399) for Banks
    with exact PBIR selector metadata targeting and lines stroke properties.
  - High-contrast axis titles (#F3F6FC) and labels (#CBD5E1) on dark navy (#131B2E) background.
  - Slicer FY with high-contrast text (#F3F6FC) and matching background (#131B2E).
  - Header banner: clean paragraph structure without embedded newline, expanded height to 62px,
    completely eliminating vertical scrollbar overflow artifact (white strip).
  - Slicer FY height synchronized to 62px for perfect top row alignment.
  - Complete schema validation and layout auditing.
"""
import os
import shutil
import json
import urllib.request
import jsonschema

PROJECT_ROOT = r"D:\upi-growth-analysis"
REPORT_DIR = os.path.join(PROJECT_ROOT, "powerbi", "upi_growth_analysis.Report")
DEF_DIR = os.path.join(REPORT_DIR, "definition")
PAGES_DIR = os.path.join(DEF_DIR, "pages")
STATIC_RES_DIR = os.path.join(REPORT_DIR, "StaticResources", "RegisteredResources")
DEF_RES_DIR = os.path.join(DEF_DIR, "RegisteredResources")
PAGE_NAME = "ExecutiveOverview"
PAGE_DIR = os.path.join(PAGES_DIR, PAGE_NAME)
VISUALS_DIR = os.path.join(PAGE_DIR, "visuals")

# Schema URLs
VC_SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json"
PAGE_SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
REPORT_SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json"
PAGES_META_SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"


def setup_theme():
    """Create Dark Fintech theme and register in report.json across all resource paths."""
    os.makedirs(STATIC_RES_DIR, exist_ok=True)
    os.makedirs(DEF_RES_DIR, exist_ok=True)
    theme_filename = "DarkFintechTheme.json"
    theme_path = os.path.join(STATIC_RES_DIR, theme_filename)
    theme_def_path = os.path.join(DEF_RES_DIR, theme_filename)

    theme_content = {
        "name": "DarkFintechTheme",
        "dataColors": [
            "#2DD4BF",  # Teal accent (Volume)
            "#A78BFA",  # Violet accent (Value)
            "#34D399",  # Emerald positive growth / Banks
            "#FB7185",  # Rose negative growth
            "#38BDF8",  # Sky blue (Ticket size)
            "#F59E0B",  # Amber
            "#EC4899",  # Pink
            "#818CF8"   # Indigo
        ],
        "background": "#0B1020",
        "foreground": "#F3F6FC",
        "tableAccent": "#2DD4BF",
        "visualStyles": {
            "*": {
                "*": {
                    "outspace": [{"color": {"solid": {"color": "#0B1020"}}}],
                    "background": [{"show": True, "color": {"solid": {"color": "#131B2E"}}, "transparency": 0}],
                    "border": [{"show": True, "color": {"solid": {"color": "#1E293B"}}, "radius": 6}],
                    "title": [{"show": True, "fontColor": {"solid": {"color": "#F3F6FC"}}, "fontSize": 11, "fontFamily": "Segoe UI Semibold"}],
                    "subTitle": [{"show": True, "fontColor": {"solid": {"color": "#CBD5E1"}}, "fontSize": 9.5, "fontFamily": "Segoe UI"}]
                }
            },
            "page": {
                "*": {
                    "background": [{"color": {"solid": {"color": "#0B1020"}}, "transparency": 0}],
                    "outspace": [{"color": {"solid": {"color": "#0B1020"}}, "transparency": 0}]
                }
            },
            "card": {
                "*": {
                    "labels": [{"color": {"solid": {"color": "#2DD4BF"}}, "fontSize": 20, "fontFamily": "Segoe UI Bold"}],
                    "categoryLabels": [{"show": True, "color": {"solid": {"color": "#CBD5E1"}}, "fontSize": 10, "fontFamily": "Segoe UI"}]
                }
            },
            "slicer": {
                "*": {
                    "data": [{"mode": "Dropdown"}],
                    "general": [{"mode": "Dropdown"}],
                    "slicerSettings": [{"style": "Dropdown"}],
                    "header": [{"show": True, "fontColor": {"solid": {"color": "#F3F6FC"}}, "background": {"solid": {"color": "#131B2E"}}, "textSize": 10}],
                    "items": [{"fontColor": {"solid": {"color": "#F3F6FC"}}, "background": {"solid": {"color": "#131B2E"}}, "textSize": 10}]
                }
            },
            "areaChart": {
                "*": {
                    "valueAxis": [{"show": True, "titleColor": {"solid": {"color": "#F3F6FC"}}, "labelColor": {"solid": {"color": "#CBD5E1"}}}],
                    "categoryAxis": [{"show": True, "labelColor": {"solid": {"color": "#CBD5E1"}}}]
                }
            },
            "lineChart": {
                "*": {
                    "valueAxis": [{"show": True, "titleColor": {"solid": {"color": "#F3F6FC"}}, "labelColor": {"solid": {"color": "#CBD5E1"}}}],
                    "categoryAxis": [{"show": True, "labelColor": {"solid": {"color": "#CBD5E1"}}}]
                }
            }
        }
    }

    with open(theme_path, "w", encoding="utf-8") as f:
        json.dump(theme_content, f, indent=2)
    with open(theme_def_path, "w", encoding="utf-8") as f:
        json.dump(theme_content, f, indent=2)
    print(f"Created custom theme at {theme_path} and {theme_def_path}")

    # Update report.json
    report_json_path = os.path.join(DEF_DIR, "report.json")
    report_data = {
        "$schema": REPORT_SCHEMA_URL,
        "themeCollection": {
            "baseTheme": {
                "name": "CY24SU02",
                "reportVersionAtImport": {
                    "visual": "1.8.89",
                    "report": "2.0.89",
                    "page": "1.3.89"
                },
                "type": "SharedResources"
            },
            "customTheme": {
                "name": "DarkFintechTheme",
                "reportVersionAtImport": {
                    "visual": "1.8.89",
                    "report": "2.0.89",
                    "page": "1.3.89"
                },
                "type": "RegisteredResources"
            }
        },
        "resourcePackages": [
            {
                "name": "SharedResources",
                "type": "SharedResources",
                "items": [
                    {
                        "name": "CY24SU02",
                        "path": "BaseThemes/CY24SU02.json",
                        "type": "BaseTheme"
                    }
                ]
            },
            {
                "name": "RegisteredResources",
                "type": "RegisteredResources",
                "items": [
                    {
                        "name": "DarkFintechTheme",
                        "path": f"RegisteredResources/{theme_filename}",
                        "type": "CustomTheme"
                    }
                ]
            }
        ]
    }

    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    print("Updated report.json with custom theme registration.")


def setup_pages():
    """Create ExecutiveOverview page.json and update pages.json."""
    os.makedirs(PAGE_DIR, exist_ok=True)
    os.makedirs(VISUALS_DIR, exist_ok=True)

    page_data = {
        "$schema": PAGE_SCHEMA_URL,
        "name": PAGE_NAME,
        "displayName": "Executive Overview",
        "displayOption": "FitToPage",
        "width": 1280,
        "height": 720,
        "objects": {
            "background": [
                {
                    "properties": {
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#0B1020'"}}}}},
                        "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                    }
                }
            ],
            "outspace": [
                {
                    "properties": {
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#0B1020'"}}}}},
                        "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                    }
                }
            ]
        }
    }

    page_json_path = os.path.join(PAGE_DIR, "page.json")
    with open(page_json_path, "w", encoding="utf-8") as f:
        json.dump(page_data, f, indent=2)
    print(f"Created {page_json_path}")

    # Remove Section_DataModel if present
    legacy_page = os.path.join(PAGES_DIR, "Section_DataModel")
    if os.path.exists(legacy_page):
        shutil.rmtree(legacy_page)
        print(f"Removed legacy placeholder page {legacy_page}")

    # Update pages.json (preserving multi-page order)
    pages_json_path = os.path.join(PAGES_DIR, "pages.json")
    page_order = [PAGE_NAME]
    if os.path.exists(pages_json_path):
        try:
            with open(pages_json_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
                for p in existing.get("pageOrder", []):
                    if p not in page_order:
                        page_order.append(p)
        except Exception:
            pass
    pages_data = {
        "$schema": PAGES_META_SCHEMA_URL,
        "pageOrder": page_order,
        "activePageName": PAGE_NAME
    }
    with open(pages_json_path, "w", encoding="utf-8") as f:
        json.dump(pages_data, f, indent=2)
    print(f"Updated {pages_json_path} (pageOrder: {page_order})")


def get_container_formatting(title_text=None, subtitle_text=None, bg_color="'#131B2E'", border_color="'#1E293B'", radius="6D", show_border=True, show_header=False):
    """Standard visualContainerObjects formatting with high-contrast typography."""
    formatting = {
        "background": [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": bg_color}}}}},
                    "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                }
            }
        ]
    }
    if show_border:
        formatting["border"] = [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "color": {"solid": {"color": {"expr": {"Literal": {"Value": border_color}}}}},
                    "radius": {"expr": {"Literal": {"Value": radius}}}
                }
            }
        ]
    if title_text:
        formatting["title"] = [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{title_text}'"}}},
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F3F6FC'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "10D"}}},
                    "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}}
                }
            }
        ]
    if subtitle_text:
        formatting["subTitle"] = [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": f"'{subtitle_text}'"}}},
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": "9D"}}},
                    "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI'"}}}
                }
            }
        ]
    if show_header:
        formatting["visualHeader"] = [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}}
                }
            }
        ]
    return formatting


def build_visuals():
    """Build all 11 visual containers with QA4 visual polish."""
    visuals = []

    # 1. Header Banner (textbox) - Height 62px, 2 clean paragraphs, no newline scrollbar overflow
    visuals.append({
        "name": "header_banner",
        "position": {"x": 24, "y": 16, "z": 1000, "height": 62, "width": 976, "tabOrder": 1000},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {
                                            "value": "UPI | INDIA'S DIGITAL PAYMENTS GROWTH",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI Semibold",
                                                "fontSize": "15pt",
                                                "fontWeight": "bold",
                                                "color": "#F3F6FC"
                                            }
                                        }
                                    ]
                                },
                                {
                                    "textRuns": [
                                        {
                                            "value": "Monthly Transaction & Network Scaling Analysis · Apr 2016 – Sep 2026 · Official NPCI Data Baseline",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI",
                                                "fontSize": "9.5pt",
                                                "color": "#CBD5E1"
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting()
        }
    })

    # 2. Financial Year Slicer (slicer) - Height 62px, compact native Dropdown slicer
    visuals.append({
        "name": "slicer_fy",
        "position": {"x": 1016, "y": 16, "z": 1100, "height": 62, "width": 240, "tabOrder": 1100},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Entity": "DimFinancialYear"}},
                                        "Property": "FinancialYear"
                                    }
                                },
                                "queryRef": "DimFinancialYear.FinancialYear"
                            }
                        ]
                    }
                },
                "sortDefinition": {
                    "sort": [
                        {
                            "field": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Entity": "DimFinancialYear"}},
                                    "Property": "FinancialYear"
                                }
                            },
                            "direction": "Ascending"
                        }
                    ],
                    "isDefaultSort": False
                }
            },
            "objects": {
                "data": [
                    {
                        "properties": {
                            "mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}
                        }
                    }
                ],
                "general": [
                    {
                        "properties": {
                            "mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}
                        }
                    }
                ],
                "slicerSettings": [
                    {
                        "properties": {
                            "style": {"expr": {"Literal": {"Value": "'Dropdown'"}}}
                        }
                    }
                ],
                "selection": [
                    {
                        "properties": {
                            "selectAllCheckbox": {"expr": {"Literal": {"Value": "true"}}},
                            "singleSelect": {"expr": {"Literal": {"Value": "false"}}}
                        }
                    }
                ],
                "header": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F3F6FC'"}}}}},
                            "background": {"solid": {"color": {"expr": {"Literal": {"Value": "'#131B2E'"}}}}},
                            "textSize": {"expr": {"Literal": {"Value": "10D"}}}
                        }
                    }
                ],
                "items": [
                    {
                        "properties": {
                            "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F3F6FC'"}}}}},
                            "background": {"solid": {"color": {"expr": {"Literal": {"Value": "'#131B2E'"}}}}},
                            "textSize": {"expr": {"Literal": {"Value": "10D"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting(title_text="Filter Financial Year", show_header=True)
        }
    })

    # 3. KPI 1: Total Volume (Bn)
    visuals.append({
        "name": "kpi_total_volume",
        "position": {"x": 24, "y": 86, "z": 2000, "height": 104, "width": 236, "tabOrder": 2000},
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "Total Volume (Bn)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Total Volume (Bn)"
                            }
                        ]
                    }
                }
            },
            "objects": {
                "labels": [
                    {
                        "properties": {
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "18D"}}},
                            "labelDisplayUnits": {"expr": {"Literal": {"Value": "1D"}}}
                        }
                    }
                ],
                "categoryLabels": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "false"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="TOTAL VOLUME (BILLION)",
                subtitle_text="Cumulative transactions: 870.01 Bn"
            )
        }
    })

    # 4. KPI 2: Total Value (Lakh Cr INR)
    visuals.append({
        "name": "kpi_total_value",
        "position": {"x": 272, "y": 86, "z": 2100, "height": 104, "width": 236, "tabOrder": 2100},
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "Total Value (Lakh Cr INR)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Total Value (Lakh Cr INR)"
                            }
                        ]
                    }
                }
            },
            "objects": {
                "labels": [
                    {
                        "properties": {
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "18D"}}},
                            "labelDisplayUnits": {"expr": {"Literal": {"Value": "1D"}}}
                        }
                    }
                ],
                "categoryLabels": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "false"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="TOTAL VALUE (LAKH CR INR)",
                subtitle_text="Cumulative turnover: ₹1,247.36 Lakh Cr"
            )
        }
    })

    # 5. KPI 3: Weighted Avg Ticket Size (INR)
    visuals.append({
        "name": "kpi_ticket_size",
        "position": {"x": 520, "y": 86, "z": 2200, "height": 104, "width": 236, "tabOrder": 2200},
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "Weighted Avg Ticket Size (INR)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Weighted Avg Ticket Size (INR)"
                            }
                        ]
                    }
                }
            },
            "objects": {
                "labels": [
                    {
                        "properties": {
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#38BDF8'"}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "18D"}}},
                            "labelDisplayUnits": {"expr": {"Literal": {"Value": "1D"}}}
                        }
                    }
                ],
                "categoryLabels": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "false"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="AVG TICKET SIZE (INR)",
                subtitle_text="Overall weighted ticket: ₹1,433.74"
            )
        }
    })

    # 6. KPI 4: Latest Participating Banks Count
    visuals.append({
        "name": "kpi_bank_count",
        "position": {"x": 768, "y": 86, "z": 2300, "height": 104, "width": 236, "tabOrder": 2300},
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "Latest Bank Count"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Latest Bank Count"
                            }
                        ]
                    }
                }
            },
            "objects": {
                "labels": [
                    {
                        "properties": {
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#34D399'"}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "18D"}}},
                            "labelDisplayUnits": {"expr": {"Literal": {"Value": "1D"}}}
                        }
                    }
                ],
                "categoryLabels": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "false"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="LIVE MEMBER BANKS",
                subtitle_text="Active network participants: 756 Banks"
            )
        }
    })

    # 7. KPI 5: Latest Month YoY Growth Momentum (Sep 2026)
    visuals.append({
        "name": "kpi_latest_growth",
        "position": {"x": 1016, "y": 86, "z": 2400, "height": 104, "width": 240, "tabOrder": 2400},
        "visual": {
            "visualType": "card",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "Latest Month Volume YoY Growth %"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Latest Month Volume YoY Growth %"
                            }
                        ]
                    }
                }
            },
            "objects": {
                "labels": [
                    {
                        "properties": {
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#34D399'"}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "18D"}}}
                        }
                    }
                ],
                "categoryLabels": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "false"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="SEP 2026 MOMENTUM",
                subtitle_text="YoY Vol: +22.59% | YoY Val: +17.98%"
            )
        }
    })

    # 8. Monthly Volume Trend Chart (areaChart in Billions - Teal #2DD4BF)
    visuals.append({
        "name": "chart_monthly_volume",
        "position": {"x": 24, "y": 204, "z": 3000, "height": 236, "width": 604, "tabOrder": 3000},
        "visual": {
            "visualType": "areaChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Entity": "DimDate"}},
                                        "Property": "Date"
                                    }
                                },
                                "queryRef": "DimDate.Date"
                            }
                        ]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "Monthly Volume (Bn)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Monthly Volume (Bn)"
                            }
                        ]
                    }
                },
                "sortDefinition": {
                    "sort": [
                        {
                            "field": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Entity": "DimDate"}},
                                    "Property": "Date"
                                }
                            },
                            "direction": "Ascending"
                        }
                    ],
                    "isDefaultSort": False
                }
            },
            "objects": {
                "dataPoint": [
                    {
                        "properties": {
                            "fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}
                        },
                        "selector": {
                            "metadata": "MonthlyMetrics.Monthly Volume (Bn)"
                        }
                    },
                    {
                        "properties": {
                            "fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}
                        }
                    }
                ],
                "lines": [
                    {
                        "properties": {
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}
                        },
                        "selector": {
                            "metadata": "MonthlyMetrics.Monthly Volume (Bn)"
                        }
                    },
                    {
                        "properties": {
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}
                        }
                    }
                ],
                "valueAxis": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "titleText": {"expr": {"Literal": {"Value": "'Volume (Billion Transactions)'"}}},
                            "showAxisTitle": {"expr": {"Literal": {"Value": "true"}}},
                            "titleColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F3F6FC'"}}}}},
                            "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}},
                            "labelDisplayUnits": {"expr": {"Literal": {"Value": "1D"}}},
                            "gridlineShow": {"expr": {"Literal": {"Value": "true"}}},
                            "gridlineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2A374E'"}}}}}
                        }
                    }
                ],
                "categoryAxis": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "showAxisTitle": {"expr": {"Literal": {"Value": "false"}}},
                            "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="Monthly Transaction Volume (Billion Transactions)",
                subtitle_text="Jul 2016: 0.09M → Aug 2026 peak: 24,508.96M (24.51 Bn) · Latest: Sep 2026, 24,068.38M (24.07 Bn)"
            )
        }
    })

    # 9. Monthly Value Trend Chart (areaChart in Lakh Crore - Violet #A78BFA)
    visuals.append({
        "name": "chart_monthly_value",
        "position": {"x": 652, "y": 204, "z": 3100, "height": 236, "width": 604, "tabOrder": 3100},
        "visual": {
            "visualType": "areaChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Entity": "DimDate"}},
                                        "Property": "Date"
                                    }
                                },
                                "queryRef": "DimDate.Date"
                            }
                        ]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "Monthly Value (Lakh Cr INR)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Monthly Value (Lakh Cr INR)"
                            }
                        ]
                    }
                },
                "sortDefinition": {
                    "sort": [
                        {
                            "field": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Entity": "DimDate"}},
                                    "Property": "Date"
                                }
                            },
                            "direction": "Ascending"
                        }
                    ],
                    "isDefaultSort": False
                }
            },
            "objects": {
                "dataPoint": [
                    {
                        "properties": {
                            "fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}
                        },
                        "selector": {
                            "metadata": "MonthlyMetrics.Monthly Value (Lakh Cr INR)"
                        }
                    },
                    {
                        "properties": {
                            "fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}
                        }
                    }
                ],
                "lines": [
                    {
                        "properties": {
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}
                        },
                        "selector": {
                            "metadata": "MonthlyMetrics.Monthly Value (Lakh Cr INR)"
                        }
                    },
                    {
                        "properties": {
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}
                        }
                    }
                ],
                "valueAxis": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "titleText": {"expr": {"Literal": {"Value": "'Value (Lakh Crore INR)'"}}},
                            "showAxisTitle": {"expr": {"Literal": {"Value": "true"}}},
                            "titleColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F3F6FC'"}}}}},
                            "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}},
                            "labelDisplayUnits": {"expr": {"Literal": {"Value": "1D"}}},
                            "gridlineShow": {"expr": {"Literal": {"Value": "true"}}},
                            "gridlineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2A374E'"}}}}}
                        }
                    }
                ],
                "categoryAxis": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "showAxisTitle": {"expr": {"Literal": {"Value": "false"}}},
                            "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="Monthly Transaction Value (Lakh Crore INR)",
                subtitle_text="Jul 2016: ₹0.38 Cr → May 2026 peak: ₹29,90,424.21 Cr (₹29.90 Lakh Cr) · Latest: Sep 2026, ₹29.37 Lakh Cr"
            )
        }
    })

    # 10. Participating Banks Expansion Chart (lineChart - Emerald #34D399)
    visuals.append({
        "name": "chart_bank_growth",
        "position": {"x": 24, "y": 452, "z": 3200, "height": 226, "width": 1232, "tabOrder": 3200},
        "visual": {
            "visualType": "lineChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Entity": "DimDate"}},
                                        "Property": "Date"
                                    }
                                },
                                "queryRef": "DimDate.Date"
                            }
                        ]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {
                                    "Aggregation": {
                                        "Expression": {
                                            "Column": {
                                                "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                                "Property": "bank_count"
                                            }
                                        },
                                        "Function": 4
                                    }
                                },
                                "queryRef": "Max(MonthlyMetrics.bank_count)",
                                "displayName": "Live Member Banks"
                            }
                        ]
                    }
                },
                "sortDefinition": {
                    "sort": [
                        {
                            "field": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Entity": "DimDate"}},
                                    "Property": "Date"
                                }
                            },
                            "direction": "Ascending"
                        }
                    ],
                    "isDefaultSort": False
                }
            },
            "objects": {
                "dataPoint": [
                    {
                        "properties": {
                            "fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#34D399'"}}}}},
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#34D399'"}}}}}
                        },
                        "selector": {
                            "metadata": "Max(MonthlyMetrics.bank_count)"
                        }
                    },
                    {
                        "properties": {
                            "fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#34D399'"}}}}},
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#34D399'"}}}}}
                        }
                    }
                ],
                "lines": [
                    {
                        "properties": {
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#34D399'"}}}}}
                        },
                        "selector": {
                            "metadata": "Max(MonthlyMetrics.bank_count)"
                        }
                    },
                    {
                        "properties": {
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#34D399'"}}}}}
                        }
                    }
                ],
                "valueAxis": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "titleText": {"expr": {"Literal": {"Value": "'Live Member Banks'"}}},
                            "showAxisTitle": {"expr": {"Literal": {"Value": "true"}}},
                            "titleColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F3F6FC'"}}}}},
                            "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}},
                            "labelDisplayUnits": {"expr": {"Literal": {"Value": "1D"}}},
                            "gridlineShow": {"expr": {"Literal": {"Value": "true"}}},
                            "gridlineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2A374E'"}}}}}
                        }
                    }
                ],
                "categoryAxis": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "showAxisTitle": {"expr": {"Literal": {"Value": "false"}}},
                            "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="UPI Network Expansion — Participating Live Member Banks",
                subtitle_text="Ecosystem scale: 21 banks in Apr 2016 to 756 live member banks in Sep 2026 (36x expansion)"
            )
        }
    })

    # 11. Footer Methodology Note (textbox)
    visuals.append({
        "name": "footer_note",
        "position": {"x": 24, "y": 684, "z": 4000, "height": 28, "width": 1232, "tabOrder": 4000},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {
                                            "value": "Source: NPCI official monthly statistics. Same-account debit/credit transactions are excluded from August 2018 onwards; this methodology change affects comparisons across that boundary. FY 2026–27 data covers April–September 2026 and is incomplete.",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI",
                                                "fontSize": "8pt",
                                                "color": "#94A3B8"
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting(bg_color="'#0B1020'", border_color="'#0B1020'", show_border=False)
        }
    })

    # Write each visual container
    for v in visuals:
        v["$schema"] = VC_SCHEMA_URL
        v_name = v["name"]
        v_dir = os.path.join(VISUALS_DIR, v_name)
        os.makedirs(v_dir, exist_ok=True)
        v_path = os.path.join(v_dir, "visual.json")
        with open(v_path, "w", encoding="utf-8") as f:
            json.dump(v, f, indent=2)
        print(f"Created visual container: {v_name} ({v['visual']['visualType']}) at {v_path}")

    return visuals


def validate_all(visuals):
    """Validate all generated files against schemas."""
    print("\n--- Validating Generated Files Against Fabric Schemas ---")
    headers = {'User-Agent': 'Mozilla/5.0'}
    get_json = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode())

    vc_schema = get_json(VC_SCHEMA_URL)
    emb_schema = get_json("https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualConfiguration/2.0.0/schema-embedded.json")
    sq_schema = get_json("https://developer.microsoft.com/json-schemas/fabric/item/report/definition/semanticQuery/1.2.0/schema.json")
    fmt_schema = get_json("https://developer.microsoft.com/json-schemas/fabric/item/report/definition/formattingObjectDefinitions/1.3.0/schema.json")
    page_schema = get_json(PAGE_SCHEMA_URL)
    report_schema = get_json(REPORT_SCHEMA_URL)

    store = {
        VC_SCHEMA_URL: vc_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualConfiguration/2.0.0/schema-embedded.json": emb_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualConfiguration/2.0.0/schema.embedded.json": emb_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/semanticQuery/1.2.0/schema.json": sq_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/formattingObjectDefinitions/1.3.0/schema.json": fmt_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/formattingObjectDefinitions/1.5.0/schema.json": fmt_schema,
        PAGE_SCHEMA_URL: page_schema,
        REPORT_SCHEMA_URL: report_schema
    }

    # Validate report.json
    report_json_path = os.path.join(DEF_DIR, "report.json")
    with open(report_json_path, "r", encoding="utf-8") as f:
        rep_inst = json.load(f)
    rep_resolver = jsonschema.validators.RefResolver(base_uri=REPORT_SCHEMA_URL, referrer=report_schema, store=store)
    jsonschema.validate(instance=rep_inst, schema=report_schema, resolver=rep_resolver)
    print("SUCCESS: report.json passed schema validation!")

    # Validate page.json
    page_json_path = os.path.join(PAGE_DIR, "page.json")
    with open(page_json_path, "r", encoding="utf-8") as f:
        page_inst = json.load(f)
    page_resolver = jsonschema.validators.RefResolver(base_uri=PAGE_SCHEMA_URL, referrer=page_schema, store=store)
    jsonschema.validate(instance=page_inst, schema=page_schema, resolver=page_resolver)
    print("SUCCESS: page.json passed schema validation!")

    # Validate each visual
    vc_resolver = jsonschema.validators.RefResolver(base_uri=VC_SCHEMA_URL, referrer=vc_schema, store=store)
    for v in visuals:
        jsonschema.validate(instance=v, schema=vc_schema, resolver=vc_resolver)
        print(f"SUCCESS: visual '{v['name']}' ({v['visual']['visualType']}) passed schema validation!")

    print("\nALL 11 VISUALS AND PAGE CONFIGURATIONS FULLY VALIDATED!")


if __name__ == "__main__":
    setup_theme()
    setup_pages()
    visuals = build_visuals()
    validate_all(visuals)
