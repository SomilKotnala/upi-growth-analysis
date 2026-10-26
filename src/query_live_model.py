"""
query_live_model.py
Queries the live Power BI Analysis Services instance by dynamically detecting its listening port.
"""
import subprocess
import re

ps_script = r"""
$ErrorActionPreference = "Stop"
# Find msmdsrv process
$msmd = Get-Process -Name "msmdsrv" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $msmd) {
    Write-Host "msmdsrv process not found!"
    exit 1
}
$port = (Get-NetTCPConnection -OwningProcess $msmd.Id -State Listen | Where-Object { $_.LocalAddress -eq "127.0.0.1" } | Select-Object -First 1).LocalPort
Write-Host "Detected msmdsrv PID: $($msmd.Id) listening on port: $port"

[System.Reflection.Assembly]::LoadFrom("C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.883.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.AdomdClient.dll") | Out-Null
$conn = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection("Data Source=localhost:$port;")
$conn.Open()
Write-Host "Connected successfully! Database: $($conn.Database)"

$queries = @(
    @{
        Name = "Executive Unfiltered Totals"
        Dax = "EVALUATE ROW(`"TotalVolBn`", [Total Volume (Bn)], `"TotalValLakhCr`", [Total Value (Lakh Cr INR)], `"TicketSize`", [Weighted Avg Ticket Size (INR)], `"LatestBanks`", [Latest Bank Count], `"LatestVolYoY`", [Latest Month Volume YoY Growth %], `"LatestValYoY`", [Latest Month Value YoY Growth %])"
    },
    @{
        Name = "FY 2025-26 Filtered Performance"
        Dax = "EVALUATE CALCULATETABLE(ROW(`"FYVolBn`", [Total Volume (Bn)], `"FYValLakhCr`", [Total Value (Lakh Cr INR)], `"FYTicket`", [Weighted Avg Ticket Size (INR)], `"Status`", [FY Completeness Status]), DimFinancialYear[FinancialYear] = `"2025-26`")"
    },
    @{
        Name = "FY 2026-27 Incomplete 6Mo Performance"
        Dax = "EVALUATE CALCULATETABLE(ROW(`"FYVolBn`", [Total Volume (Bn)], `"FYValLakhCr`", [Total Value (Lakh Cr INR)], `"FYTicket`", [Weighted Avg Ticket Size (INR)], `"Status`", [FY Completeness Status]), DimFinancialYear[FinancialYear] = `"2026-27`")"
    }
)

foreach ($q in $queries) {
    Write-Host "`n--- $($q.Name) ---"
    $cmd = $conn.CreateCommand()
    $cmd.CommandText = $q.Dax
    $reader = $cmd.ExecuteReader()
    $schema = $reader.GetSchemaTable()
    while ($reader.Read()) {
        for ($i = 0; $i -lt $reader.FieldCount; $i++) {
            $colName = $schema.Rows[$i]["ColumnName"]
            Write-Host "  $colName : $($reader[$i])"
        }
    }
    $reader.Close()
}
$conn.Close()
"""

ps_path = r"D:\upi-growth-analysis\src\run_adomd_query.ps1"
with open(ps_path, "w", encoding="utf-8") as f:
    f.write(ps_script)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_path], capture_output=True, text=True)
print("STDOUT:\n", res.stdout)
if res.stderr:
    print("STDERR:\n", res.stderr)
