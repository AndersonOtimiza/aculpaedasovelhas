param(
  [Parameter(Mandatory=$true)][string]$Texto,
  [string]$Target = "default",
  [string]$Adapter = ""
)
$Body = @{
  text = $Texto
  target = $Target
}
if ($Adapter) {
  $Body.adapter = $Adapter
}
$Json = $Body | ConvertTo-Json -Depth 6
Invoke-RestMethod -Method Post -Uri http://localhost:8090/command -ContentType 'application/json' -Body $Json
