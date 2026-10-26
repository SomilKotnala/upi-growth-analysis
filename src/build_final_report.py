"""
build_final_report.py
Generates the complete, portfolio-grade 3-page Power BI report for upi_growth_analysis_final:
  Page 1: ExecutiveOverview ("UPI / INDIA'S DIGITAL PAYMENTS SCALE - Scale & Trajectory")
  Page 2: GrowthAndAdoption ("THE UPI GROWTH ENGINE - Momentum & Adoption")
  Page 3: FinancialYearPerformance ("THE ANNUAL SCORECARD - Performance & Financial-Year Matrix")
Includes full schema validation against Fabric schemas and layout collision auditing.
"""
import os
import shutil
import json
import jsonschema

PROJECT_ROOT = r"D:\upi-growth-analysis"
REPORT_DIR = os.path.join(PROJECT_ROOT, "powerbi", "upi_growth_analysis_final.Report")
DEF_DIR = os.path.join(REPORT_DIR, "definition")
PAGES_DIR = os.path.join(DEF_DIR, "pages")
STATIC_RES_DIR = os.path.join(REPORT_DIR, "StaticResources", "RegisteredResources")
DEF_RES_DIR = os.path.join(DEF_DIR, "RegisteredResources")
SCHEMA_CACHE_DIR = os.path.join(PROJECT_ROOT, ".cache", "schemas")

# Fabric Schema URLs
VC_SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json"
PAGE_SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
REPORT_SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json"
PAGES_META_SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json"
FILTER_SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/filterConfiguration/1.1.0/schema-embedded.json"


def setup_theme_and_report_json():
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
                    "title": [{"show": True, "fontColor": {"solid": {"color": "#F3F6FC"}}, "fontSize": 10, "fontFamily": "Segoe UI Semibold"}],
                    "subTitle": [{"show": True, "fontColor": {"solid": {"color": "#CBD5E1"}}, "fontSize": 9, "fontFamily": "Segoe UI"}]
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
                    "labels": [{"color": {"solid": {"color": "#2DD4BF"}}, "fontSize": 18, "fontFamily": "Segoe UI Bold"}],
                    "categoryLabels": [{"show": True, "color": {"solid": {"color": "#CBD5E1"}}, "fontSize": 9.5, "fontFamily": "Segoe UI"}]
                }
            },
            "slicer": {
                "*": {
                    "data": [{"mode": "Dropdown"}],
                    "general": [{"mode": "Dropdown"}, {"outlineColor": {"solid": {"color": "#2A374E"}}}],
                    "slicerSettings": [{"style": "Dropdown"}],
                    "header": [{"show": False}],
                    "dropdown": [{"borderColor": {"solid": {"color": "#2A374E"}}, "background": {"solid": {"color": "#131B2E"}}, "borderRadius": 4}],
                    "items": [{"fontColor": {"solid": {"color": "#F3F6FC"}}, "background": {"solid": {"color": "#131B2E"}}, "textSize": 9.5}]
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
            },
            "clusteredColumnChart": {
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
    print("Theme registered in report.json.")

    # Write version.json
    version_json_path = os.path.join(DEF_DIR, "version.json")
    version_data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
        "version": "2.0.0"
    }
    with open(version_json_path, "w", encoding="utf-8") as f:
        json.dump(version_data, f, indent=2)
    print("version.json created.")

    # Write .platform
    platform_json_path = os.path.join(REPORT_DIR, ".platform")
    platform_data = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {
            "type": "Report",
            "displayName": "upi_growth_analysis_final"
        },
        "config": {
            "version": "2.0",
            "logicalId": "0fa501e4-ec95-4776-882c-fe4e02fe04b5"
        }
    }
    with open(platform_json_path, "w", encoding="utf-8") as f:
        json.dump(platform_data, f, indent=2)
    print(".platform created.")


def get_container_formatting(title_text=None, subtitle_text=None, bg_color="'#131B2E'", border_color="'#1E293B'", radius="6D", show_border=True, show_header=False, title_font_size="10D", title_font_color="'#F3F6FC'", subtitle_font_size="8D"):
    """Standard visualContainerObjects formatting."""
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
                    "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": title_font_color}}}}},
                    "fontSize": {"expr": {"Literal": {"Value": title_font_size}}},
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
                    "fontSize": {"expr": {"Literal": {"Value": subtitle_font_size}}},
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


def build_nav_button(name, x, y, width, height, tab_order, label, target_page, is_active=False):
    """Build a visible native page-navigation button."""
    btn_bg = "'#1E293B'" if is_active else "'#131B2E'"
    btn_border = "'#2DD4BF'" if is_active else "'#1E293B'"
    font_color = "'#2DD4BF'" if is_active else "'#CBD5E1'"

    container_fmt = get_container_formatting(bg_color=btn_bg, border_color=btn_border, radius="6D")
    container_fmt["visualLink"] = [
        {
            "properties": {
                "show": {"expr": {"Literal": {"Value": "true"}}},
                "type": {"expr": {"Literal": {"Value": "'PageNavigation'"}}},
                "navigationSection": {"expr": {"Literal": {"Value": f"'{target_page}'"}}},
                "tooltip": {"expr": {"Literal": {"Value": f"'Navigate to {label}'"}}}
            }
        }
    ]

    return {
        "name": name,
        "position": {"x": x, "y": y, "z": tab_order, "height": height, "width": width, "tabOrder": tab_order},
        "visual": {
            "visualType": "actionButton",
            "objects": {
                "action": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "type": {"expr": {"Literal": {"Value": "'PageNavigation'"}}},
                            "destination": {"expr": {"Literal": {"Value": f"'{target_page}'"}}}
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
                            "text": {"expr": {"Literal": {"Value": f"'{label}'"}}},
                            "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": font_color}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "9.5D"}}},
                            "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI Semibold'"}}},
                            "bold": {"expr": {"Literal": {"Value": "true"}}},
                            "horizontalAlignment": {"expr": {"Literal": {"Value": "'center'"}}},
                            "verticalAlignment": {"expr": {"Literal": {"Value": "'middle'"}}}
                        },
                        "selector": {"id": "default"}
                    }
                ],
                "fill": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "fillColor": {"solid": {"color": {"expr": {"Literal": {"Value": btn_bg}}}}},
                            "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                        },
                        "selector": {"id": "default"}
                    }
                ],
                "outline": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": btn_border}}}}},
                            "lineWeight": {"expr": {"Literal": {"Value": "1D"}}},
                            "roundEdge": {"expr": {"Literal": {"Value": "6D"}}}
                        },
                        "selector": {"id": "default"}
                    }
                ]
            },
            "visualContainerObjects": container_fmt
        }
    }


