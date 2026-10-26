$ErrorActionPreference = "Stop"

$pbi = Get-Process -Name "PBIDesktop" | Sort-Object StartTime -Descending | Select-Object -First 1
$msmd = Get-CimInstance Win32_Process -Filter "Name = 'msmdsrv.exe'" | Where-Object { $_.ParentProcessId -eq $pbi.Id }
if (-not $msmd) {
    $msmd = Get-Process -Name "msmdsrv" | Select-Object -First 1
}
$port = (Get-NetTCPConnection -OwningProcess $msmd.ProcessId -State Listen | Where-Object { $_.LocalAddress -eq "127.0.0.1" } | Select-Object -First 1).LocalPort
Write-Host "Connected to msmdsrv PID: $($msmd.ProcessId) on Port: $port"

[System.Reflection.Assembly]::LoadFrom("C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.883.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;")
$conn.Open()
Write-Host "Database: $($conn.Database)"

$queries = @(
    @{
        Name = "1. UNFILTERED DEFAULT CONTEXT (Page 1 Cumulative & Page 3 Scorecard Default)"
        Dax = "EVALUATE ROW(
            `"P1_Cumulative_Vol_Bn`", [Total Volume (Bn)],
            `"P1_Cumulative_Val_LakhCr`", [Total Value (Lakh Cr INR)],
            `"P1_Weighted_Ticket_INR`", [Weighted Avg Ticket Size (INR)],
            `"P1_Live_Banks`", [Latest Bank Count],
            `"P3_Scorecard_Vol_Bn`", [Scorecard FY Volume (Bn)],
            `"P3_Scorecard_Val_LakhCr`", [Scorecard FY Value (Lakh Cr INR)],
            `"P3_Scorecard_Ticket_INR`", [Scorecard FY Weighted Avg Ticket Size (INR)],
            `"P3_Scorecard_Closing_Banks`", [Scorecard FY Closing Bank Count]
        )"
    },
    @{
        Name = "2. FY 2025-26 FILTERED CONTEXT (Latest Complete Financial Year)"
        Dax = "EVALUATE CALCULATETABLE(ROW(
            `"Scorecard_Vol_Bn`", [Scorecard FY Volume (Bn)],
            `"Scorecard_Val_LakhCr`", [Scorecard FY Value (Lakh Cr INR)],
            `"Scorecard_Ticket_INR`", [Scorecard FY Weighted Avg Ticket Size (INR)],
            `"Scorecard_Closing_Banks`", [Scorecard FY Closing Bank Count],
            `"Period_Status`", [FY Completeness Status]
        ), DimFinancialYear[FinancialYear] = `"2025-26`")"
    },
    @{
        Name = "3. FY 2026-27 FILTERED CONTEXT (Partial 6-Month Incomplete Year)"
        Dax = "EVALUATE CALCULATETABLE(ROW(
            `"Scorecard_Vol_Bn`", [Scorecard FY Volume (Bn)],
            `"Scorecard_Val_LakhCr`", [Scorecard FY Value (Lakh Cr INR)],
            `"Scorecard_Ticket_INR`", [Scorecard FY Weighted Avg Ticket Size (INR)],
            `"Scorecard_Closing_Banks`", [Scorecard FY Closing Bank Count],
            `"Period_Status`", [FY Completeness Status]
        ), DimFinancialYear[FinancialYear] = `"2026-27`")"
    }
)

foreach ($q in $queries) {
    Write-Host "`n============================================================"
    Write-Host $q.Name
    Write-Host "============================================================"
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = $q.Dax
    $reader = $cmd.ExecuteReader()
    $schema = $reader.GetSchemaTable()
    while ($reader.Read()) {
        for ($i = 0; $i -lt $reader.FieldCount; $i++) {
            $colName = $schema.Rows[$i]["ColumnName"]
            $val = $reader.GetValue($i)
            Write-Host "  $colName : $val"
        }
    }
    $reader.Close()
}
$conn.Close()
