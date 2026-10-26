let
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