def build_slicer_fy(name, x, y, width, height, tab_order):
    """Build a clearly clickable, high-contrast native Dropdown slicer."""
    return {
        "name": name,
        "position": {"x": x, "y": y, "z": tab_order, "height": height, "width": width, "tabOrder": tab_order},
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
                            "mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}},
                            "outlineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2A374E'"}}}}},
                            "outlineWeight": {"expr": {"Literal": {"Value": "1D"}}}
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
                            "show": {"expr": {"Literal": {"Value": "false"}}},
                            "titleText": {"expr": {"Literal": {"Value": "'FINANCIAL YEAR'"}}}
                        }
                    }
                ],
                "items": [
                    {
                        "properties": {
                            "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F3F6FC'"}}}}},
                            "background": {"solid": {"color": {"expr": {"Literal": {"Value": "'#131B2E'"}}}}},
                            "textSize": {"expr": {"Literal": {"Value": "9.5D"}}},
                            "fontFamily": {"expr": {"Literal": {"Value": "'Segoe UI'"}}}
                        }
                    }
                ],
                "dropdown": [
                    {
                        "properties": {
                            "background": {"solid": {"color": {"expr": {"Literal": {"Value": "'#131B2E'"}}}}},
                            "borderColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2A374E'"}}}}},
                            "borderWidth": {"expr": {"Literal": {"Value": "1D"}}},
                            "borderRadius": {"expr": {"Literal": {"Value": "4D"}}}
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="FINANCIAL YEAR",
                title_font_size="8.5D",
                title_font_color="'#CBD5E1'",
                show_header=True
            )
        }
    }


