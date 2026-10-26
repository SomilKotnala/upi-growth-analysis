let
    Source = Csv.Document(File.Contents(EdaDirectory & "\monthly_metrics.csv"),[Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"month", type date}, {"bank_count", Int64.Type}, {"volume_mn", type number}, {"value_cr", type number}, {"avg_ticket_size_inr", type number}, {"prev_year_volume_mn", type number}, {"prev_year_value_cr", type number}, {"yoy_volume_growth_pct", type number}, {"yoy_value_growth_pct", type number}})
in
    #"Changed Type"
