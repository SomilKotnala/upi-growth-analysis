let
    Source = Csv.Document(File.Contents(EdaDirectory & "\financial_year_metrics.csv"),[Delimiter=",", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"fy_label", type text}, {"months_available", Int64.Type}, {"is_complete", type logical}, {"total_volume_mn", type number}, {"total_value_cr", type number}, {"weighted_avg_ticket_size_inr", type number}, {"opening_bank_count", Int64.Type}, {"closing_bank_count", Int64.Type}, {"yoy_volume_growth_pct", type number}, {"yoy_value_growth_pct", type number}})
in
    #"Changed Type"
