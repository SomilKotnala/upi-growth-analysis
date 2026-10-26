"""
Validates all required visual types for the Executive Overview page.
"""
import urllib.request
import json
import jsonschema

def main():
    vc_url = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json'
    emb_url = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualConfiguration/2.0.0/schema-embedded.json'
    sq_url = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/semanticQuery/1.2.0/schema.json'
    fmt_url = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/formattingObjectDefinitions/1.3.0/schema.json'
    page_url = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json'
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    get_json = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode())
    
    vc_schema = get_json(vc_url)
    emb_schema = get_json(emb_url)
    sq_schema = get_json(sq_url)
    fmt_schema = get_json(fmt_url)
    page_schema = get_json(page_url)
    
    store = {
        vc_url: vc_schema,
        emb_url: emb_schema,
        'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualConfiguration/2.0.0/schema.embedded.json': emb_schema,
        sq_url: sq_schema,
        'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/semanticQuery/1.2.0/schema.json': sq_schema,
        fmt_url: fmt_schema,
        'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/formattingObjectDefinitions/1.3.0/schema.json': fmt_schema,
        page_url: page_schema
    }
    
    resolver = jsonschema.validators.RefResolver(base_uri=vc_url, referrer=vc_schema, store=store)

    # 1. Line Chart
    line_chart = {
        "$schema": vc_url,
        "name": "chart_monthly_volume",
        "position": {"x": 24, "y": 202, "z": 2000, "height": 238, "width": 604, "tabOrder": 2000},
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
                                        "Property": "Total Volume (Mn)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Total Volume (Mn)"
                            }
                        ]
                    }
                }
            }
        }
    }
    jsonschema.validate(instance=line_chart, schema=vc_schema, resolver=resolver)
    print("SUCCESS: Line/Area chart valid!")

    # 2. Slicer
    slicer = {
        "$schema": vc_url,
        "name": "slicer_financial_year",
        "position": {"x": 1016, "y": 16, "z": 3000, "height": 56, "width": 240, "tabOrder": 3000},
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
                }
            }
        }
    }
    jsonschema.validate(instance=slicer, schema=vc_schema, resolver=resolver)
    print("SUCCESS: Slicer valid!")

    # 3. Textbox
    textbox = {
        "$schema": vc_url,
        "name": "header_title",
        "position": {"x": 24, "y": 16, "z": 1000, "height": 56, "width": 976, "tabOrder": 1000},
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
                                                "fontFamily": "Segoe UI",
                                                "fontSize": "16pt",
                                                "fontWeight": "bold",
                                                "color": "#F3F6FC"
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }
    jsonschema.validate(instance=textbox, schema=vc_schema, resolver=resolver)
    print("SUCCESS: Textbox valid!")

if __name__ == "__main__":
    main()

def test_page_objects():
    page_url = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json'
    fmt_url = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/formattingObjectDefinitions/1.5.0/schema.json'
    headers = {'User-Agent': 'Mozilla/5.0'}
    get_json = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode())

    page_schema = get_json(page_url)
    fmt_schema = get_json(fmt_url)

    store = {
        page_url: page_schema,
        fmt_url: fmt_schema
    }

    test_page = {
        "$schema": page_url,
        "name": "ExecutiveOverview",
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

    resolver = jsonschema.validators.RefResolver(base_uri=page_url, referrer=page_schema, store=store)
    jsonschema.validate(instance=test_page, schema=page_schema, resolver=resolver)
    print("SUCCESS: Page with custom dark background validated successfully!")

test_page_objects()

def test_container_formatting():
    vc_url = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.0.0/schema.json'
    emb_url = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualConfiguration/2.0.0/schema-embedded.json'
    sq_url = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/semanticQuery/1.2.0/schema.json'
    fmt_url = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/formattingObjectDefinitions/1.3.0/schema.json'
    headers = {'User-Agent': 'Mozilla/5.0'}
    get_json = lambda u: json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=headers)).read().decode())
    vc_schema = get_json(vc_url)
    emb_schema = get_json(emb_url)
    sq_schema = get_json(sq_url)
    fmt_schema = get_json(fmt_url)
    store = {
        vc_url: vc_schema,
        emb_url: emb_schema,
        'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualConfiguration/2.0.0/schema.embedded.json': emb_schema,
        sq_url: sq_schema,
        fmt_url: fmt_schema
    }
    card_with_bg = {
        "$schema": vc_url,
        "name": "kpi_total_volume",
        "position": {"x": 24, "y": 86, "z": 1000, "height": 104, "width": 236, "tabOrder": 1000},
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
                                        "Property": "Total Volume (Mn)"
                                    }
                                },
                                "queryRef": "MonthlyMetrics.Total Volume (Mn)"
                            }
                        ]
                    }
                }
            },
            "visualContainerObjects": {
                "background": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#131B2E'"}}}}},
                            "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                        }
                    }
                ],
                "border": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1E293B'"}}}}},
                            "radius": {"expr": {"Literal": {"Value": "6D"}}}
                        }
                    }
                ]
            }
        }
    }
    resolver = jsonschema.validators.RefResolver(base_uri=vc_url, referrer=vc_schema, store=store)
    jsonschema.validate(instance=card_with_bg, schema=vc_schema, resolver=resolver)
    print("SUCCESS: VisualContainerObjects background and border formatting validated!")

test_container_formatting()