def create_page_json(page_dir, page_name, display_name):
    """Write page.json for a given page."""
    os.makedirs(page_dir, exist_ok=True)
    page_data = {
        "$schema": PAGE_SCHEMA_URL,
        "name": page_name,
        "displayName": display_name,
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
    p_path = os.path.join(page_dir, "page.json")
    with open(p_path, "w", encoding="utf-8") as f:
        json.dump(page_data, f, indent=2)
    print(f"Created page: {page_name} at {p_path}")


def write_visuals(page_name, visuals):
    """Write visual containers for a page."""
    p_dir = os.path.join(PAGES_DIR, page_name, "visuals")
    if os.path.exists(p_dir):
        shutil.rmtree(p_dir)
    os.makedirs(p_dir, exist_ok=True)
    for v in visuals:
        v["$schema"] = VC_SCHEMA_URL
        v_dir = os.path.join(p_dir, v["name"])
        os.makedirs(v_dir, exist_ok=True)
        v_path = os.path.join(v_dir, "visual.json")
        with open(v_path, "w", encoding="utf-8") as f:
            json.dump(v, f, indent=2)
    print(f"Wrote {len(visuals)} visuals for {page_name}")


def build_page1_executive_overview():
    """Build Page 1: ExecutiveOverview (Scale & Trajectory)."""
    visuals = []

    # 1. Header Banner (textbox)
    visuals.append({
        "name": "header_banner",
        "position": {"x": 24, "y": 16, "z": 1000, "height": 60, "width": 620, "tabOrder": 1000},
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
                                            "value": "UPI | INDIA'S DIGITAL PAYMENTS SCALE",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI Semibold",
                                                "fontSize": "13.5pt",
                                                "fontWeight": "bold",
                                                "color": "#F3F6FC"
                                            }
                                        }
                                    ]
                                },
                                {
                                    "textRuns": [
                                        {
                                            "value": "Macro Scale & Network Evolution · Apr 2016 – Sep 2026 · Official NPCI Data Baseline",
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

    # 2-4. Navigation Buttons (Page 1 Active)
    visuals.append(build_nav_button("btn_nav_p1", 656, 16, 110, 60, 1100, "1. SCALE", "ExecutiveOverview", is_active=True))
    visuals.append(build_nav_button("btn_nav_p2", 774, 16, 110, 60, 1200, "2. ADOPTION", "GrowthAndAdoption", is_active=False))
    visuals.append(build_nav_button("btn_nav_p3", 892, 16, 110, 60, 1300, "3. SCORECARD", "FinancialYearPerformance", is_active=False))

    # 5. Financial Year Dropdown Slicer
    visuals.append(build_slicer_fy("slicer_fy", 1014, 16, 242, 60, 1400))

    # 6-10. Row 2: 5 KPI Cards (y: 84, h: 88, bottom: 172)
    # KPI 1: Total Volume (Bn)
    visuals.append({
        "name": "kpi_total_volume",
        "position": {"x": 24, "y": 84, "z": 2000, "height": 88, "width": 236, "tabOrder": 2000},
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
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="TOTAL VOLUME (BILLION)",
                subtitle_text="Cumulative: 870.01 Bn transactions"
            )
        }
    })

    # KPI 2: Total Value (Lakh Cr INR)
    visuals.append({
        "name": "kpi_total_value",
        "position": {"x": 273, "y": 84, "z": 2100, "height": 88, "width": 236, "tabOrder": 2100},
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
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="TOTAL VALUE (LAKH CR)",
                subtitle_text="Cumulative: ₹1,247.36 Lakh Cr"
            )
        }
    })

    # KPI 3: Avg Ticket Size (INR)
    visuals.append({
        "name": "kpi_ticket_size",
        "position": {"x": 522, "y": 84, "z": 2200, "height": 88, "width": 236, "tabOrder": 2200},
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
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="AVG TICKET SIZE (INR)",
                subtitle_text="Overall weighted: ₹1,433.74"
            )
        }
    })

    # KPI 4: Live Member Banks
    visuals.append({
        "name": "kpi_bank_count",
        "position": {"x": 771, "y": 84, "z": 2300, "height": 88, "width": 236, "tabOrder": 2300},
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
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="LIVE MEMBER BANKS",
                subtitle_text="Active network: 756 Banks"
            )
        }
    })

    # KPI 5: Latest YoY Growth Momentum (Sep 2026)
    visuals.append({
        "name": "kpi_latest_growth",
        "position": {"x": 1020, "y": 84, "z": 2400, "height": 88, "width": 236, "tabOrder": 2400},
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
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="SEP 2026 MOMENTUM",
                subtitle_text="YoY Vol: +22.59% | Val: +17.98%"
            )
        }
    })

    # 11. Monthly Volume Trend Chart (areaChart, Teal #2DD4BF)
    visuals.append({
        "name": "chart_monthly_volume",
        "position": {"x": 24, "y": 184, "z": 3000, "height": 284, "width": 610, "tabOrder": 3000},
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
                        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}},
                        "selector": {"metadata": "MonthlyMetrics.Monthly Volume (Bn)"}
                    },
                    {"properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}}}
                ],
                "lines": [
                    {
                        "properties": {"lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}},
                        "selector": {"metadata": "MonthlyMetrics.Monthly Volume (Bn)"}
                    },
                    {"properties": {"lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}}}
                ],
                "valueAxis": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "titleText": {"expr": {"Literal": {"Value": "'Monthly Volume (Billion)'"}}},
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
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="Monthly Transaction Volume Trajectory (Billions)",
                subtitle_text="Jul 2016: 0.09M → Aug 2026 peak: 24,508.96M · Latest: Sep 2026, 24,068.38M"
            )
        }
    })

    # 12. Monthly Value Trend Chart (areaChart, Violet #A78BFA)
    visuals.append({
        "name": "chart_monthly_value",
        "position": {"x": 646, "y": 184, "z": 3100, "height": 284, "width": 610, "tabOrder": 3100},
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
                        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}},
                        "selector": {"metadata": "MonthlyMetrics.Monthly Value (Lakh Cr INR)"}
                    },
                    {"properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}}}
                ],
                "lines": [
                    {
                        "properties": {"lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}},
                        "selector": {"metadata": "MonthlyMetrics.Monthly Value (Lakh Cr INR)"}
                    },
                    {"properties": {"lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}}}
                ],
                "valueAxis": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "titleText": {"expr": {"Literal": {"Value": "'Monthly Value (Lakh Crore INR)'"}}},
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
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="Monthly Transaction Value Trajectory (Lakh Crore INR)",
                subtitle_text="Jul 2016: ₹0.38 Cr → May 2026 peak: ₹29.90L Cr · Latest: Sep 2026, ₹29.37L Cr"
            )
        }
    })

    # 13. Bank Network Expansion Chart (lineChart, Emerald #34D399)
    visuals.append({
        "name": "chart_bank_growth",
        "position": {"x": 24, "y": 480, "z": 4000, "height": 176, "width": 780, "tabOrder": 4000},
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
                                "queryRef": "Max(MonthlyMetrics.bank_count)"
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
                        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#34D399'"}}}}}},
                        "selector": {"metadata": "Max(MonthlyMetrics.bank_count)"}
                    },
                    {"properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#34D399'"}}}}}}}
                ],
                "lines": [
                    {
                        "properties": {"lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#34D399'"}}}}}},
                        "selector": {"metadata": "Max(MonthlyMetrics.bank_count)"}
                    },
                    {"properties": {"lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#34D399'"}}}}}}}
                ],
                "valueAxis": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "titleText": {"expr": {"Literal": {"Value": "'Live Member Banks'"}}},
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
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="UPI Participating Member Banks Growth (2016–2026)",
                subtitle_text="Network scale: 21 member banks in Apr 2016 expanding to 756 live banks in Sep 2026 (36.0x expansion)"
            )
        }
    })

    # 14. Key Facts Editorial Textbox
    visuals.append({
        "name": "textbox_facts",
        "position": {"x": 816, "y": 480, "z": 4100, "height": 176, "width": 440, "tabOrder": 4100},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {"value": "KEY MEASURED FACTS", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "10pt", "fontWeight": "bold", "color": "#2DD4BF"}}
                                    ]
                                },
                                {
                                    "textRuns": [
                                        {"value": "• Cumulative Volume: ", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "8.5pt", "color": "#F3F6FC"}},
                                        {"value": "870.01 Billion transactions across 126 reported months.\n", "textStyle": {"fontFamily": "Segoe UI", "fontSize": "8.5pt", "color": "#CBD5E1"}},
                                        {"value": "• Cumulative Value: ", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "8.5pt", "color": "#F3F6FC"}},
                                        {"value": "₹1,247.36 Lakh Crore across 126 reported months.\n", "textStyle": {"fontFamily": "Segoe UI", "fontSize": "8.5pt", "color": "#CBD5E1"}},
                                        {"value": "• Average Ticket Size: ", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "8.5pt", "color": "#F3F6FC"}},
                                        {"value": "₹1,433.74 weighted average ticket size across the full 126-month period.\n", "textStyle": {"fontFamily": "Segoe UI", "fontSize": "8.5pt", "color": "#CBD5E1"}},
                                        {"value": "• Peaks: ", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "8.5pt", "color": "#F3F6FC"}},
                                        {"value": "Volume peak August 2026 (24.51 Bn); Value peak May 2026 (₹29.90 Lakh Cr).", "textStyle": {"fontFamily": "Segoe UI", "fontSize": "8.5pt", "color": "#CBD5E1"}}
                                    ]
                                }
                            ]
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting(title_text="EXECUTIVE HIGHLIGHTS")
        }
    })

    # 15. Footnote (textbox, y: 668, h: 44, bottom: 712)
    visuals.append({
        "name": "footer_note_p1",
        "position": {"x": 24, "y": 668, "z": 5000, "height": 44, "width": 1232, "tabOrder": 5000},
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

    return visuals


def build_page2_growth_adoption():
    """Build Page 2: GrowthAndAdoption (Momentum & Adoption)."""
    visuals = []

    # 1. Header Banner
    visuals.append({
        "name": "header_banner",
        "position": {"x": 24, "y": 16, "z": 1000, "height": 60, "width": 620, "tabOrder": 1000},
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
                                            "value": "THE UPI GROWTH ENGINE",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI Semibold",
                                                "fontSize": "13.5pt",
                                                "fontWeight": "bold",
                                                "color": "#F3F6FC"
                                            }
                                        }
                                    ]
                                },
                                {
                                    "textRuns": [
                                        {
                                            "value": "Scaling Dynamics, Network Multiples & Monthly Detail Explorer · Apr 2016 – Sep 2026",
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

    # 2-4. Navigation Buttons (Page 2 Active)
    visuals.append(build_nav_button("btn_nav_p1", 656, 16, 110, 60, 1100, "1. SCALE", "ExecutiveOverview", is_active=False))
    visuals.append(build_nav_button("btn_nav_p2", 774, 16, 110, 60, 1200, "2. ADOPTION", "GrowthAndAdoption", is_active=True))
    visuals.append(build_nav_button("btn_nav_p3", 892, 16, 110, 60, 1300, "3. SCORECARD", "FinancialYearPerformance", is_active=False))

    # 5. Financial Year Dropdown Slicer
    visuals.append(build_slicer_fy("slicer_fy", 1014, 16, 242, 60, 1400))

    # 6. Hero Line Chart: Monthly Growth Pulse (2020-2026)
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
                        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}},
                        "selector": {"metadata": "MonthlyMetrics.Monthly Volume YoY Growth %"}
                    },
                    {
                        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}},
                        "selector": {"metadata": "MonthlyMetrics.Monthly Value YoY Growth %"}
                    }
                ],
                "lines": [
                    {
                        "properties": {"lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}},
                        "selector": {"metadata": "MonthlyMetrics.Monthly Volume YoY Growth %"}
                    },
                    {
                        "properties": {"lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}},
                        "selector": {"metadata": "MonthlyMetrics.Monthly Value YoY Growth %"}
                    }
                ],
                "valueAxis": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "titleText": {"expr": {"Literal": {"Value": "'YoY Growth Rate (%)'"}}},
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
                title_text="Mature Scaling Growth Pulse: Volume vs Value YoY % (2020–2026)",
                subtitle_text="Focuses on mature growth (0%–250%) · COVID rebound & Sep 2026: +22.59% vol, +17.98% val"
            )
        },
        "filterConfig": {
            "filters": [
                {
                    "name": "filter_mature_pulse",
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

    # 7. Network Adoption Callout Card
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
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="NETWORK ADOPTION & LAUNCH HYPER-GROWTH",
                subtitle_text="756 live banks (36.0x scale) | FY 17-18 Vol: +5,024%"
            )
        }
    })

    # 8. Clustered Column: Financial Year Growth
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
                        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}},
                        "selector": {"metadata": "MonthlyMetrics.FY Volume YoY Growth %"}
                    },
                    {
                        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}},
                        "selector": {"metadata": "MonthlyMetrics.FY Value YoY Growth %"}
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

    # 9. Monthly Detail Explorer Table (tableEx)
    visuals.append({
        "name": "table_monthly_detail",
        "position": {"x": 24, "y": 422, "z": 3000, "height": 236, "width": 1232, "tabOrder": 3000},
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
                "total": [{"properties": {"totals": {"expr": {"Literal": {"Value": "false"}}}}}],
                "totals": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "columnWidth": [
                    {"properties": {"width": {"expr": {"Literal": {"Value": "150D"}}}}, "selector": {"metadata": "DimDate.MonthYear"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "180D"}}}}, "selector": {"metadata": "MonthlyMetrics.Monthly Volume (Bn)"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "210D"}}}}, "selector": {"metadata": "MonthlyMetrics.Monthly Value (Lakh Cr INR)"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "180D"}}}}, "selector": {"metadata": "MonthlyMetrics.Weighted Avg Ticket Size (INR)"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "170D"}}}}, "selector": {"metadata": "MonthlyMetrics.Monthly Volume YoY Growth %"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "170D"}}}}, "selector": {"metadata": "MonthlyMetrics.Monthly Value YoY Growth %"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "172D"}}}}, "selector": {"metadata": "Max(MonthlyMetrics.bank_count)"}}
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="Monthly Transaction & Network Detail Explorer (All 126 Months)",
                subtitle_text="Granular drilldown · Apr 2016 – Sep 2026 (preserves all launch & zero-volume months) · Filtered by FY slicer"
            )
        }
    })

    # 10. Footnote (y: 668, h: 44, bottom: 712)
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
                                            "value": "Methodology Context: Source: NPCI official statistics. Same-account debit/credit transactions are excluded from August 2018 onwards. FY 2026–27 covers April–September 2026 (6 months, incomplete). Launch hyper-growth (FY 17–18 +5,024% Vol) represents initial low-base expansion.",
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

    return visuals


