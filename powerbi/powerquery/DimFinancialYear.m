let
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
