"""
Builds Page 2: Growth & Adoption ("The UPI Growth Engine") for Task UPI-008A-FINAL.
Visuals created:
  1. btn_nav_overview (actionButton): Native 1-click navigation to Executive Overview with visible label.
  2. header_banner (textbox): Editorial section marker, headline, and subtitle.
  3. slicer_fy (slicer): Compact native Dropdown slicer bound to DimFinancialYear[FinancialYear].
  4. chart_monthly_growth_pulse (lineChart): Mature Scaling Growth Pulse (2020-2026) comparing Volume YoY %
     (Teal #2DD4BF) and Value YoY % (Violet #A78BFA).
  5. kpi_network_adoption (card): Network expansion multiple (36.0x) and launch hyper-growth callout.
  6. chart_fy_growth (clusteredColumnChart): Financial-year growth comparison (FY 2018-19 to FY 2025-26).
  7. table_monthly_detail (tableEx): Granular monthly detail explorer (126 observations) with MonthYear labels,
     enforced column widths spanning 1232px, and totals disabled.
  8. footer_note_p2 (textbox): Methodology context and boundary footnote with adequate height (no overflow).
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
PAGE_NAME = "GrowthAndAdoption"
PAGE_DIR = os.path.join(PAGES_DIR, PAGE_NAME)
VISUALS_DIR = os.path.join(PAGE_DIR, "visuals")

# Schema URLs
VC_SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json"
PAGE_SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
REPORT_SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json"
PAGES_META_SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"
FILTER_SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/filterConfiguration/1.1.0/schema-embedded.json"


def setup_page():
    """Create GrowthAndAdoption page.json and update pages.json."""
    os.makedirs(PAGE_DIR, exist_ok=True)
    os.makedirs(VISUALS_DIR, exist_ok=True)

    page_data = {
        "$schema": PAGE_SCHEMA_URL,
        "name": PAGE_NAME,
        "displayName": "Growth & Adoption",
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

    # Update pages.json to include both ExecutiveOverview and GrowthAndAdoption
    pages_json_path = os.path.join(PAGES_DIR, "pages.json")
    pages_data = {
        "$schema": PAGES_META_SCHEMA_URL,
        "pageOrder": ["ExecutiveOverview", PAGE_NAME],
        "activePageName": "ExecutiveOverview"
    }
    with open(pages_json_path, "w", encoding="utf-8") as f:
        json.dump(pages_data, f, indent=2)
    print(f"Updated {pages_json_path} with both pages.")


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


def build_page2_visuals():
    """Build all 8 visual containers for Page 2: Growth & Adoption."""
    visuals = []

    # 1. Back Navigation Button (actionButton) -> Navigates to ExecutiveOverview with visible text
    btn_container_fmt = get_container_formatting()
    btn_container_fmt["visualLink"] = [
        {
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "type": {"expr": {"Literal": {"Value": "'PageNavigation'"}}},
                "navigationSection": {"expr": {"Literal": {"Value": "'ExecutiveOverview'"}}},
                "tooltip": {"expr": {"Literal": {"Value": "'Back to Executive Overview'"}}}
            }
        }
    ]

    visuals.append({
        "name": "btn_nav_overview",
        "position": {"x": 24, "y": 16, "z": 1000, "height": 56, "width": 168, "tabOrder": 1000},
        "visual": {
            "visualType": "actionButton",
            "objects": {
                "action": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "type": {"expr": {"Literal": {"Value": "'PageNavigation'"}}},
                            "destination": {"expr": {"Literal": {"Value": "'ExecutiveOverview'"}}}
                        }
                    }
                ],
                "text": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}}
                        }
                    },
                    {
                        "properties": {
                            "text": {"expr": {"Literal": {"Value": "'← EXECUTIVE OVERVIEW'"}}},
                            "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "9.5D"}}},
                            "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}},
                            "bold": {"expr": {"Literal": {"Value": "true"}}},
                            "horizontalAlignment": {"expr": {"Literal": {"Value": "'center'"}}},
                            "verticalAlignment": {"expr": {"Literal": {"Value": "'middle'"}}}
                        },
                        "selector": {
                            "id": "default"
                        }
                    }
                ],
                "fill": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "fillColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#131B2E'"}}}}},
                            "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                        },
                        "selector": {
                            "id": "default"
                        }
                    }
                ],
                "outline": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}},
                            "lineWeight": {"expr": {"Literal": {"Value": "1D"}}},
                            "roundEdge": {"expr": {"Literal": {"Value": "6D"}}}
                        },
                        "selector": {
                            "id": "default"
                        }
                    }
                ]
            },
            "visualContainerObjects": btn_container_fmt
        }
    })

    # 2. Header Banner (textbox) - Section marker, headline, subtitle
    visuals.append({
        "name": "header_banner",
        "position": {"x": 200, "y": 16, "z": 1100, "height": 56, "width": 800, "tabOrder": 1100},
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
                                            "value": "02 / MOMENTUM & ADOPTION — ",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI Semibold",
                                                "fontSize": "8.5pt",
                                                "fontWeight": "bold",
                                                "color": "#2DD4BF"
                                            }
                                        },
                                        {
                                            "value": "THE UPI GROWTH ENGINE",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI Semibold",
                                                "fontSize": "13pt",
                                                "fontWeight": "bold",
                                                "color": "#F3F6FC"
                                            }
                                        }
                                    ]
                                },
                                {
                                    "textRuns": [
                                        {
                                            "value": "From early adoption to large-scale digital payment infrastructure · Apr 2016 – Sep 2026",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI",
                                                "fontSize": "8.5pt",
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

    # 3. Financial Year Slicer (slicer) - Compact native Dropdown
    visuals.append({
        "name": "slicer_fy",
        "position": {"x": 1016, "y": 16, "z": 1200, "height": 56, "width": 240, "tabOrder": 1200},
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

    # 4. Hero Visual: Monthly Growth Pulse (lineChart) - Volume YoY % vs Value YoY %
    # Focused on Mature Scaling Period (Jan 2020 – Sep 2026) to provide a 0%-250% scale
    # revealing COVID dip (Apr 2020), 2021 rebound, and Sep 2026 level (+22.59% vol, +17.98% val)
    visuals.append({
        "name": "chart_monthly_growth_pulse",
        "position": {"x": 24, "y": 84, "z": 2000, "height": 326, "width": 768, "tabOrder": 2000},
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
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "Monthly Volume YoY Growth %"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Monthly Volume YoY Growth %"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "Monthly Value YoY Growth %"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Monthly Value YoY Growth %"
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
                            "fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}},
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}
                        },
                        "selector": {
                            "metadata": "MonthlyMetrics.Monthly Volume YoY Growth %"
                        }
                    },
                    {
                        "properties": {
                            "fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}},
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}
                        },
                        "selector": {
                            "metadata": "MonthlyMetrics.Monthly Value YoY Growth %"
                        }
                    }
                ],
                "lines": [
                    {
                        "properties": {
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}
                        },
                        "selector": {
                            "metadata": "MonthlyMetrics.Monthly Volume YoY Growth %"
                        }
                    },
                    {
                        "properties": {
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}
                        },
                        "selector": {
                            "metadata": "MonthlyMetrics.Monthly Value YoY Growth %"
                        }
                    }
                ],
                "valueAxis": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "titleText": {"expr": {"Literal": {"Value": "'Monthly YoY Growth Rate (%)'"}}},
                            "showAxisTitle": {"expr": {"Literal": {"Value": "true"}}},
                            "titleColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F3F6FC'"}}}}},
                            "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}},
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
                ],
                "legend": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "position": {"expr": {"Literal": {"Value": "'Top'"}}},
                            "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="Monthly Growth Pulse — Mature Scaling (2020–2026)",
                subtitle_text="Sep 2026: Vol +22.59% · Val +17.98% | Launch rates documented in callout"
            )
        },
        "filterConfig": {
            "filters": [
                {
                    "name": "filter_mature_period",
                    "field": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": "DimDate"}},
                            "Property": "Date"
                        }
                    },
                    "type": "Advanced",
                    "howCreated": "User",
                    "filter": {
                        "Version": 2,
                        "From": [{"Name": "d", "Entity": "DimDate", "Type": 0}],
                        "Where": [
                            {
                                "Condition": {
                                    "Comparison": {
                                        "ComparisonKind": 2,
                                        "Left": {"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": "Date"}},
                                        "Right": {"Literal": {"Value": "datetime'2020-01-01T00:00:00'"}}
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
    })

    # 5. Network Adoption Card (card) - 36.0x Expansion Multiple & Launch Hyper-Growth Callout
    visuals.append({
        "name": "kpi_network_adoption",
        "position": {"x": 808, "y": 84, "z": 2100, "height": 106, "width": 448, "tabOrder": 2100},
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
                                        "Property": "Network Expansion Multiple"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Network Expansion Multiple"
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
                            "fontSize": {"expr": {"Literal": {"Value": "22D"}}}
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
                title_text="NETWORK ADOPTION & LAUNCH HYPER-GROWTH",
                subtitle_text="756 live banks (36.0x scale) | FY 17-18 Vol: +5,024%"
            )
        }
    })

    # 6. Financial-Year Growth Comparison (clusteredColumnChart) - Volume vs Value YoY %
    # Filtered to complete scaling years: FY 2018-19 through FY 2025-26
    visuals.append({
        "name": "chart_fy_growth",
        "position": {"x": 808, "y": 202, "z": 2200, "height": 208, "width": 448, "tabOrder": 2200},
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {
                "queryState": {
                    "Category": {
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
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "FY Volume YoY Growth %"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.FY Volume YoY Growth %"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "FY Value YoY Growth %"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.FY Value YoY Growth %"
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
                "dataPoint": [
                    {
                        "properties": {
                            "fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}
                        },
                        "selector": {
                            "metadata": "MonthlyMetrics.FY Volume YoY Growth %"
                        }
                    },
                    {
                        "properties": {
                            "fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}
                        },
                        "selector": {
                            "metadata": "MonthlyMetrics.FY Value YoY Growth %"
                        }
                    }
                ],
                "valueAxis": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "titleText": {"expr": {"Literal": {"Value": "'Annual YoY Growth (%)'"}}},
                            "showAxisTitle": {"expr": {"Literal": {"Value": "true"}}},
                            "titleColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F3F6FC'"}}}}},
                            "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}},
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
                ],
                "legend": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "position": {"expr": {"Literal": {"Value": "'Top'"}}},
                            "labelColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="Annual Growth Trajectory (FY YoY %)",
                subtitle_text="FY 2018–19 to FY 2025–26 · Launch outlier in callout"
            )
        },
        "filterConfig": {
            "filters": [
                {
                    "name": "filter_fy_scaling",
                    "field": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": "DimFinancialYear"}},
                            "Property": "FinancialYear"
                        }
                    },
                    "type": "Categorical",
                    "howCreated": "User",
                    "filter": {
                        "Version": 2,
                        "From": [{"Name": "fy", "Entity": "DimFinancialYear", "Type": 0}],
                        "Where": [
                            {
                                "Condition": {
                                    "In": {
                                        "Expressions": [
                                            {"Column": {"Expression": {"SourceRef": {"Source": "fy"}}, "Property": "FinancialYear"}}
                                        ],
                                        "Values": [
                                            [{"Literal": {"Value": "'2018-19'"}}],
                                            [{"Literal": {"Value": "'2019-20'"}}],
                                            [{"Literal": {"Value": "'2020-21'"}}],
                                            [{"Literal": {"Value": "'2021-22'"}}],
                                            [{"Literal": {"Value": "'2022-23'"}}],
                                            [{"Literal": {"Value": "'2023-24'"}}],
                                            [{"Literal": {"Value": "'2024-25'"}}],
                                            [{"Literal": {"Value": "'2025-26'"}}]
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                }
            ]
        }
    })

    # 7. Monthly Detail Exploration Table (tableEx) - 126 observations with MonthYear labels,
    # autoSizeColumnWidth: false to strictly enforce 1165px width utilization, and totals disabled
    visuals.append({
        "name": "table_monthly_detail",
        "position": {"x": 24, "y": 422, "z": 3000, "height": 238, "width": 1232, "tabOrder": 3000},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Entity": "DimDate"}},
                                        "Property": "MonthYear"
                                    }
                                },
                                "queryRef": "DimDate.MonthYear",
                                "displayName": "Month"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "Monthly Volume (Bn)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Monthly Volume (Bn)",
                                "displayName": "Volume (Bn)"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "Monthly Value (Lakh Cr INR)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Monthly Value (Lakh Cr INR)",
                                "displayName": "Value (Lakh Cr INR)"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "Weighted Avg Ticket Size (INR)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Weighted Avg Ticket Size (INR)",
                                "displayName": "Avg Ticket (INR)"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "Monthly Volume YoY Growth %"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Monthly Volume YoY Growth %",
                                "displayName": "Vol YoY %"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "Monthly Value YoY Growth %"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Monthly Value YoY Growth %",
                                "displayName": "Val YoY %"
                            },
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
                                "displayName": "Live Banks"
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
                                    "Property": "MonthYear"
                                }
                            },
                            "direction": "Descending"
                        }
                    ],
                    "isDefaultSort": False
                }
            },
            "objects": {
                "columnHeaders": [
                    {
                        "properties": {
                            "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F3F6FC'"}}}}},
                            "backColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1E293B'"}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "9.5D"}}},
                            "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}},
                            "autoSizeColumnWidth": {"expr": {"Literal": {"Value": "false"}}}
                        }
                    }
                ],
                "values": [
                    {
                        "properties": {
                            "fontColorPrimary": {"solid": {"color": {"expr": {"Literal": {"Value": "'#CBD5E1'"}}}}},
                            "backColorPrimary": {"solid": {"color": {"expr": {"Literal": {"Value": "'#131B2E'"}}}}},
                            "fontColorSecondary": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F3F6FC'"}}}}},
                            "backColorSecondary": {"solid": {"color": {"expr": {"Literal": {"Value": "'#162036'"}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "9D"}}},
                            "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI'"}}}
                        }
                    }
                ],
                "grid": [
                    {
                        "properties": {
                            "gridVertical": {"expr": {"Literal": {"Value": "true"}}},
                            "gridVerticalColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2A374E'"}}}}},
                            "gridVerticalWeight": {"expr": {"Literal": {"Value": "1D"}}},
                            "gridHorizontal": {"expr": {"Literal": {"Value": "true"}}},
                            "gridHorizontalColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2A374E'"}}}}},
                            "gridHorizontalWeight": {"expr": {"Literal": {"Value": "1D"}}}
                        }
                    }
                ],
                "total": [
                    {
                        "properties": {
                            "totals": {"expr": {"Literal": {"Value": "false"}}}
                        }
                    }
                ],
                "totals": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "false"}}}
                        }
                    }
                ],
                "columnWidth": [
                    {"properties": {"width": {"expr": {"Literal": {"Value": "140D"}}}}, "selector": {"metadata": "DimDate.MonthYear"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "175D"}}}}, "selector": {"metadata": "MonthlyMetrics.Monthly Volume (Bn)"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "200D"}}}}, "selector": {"metadata": "MonthlyMetrics.Monthly Value (Lakh Cr INR)"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "165D"}}}}, "selector": {"metadata": "MonthlyMetrics.Weighted Avg Ticket Size (INR)"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "170D"}}}}, "selector": {"metadata": "MonthlyMetrics.Monthly Volume YoY Growth %"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "170D"}}}}, "selector": {"metadata": "MonthlyMetrics.Monthly Value YoY Growth %"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "145D"}}}}, "selector": {"metadata": "Max(MonthlyMetrics.bank_count)"}}
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="Monthly Transaction & Network Detail Explorer (All 126 Months)",
                subtitle_text="Granular drilldown · Apr 2016 – Sep 2026 (preserves all launch & zero-volume months) · Filtered by FY slicer"
            )
        }
    })

    # 8. Methodology Context Footnote (textbox) - Height 44px to prevent scrollbar/clipping
    visuals.append({
        "name": "footer_note_p2",
        "position": {"x": 24, "y": 668, "z": 4000, "height": 44, "width": 1232, "tabOrder": 4000},
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
                                            "value": "Methodology Context: Source: NPCI official statistics. Reporting comparability changes from August 2018: NPCI excludes same-account debit/credit transactions from this point onward. FY 2026–27 covers April–September 2026 and is incomplete. Launch-phase hyper-growth (FY 17–18 +5,024% Vol, Jul 17 +897.6K% Val) reflects initial low-base scaling.",
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


def validate_page2(visuals):
    """Validate Page 2 generated files against Fabric schemas."""
    print("\n--- Validating Page 2 Generated Files Against Fabric Schemas ---")
    headers = {'User-Agent': 'Mozilla/5.0'}
    get_json = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode())

    vc_schema = get_json(VC_SCHEMA_URL)
    emb_schema = get_json("https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualConfiguration/2.0.0/schema-embedded.json")
    sq_schema = get_json("https://developer.microsoft.com/json-schemas/fabric/item/report/definition/semanticQuery/1.2.0/schema.json")
    fmt_schema = get_json("https://developer.microsoft.com/json-schemas/fabric/item/report/definition/formattingObjectDefinitions/1.3.0/schema.json")
    filter_schema = get_json(FILTER_SCHEMA_URL)
    page_schema = get_json(PAGE_SCHEMA_URL)
    report_schema = get_json(REPORT_SCHEMA_URL)

    store = {
        VC_SCHEMA_URL: vc_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualConfiguration/2.0.0/schema-embedded.json": emb_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualConfiguration/2.0.0/schema.embedded.json": emb_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/semanticQuery/1.2.0/schema.json": sq_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/formattingObjectDefinitions/1.3.0/schema.json": fmt_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/formattingObjectDefinitions/1.5.0/schema.json": fmt_schema,
        FILTER_SCHEMA_URL: filter_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/filterConfiguration/1.1.0/schema.embedded.json": filter_schema,
        PAGE_SCHEMA_URL: page_schema,
        REPORT_SCHEMA_URL: report_schema
    }

    # Validate page.json
    page_json_path = os.path.join(PAGE_DIR, "page.json")
    with open(page_json_path, "r", encoding="utf-8") as f:
        page_inst = json.load(f)
    page_resolver = jsonschema.validators.RefResolver(base_uri=PAGE_SCHEMA_URL, referrer=page_schema, store=store)
    jsonschema.validate(instance=page_inst, schema=page_schema, resolver=page_resolver)
    print("SUCCESS: GrowthAndAdoption page.json passed schema validation!")

    # Validate each visual
    vc_resolver = jsonschema.validators.RefResolver(base_uri=VC_SCHEMA_URL, referrer=vc_schema, store=store)
    for v in visuals:
        jsonschema.validate(instance=v, schema=vc_schema, resolver=vc_resolver)
        print(f"SUCCESS: visual '{v['name']}' ({v['visual']['visualType']}) passed schema validation!")

    print("\nALL 8 PAGE 2 VISUALS FULLY VALIDATED!")


if __name__ == "__main__":
    setup_page()
    visuals = build_page2_visuals()
    validate_page2(visuals)