def build_page3_financial_year_performance():
    """Build Page 3: FinancialYearPerformance (The Annual Scorecard)."""
    visuals = []

    # 1. Header Banner
    visuals.append({
        "name": "header_banner",
        "position": {"x": 24, "y": 16, "z": 1000, "height": 60, "width": 620, "tabOrder": 1000},
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
                                            "value": "THE ANNUAL SCORECARD",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI Semibold",
                                                "fontSize": "13.5pt",
                                                "fontWeight": "bold",
                                                "color": "#F3F6FC"
                                            }
                                        }
                                    ]
                                },
                                {
                                    "textRuns": [
                                        {
                                            "value": "Fiscal Year Trajectory, Volume/Value Comparison & Matrix · FY 2016–17 through FY 2026–27",
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

    # 2-4. Navigation Buttons (Page 3 Active)
    visuals.append(build_nav_button("btn_nav_p1", 656, 16, 110, 60, 1100, "1. SCALE", "ExecutiveOverview", is_active=False))
    visuals.append(build_nav_button("btn_nav_p2", 774, 16, 110, 60, 1200, "2. ADOPTION", "GrowthAndAdoption", is_active=False))
    visuals.append(build_nav_button("btn_nav_p3", 892, 16, 110, 60, 1300, "3. SCORECARD", "FinancialYearPerformance", is_active=True))

    # 5. Financial Year Dropdown Slicer
    visuals.append(build_slicer_fy("slicer_fy", 1014, 16, 242, 60, 1400))

    # 6-9. Row 2: 4 Annual Performance KPI Cards (y: 84, h: 84, bottom: 168)
    # KPI 1: FY Volume (Bn)
    visuals.append({
        "name": "kpi_fy_latest_vol",
        "position": {"x": 24, "y": 84, "z": 2000, "height": 84, "width": 299, "tabOrder": 2000},
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
                                        "Property": "Scorecard FY Volume (Bn)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Scorecard FY Volume (Bn)"
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
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="ANNUAL VOLUME (BILLION)",
                subtitle_text="FY25–26: 241.62 Bn | FY26–27 H1: 140.50 Bn (6 mo)"
            )
        }
    })

    # KPI 2: FY Value (Lakh Cr INR)
    visuals.append({
        "name": "kpi_fy_latest_val",
        "position": {"x": 335, "y": 84, "z": 2100, "height": 84, "width": 299, "tabOrder": 2100},
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
                                        "Property": "Scorecard FY Value (Lakh Cr INR)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Scorecard FY Value (Lakh Cr INR)"
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
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="ANNUAL VALUE (LAKH CR)",
                subtitle_text="FY25–26: ₹314.23L Cr | FY26–27 H1: ₹176.93L Cr (6 mo)"
            )
        }
    })

    # KPI 3: FY Weighted Avg Ticket Size (INR)
    visuals.append({
        "name": "kpi_fy_ticket",
        "position": {"x": 646, "y": 84, "z": 2200, "height": 84, "width": 299, "tabOrder": 2200},
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
                                        "Property": "Scorecard FY Weighted Avg Ticket Size (INR)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Scorecard FY Weighted Avg Ticket Size (INR)"
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
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="AVG TICKET SIZE (INR)",
                subtitle_text="FY25–26: ₹1,300.54 | FY26–27 H1: ₹1,259.30"
            )
        }
    })

    # KPI 4: Member Banks
    visuals.append({
        "name": "kpi_fy_banks",
        "position": {"x": 957, "y": 84, "z": 2300, "height": 84, "width": 299, "tabOrder": 2300},
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
                                        "Property": "Scorecard FY Closing Bank Count"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Scorecard FY Closing Bank Count"
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
                "categoryLabels": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="CLOSING MEMBER BANKS",
                subtitle_text="FY25–26 close: 705 | Sep 2026: 756"
            )
        }
    })

    # 10. Annual Volume Clustered Column (x: 24, w: 400, y: 178, h: 234)
    visuals.append({
        "name": "chart_fy_volume",
        "position": {"x": 24, "y": 178, "z": 3000, "height": 234, "width": 400, "tabOrder": 3000},
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
                                        "Property": "FY Volume (Bn)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.FY Volume (Bn)"
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
                        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}},
                        "selector": {"metadata": "MonthlyMetrics.FY Volume (Bn)"}
                    },
                    {"properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#2DD4BF'"}}}}}}}
                ],
                "valueAxis": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "titleText": {"expr": {"Literal": {"Value": "'Annual Volume (Billion)'"}}},
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
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="Annual Transaction Volume Trajectory (Billions)",
                subtitle_text="FY16–17: 0.02 Bn | FY25–26: 241.62 Bn | FY26–27 H1: 140.50 Bn"
            )
        }
    })

    # 11. Annual Value Clustered Column (x: 440, w: 400, y: 178, h: 234)
    visuals.append({
        "name": "chart_fy_value",
        "position": {"x": 440, "y": 178, "z": 3100, "height": 234, "width": 400, "tabOrder": 3100},
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
                                        "Property": "FY Value (Lakh Cr INR)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.FY Value (Lakh Cr INR)"
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
                        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}},
                        "selector": {"metadata": "MonthlyMetrics.FY Value (Lakh Cr INR)"}
                    },
                    {"properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#A78BFA'"}}}}}}}
                ],
                "valueAxis": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "titleText": {"expr": {"Literal": {"Value": "'Annual Value (Lakh Cr INR)'"}}},
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
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="Annual Transaction Value Trajectory (Lakh Cr INR)",
                subtitle_text="FY16–17: ₹0.07L Cr | FY25–26: ₹314.23L Cr | FY26–27 H1: ₹176.93L Cr"
            )
        }
    })

    # 12. Annual Average Ticket Size Trend (lineChart, x: 856, w: 400, y: 178, h: 234)
    visuals.append({
        "name": "chart_fy_ticket_trend",
        "position": {"x": 856, "y": 178, "z": 3200, "height": 234, "width": 400, "tabOrder": 3200},
        "visual": {
            "visualType": "lineChart",
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
                                        "Property": "FY Weighted Avg Ticket Size (INR)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.FY Weighted Avg Ticket Size (INR)"
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
                        "properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#38BDF8'"}}}}}},
                        "selector": {"metadata": "MonthlyMetrics.FY Weighted Avg Ticket Size (INR)"}
                    },
                    {"properties": {"fill": {"solid": {"color": {"expr": {"Literal": {"Value": "'#38BDF8'"}}}}}}}
                ],
                "lines": [
                    {
                        "properties": {"lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#38BDF8'"}}}}}},
                        "selector": {"metadata": "MonthlyMetrics.FY Weighted Avg Ticket Size (INR)"}
                    },
                    {"properties": {"lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#38BDF8'"}}}}}}}
                ],
                "valueAxis": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "titleText": {"expr": {"Literal": {"Value": "'Weighted Avg Ticket (INR)'"}}},
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
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="Annual Weighted Average Ticket Size (INR)",
                subtitle_text="FY16–17: ₹3,892.58 | FY25–26: ₹1,300.54 | FY26–27 H1: ₹1,259.30"
            )
        }
    })

    # 13. Annual Scorecard Matrix Table (tableEx, x: 24, y: 424, w: 888, h: 234)
    visuals.append({
        "name": "table_fy_scorecard",
        "position": {"x": 24, "y": 424, "z": 4000, "height": 234, "width": 888, "tabOrder": 4000},
        "visual": {
            "visualType": "tableEx",
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
                                "queryRef": "DimFinancialYear.FinancialYear",
                                "displayName": "Financial Year"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "FY Months Available"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.FY Months Available",
                                "displayName": "Months"
                            },
                            {
                                "field": {
                                    "Column": {
                                        "Expression": {"SourceRef": {"Entity": "DimFinancialYear"}},
                                        "Property": "Status"
                                    }
                                },
                                "queryRef": "DimFinancialYear.Status",
                                "displayName": "Period Status"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "FY Volume (Bn)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.FY Volume (Bn)",
                                "displayName": "Volume (Bn)"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "FY Value (Lakh Cr INR)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.FY Value (Lakh Cr INR)",
                                "displayName": "Value (Lakh Cr)"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "FY Weighted Avg Ticket Size (INR)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.FY Weighted Avg Ticket Size (INR)",
                                "displayName": "Avg Ticket (INR)"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "FY Volume YoY Growth %"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.FY Volume YoY Growth %",
                                "displayName": "Vol YoY %"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "FY Value YoY Growth %"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.FY Value YoY Growth %",
                                "displayName": "Val YoY %"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "FY Opening Bank Count"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.FY Opening Bank Count",
                                "displayName": "Open Banks"
                            },
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "MonthlyMetrics"}},
                                        "Property": "FY Closing Bank Count"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.FY Closing Bank Count",
                                "displayName": "Close Banks"
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
                "columnHeaders": [
                    {
                        "properties": {
                            "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#F3F6FC'"}}}}},
                            "backColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1E293B'"}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "9D"}}},
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
                            "fontSize": {"expr": {"Literal": {"Value": "8.5D"}}},
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
                "total": [{"properties": {"totals": {"expr": {"Literal": {"Value": "false"}}}}}],
                "totals": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}],
                "columnWidth": [
                    {"properties": {"width": {"expr": {"Literal": {"Value": "95D"}}}}, "selector": {"metadata": "DimFinancialYear.FinancialYear"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "55D"}}}}, "selector": {"metadata": "MonthlyMetrics.FY Months Available"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "120D"}}}}, "selector": {"metadata": "DimFinancialYear.Status"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "95D"}}}}, "selector": {"metadata": "MonthlyMetrics.FY Volume (Bn)"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "105D"}}}}, "selector": {"metadata": "MonthlyMetrics.FY Value (Lakh Cr INR)"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "100D"}}}}, "selector": {"metadata": "MonthlyMetrics.FY Weighted Avg Ticket Size (INR)"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "84D"}}}}, "selector": {"metadata": "MonthlyMetrics.FY Volume YoY Growth %"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "84D"}}}}, "selector": {"metadata": "MonthlyMetrics.FY Value YoY Growth %"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "75D"}}}}, "selector": {"metadata": "MonthlyMetrics.FY Opening Bank Count"}},
                    {"properties": {"width": {"expr": {"Literal": {"Value": "75D"}}}}, "selector": {"metadata": "MonthlyMetrics.FY Closing Bank Count"}}
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="Annual Financial-Year Scorecard & Matrix (FY 2016–17 to FY 2026–27)",
                subtitle_text="Verified NPCI records · FY 2026–27 H1 covers Apr–Sep 2026 (partial)"
            )
        }
    })

    # 14. Analytical Comparison Panel (Freed space beside table: x: 924, y: 424, w: 332, h: 234)
    visuals.append({
        "name": "panel_fy_trajectory",
        "position": {"x": 924, "y": 424, "z": 4100, "height": 234, "width": 332, "tabOrder": 4100},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {"value": "H1 MOMENTUM vs FULL-YEAR BASELINE\n", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "8.5pt", "fontWeight": "bold", "color": "#2DD4BF"}},
                                        {"value": "• Volume Pace: ", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "8pt", "color": "#F3F6FC"}},
                                        {"value": "FY 26–27 H1 (140.50 Bn) delivered 58.1% of FY 25–26 full-year peak (241.62 Bn) in just 6 months.\n", "textStyle": {"fontFamily": "Segoe UI", "fontSize": "8pt", "color": "#CBD5E1"}},
                                        {"value": "• Value Velocity: ", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "8pt", "color": "#F3F6FC"}},
                                        {"value": "H1 value reached ₹176.93 Lakh Cr (56.3% of FY 25–26 full-year ₹314.23L Cr).\n", "textStyle": {"fontFamily": "Segoe UI", "fontSize": "8pt", "color": "#CBD5E1"}},
                                        {"value": "• Ticket Size Drift: ", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "8pt", "color": "#F3F6FC"}},
                                        {"value": "Weighted ticket moderated from ₹1,300.54 (FY 25–26) to ₹1,259.30 in H1 (-3.2%).\n", "textStyle": {"fontFamily": "Segoe UI", "fontSize": "8pt", "color": "#CBD5E1"}},
                                        {"value": "• Member Banks: ", "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "8pt", "color": "#F3F6FC"}},
                                        {"value": "Live banks grew from 705 (March 2026 close) to 756 in Sep 2026 (+51 banks added).", "textStyle": {"fontFamily": "Segoe UI", "fontSize": "8pt", "color": "#CBD5E1"}}
                                    ]
                                }
                            ]
                        }
                    }
                ]
            },
            "visualContainerObjects": get_container_formatting(
                title_text="FISCAL TRAJECTORY ANALYSIS",
                subtitle_text="FY 2025–26 Baseline vs FY 2026–27 H1"
            )
        }
    })

    # 15. Footnote (y: 668, h: 44, bottom: 712)
    visuals.append({
        "name": "footer_note_p3",
        "position": {"x": 24, "y": 668, "z": 5000, "height": 44, "width": 1232, "tabOrder": 5000},
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
                                            "value": "Source: NPCI UPI statistics, Apr 2016–Sep 2026. Same-account debit/credit transactions excluded from Aug 2018 onwards. FY 2026–27 is partial (Apr–Sep, six months); incomplete-year YoY is withheld.",
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

    return visuals


def validate_report_schemas():
    """Validate all generated report definitions and visual containers against Fabric schemas."""
    print("\n" + "=" * 60)
    print("RUNNING SCHEMA VALIDATION ACROSS ALL REPORT DEFINITIONS")
    print("=" * 60)

    # Load schemas from cache
    def load_cached(fname):
        with open(os.path.join(SCHEMA_CACHE_DIR, fname), "r", encoding="utf-8") as f:
            return json.load(f)

    vc_schema = load_cached("visualContainer_schema.json")
    emb_schema = load_cached("visualConfiguration_schema-embedded.json")
    sq_schema = load_cached("semanticQuery_schema.json")
    fmt_schema = load_cached("formattingObjectDefinitions_schema.json")
    page_schema = load_cached("page_schema.json")
    rep_schema = load_cached("report_schema.json")
    meta_schema = load_cached("pagesMetadata_schema.json")
    flt_schema = load_cached("filterConfiguration_schema-embedded.json")

    store = {
        VC_SCHEMA_URL: vc_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualConfiguration/2.0.0/schema.embedded.json": emb_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualConfiguration/2.0.0/schema-embedded.json": emb_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/semanticQuery/1.2.0/schema.json": sq_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/formattingObjectDefinitions/1.3.0/schema.json": fmt_schema,
        PAGE_SCHEMA_URL: page_schema,
        REPORT_SCHEMA_URL: rep_schema,
        PAGES_META_SCHEMA_URL: meta_schema,
        FILTER_SCHEMA_URL: flt_schema,
        "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/filterConfiguration/1.1.0/schema.embedded.json": flt_schema
    }

    resolver = jsonschema.validators.RefResolver(base_uri=VC_SCHEMA_URL, referrer=vc_schema, store=store)

    # 1. Validate report.json
    rep_path = os.path.join(DEF_DIR, "report.json")
    with open(rep_path, "r", encoding="utf-8") as f:
        rep_data = json.load(f)
    jsonschema.validate(rep_data, rep_schema)
    print("  [PASS] report.json validates against Fabric report schema")

    # 1b. Validate version.json
    ver_schema = load_cached("versionMetadata_schema.json")
    ver_path = os.path.join(DEF_DIR, "version.json")
    with open(ver_path, "r", encoding="utf-8") as f:
        ver_data = json.load(f)
    jsonschema.validate(ver_data, ver_schema)
    print("  [PASS] version.json validates against Fabric versionMetadata schema")

    # 2. Validate pages.json
    pages_meta_path = os.path.join(PAGES_DIR, "pages.json")
    with open(pages_meta_path, "r", encoding="utf-8") as f:
        pages_meta = json.load(f)
    jsonschema.validate(pages_meta, meta_schema)
    print("  [PASS] pages.json validates against Fabric pagesMetadata schema")

    # 3. Validate each page and its visuals
    total_visuals = 0
    for page_name in pages_meta["pageOrder"]:
        page_dir = os.path.join(PAGES_DIR, page_name)
        page_json_path = os.path.join(page_dir, "page.json")
        with open(page_json_path, "r", encoding="utf-8") as f:
            p_data = json.load(f)
        jsonschema.validate(p_data, page_schema)
        print(f"  [PASS] {page_name}/page.json validates against Fabric page schema")

        vis_dir = os.path.join(page_dir, "visuals")
        for v_name in sorted(os.listdir(vis_dir)):
            v_file = os.path.join(vis_dir, v_name, "visual.json")
            with open(v_file, "r", encoding="utf-8") as f:
                v_data = json.load(f)
            jsonschema.validate(v_data, vc_schema, resolver=resolver)
            total_visuals += 1
            print(f"    [PASS] {page_name} / {v_name:<28} ({v_data['visual']['visualType']})")

    print(f"\nALL {total_visuals} VISUAL CONTAINERS VALIDATED SUCCESSFULLY AGAINST OFFICIAL FABRIC SCHEMAS!\n")


def audit_report_layout():
    """Audit geometry, checking for overlaps and bounding bounds across all pages."""
    print("=" * 60)
    print("AUDITING REPORT GEOMETRY & BOUNDING BOX DISJOINTNESS")
    print("=" * 60)

    pages_json_path = os.path.join(PAGES_DIR, "pages.json")
    with open(pages_json_path, "r", encoding="utf-8") as f:
        pages_meta = json.load(f)

    all_clean = True
    for page_name in pages_meta.get("pageOrder", []):
        vis_dir = os.path.join(PAGES_DIR, page_name, "visuals")
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
        print(f"\n--- Page: {page_name} (Visuals: {len(visuals)}) ---")
        for v in visuals:
            print(f"  {v['name']:<28} | {v['type']:<22} | x={v['x']:<4} y={v['y']:<4} w={v['w']:<5} h={v['h']:<4} | right={v['right']:<5} bottom={v['bottom']:<5}")

        # Check overlaps
        overlaps = []
        for i in range(len(visuals)):
            for j in range(i + 1, len(visuals)):
                v1 = visuals[i]
                v2 = visuals[j]
                if (v1["x"] < v2["right"] and v1["right"] > v2["x"] and
                    v1["y"] < v2["bottom"] and v1["bottom"] > v2["y"]):
                    overlaps.append((v1["name"], v2["name"]))

        # Check bounds
        canvas_w, canvas_h = 1280, 720
        out_of_bounds = []
        for v in visuals:
            if v["x"] < 0 or v["y"] < 0 or v["right"] > canvas_w or v["bottom"] > canvas_h:
                out_of_bounds.append(v["name"])

        if overlaps:
            print(f"  [FAIL] OVERLAPS DETECTED: {overlaps}")
            all_clean = False
        else:
            print("  [PASS] OVERLAPS: NONE (All bounding boxes strictly disjoint)")

        if out_of_bounds:
            print(f"  [FAIL] OUT OF BOUNDS: {out_of_bounds}")
            all_clean = False
        else:
            print("  [PASS] BOUNDS: NONE (All visuals strictly inside 1280x720 canvas)")

    print("\n" + "=" * 60)
    print("LAYOUT AUDIT RESULT:", "ALL PAGES CLEAN AND VALIDATED" if all_clean else "ERRORS DETECTED")
    print("=" * 60 + "\n")
    return all_clean


def main():
    print("Starting generation of upi_growth_analysis_final report...")
    setup_theme_and_report_json()

    # Setup pages.json
    os.makedirs(PAGES_DIR, exist_ok=True)
    pages_meta = {
        "$schema": PAGES_META_SCHEMA_URL,
        "pageOrder": ["ExecutiveOverview", "GrowthAndAdoption", "FinancialYearPerformance"],
        "activePageName": "ExecutiveOverview"
    }
    with open(os.path.join(PAGES_DIR, "pages.json"), "w", encoding="utf-8") as f:
        json.dump(pages_meta, f, indent=2)

    # 1. Page 1: ExecutiveOverview
    create_page_json(os.path.join(PAGES_DIR, "ExecutiveOverview"), "ExecutiveOverview", "Executive Overview")
    p1_visuals = build_page1_executive_overview()
    write_visuals("ExecutiveOverview", p1_visuals)

    # 2. Page 2: GrowthAndAdoption
    create_page_json(os.path.join(PAGES_DIR, "GrowthAndAdoption"), "GrowthAndAdoption", "Growth & Adoption")
    p2_visuals = build_page2_growth_adoption()
    write_visuals("GrowthAndAdoption", p2_visuals)

    # 3. Page 3: FinancialYearPerformance
    create_page_json(os.path.join(PAGES_DIR, "FinancialYearPerformance"), "FinancialYearPerformance", "Financial Year Performance")
    p3_visuals = build_page3_financial_year_performance()
    write_visuals("FinancialYearPerformance", p3_visuals)

    # Validate Schemas
    validate_report_schemas()

    # Audit Layout
    clean = audit_report_layout()
    if not clean:
        raise ValueError("Layout audit failed! Found overlaps or out of bounds visuals.")

    print("Successfully built and validated upi_growth_analysis_final 3-page report!")


if __name__ == "__main__":
    main()
