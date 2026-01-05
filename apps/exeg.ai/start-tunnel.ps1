# Start Cloudflare Tunnel for exeg.ai + Bible API
#
# Pre-requisitos:
# 1. Tunnel configurado (ver cloudflared.yml)
# 2. Bible API rodando na porta 3001
# 3. exeg.ai rodando na porta 8000

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Cloudflare Tunnel - exeg.ai" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se os servicos estao rodando
Write-Host "Verificando servicos..." -ForegroundColor Yellow

# Verificar Bible API (3001)
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "[OK] Bible API (3001): Online" -ForegroundColor Green
} catch {
    Write-Host "[X] Bible API (3001): Offline" -ForegroundColor Red
    Write-Host "  Execute: cd 'apps/Biblia Belem AnC/belem-anc-traducao-api' && npm run dev" -ForegroundColor Gray
}

# Verificar exeg.ai (8000)
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "[OK] exeg.ai (8000): Online" -ForegroundColor Green
} catch {
    Write-Host "[X] exeg.ai (8000): Offline" -ForegroundColor Red
    Write-Host "  Execute: cd 'apps/exeg.ai' && python -m src.main" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Iniciando Cloudflare Tunnel..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Endpoints publicos:" -ForegroundColor Cyan
Write-Host "  - https://plataforma.exeg.ai" -ForegroundColor White
Write-Host "  - https://plataforma.exeg.ai/docs" -ForegroundColor White
Write-Host "  - https://biblia.aculpaedasovelhas.org" -ForegroundColor White
Write-Host ""

# Iniciar tunnel
cloudflared tunnel --config cloudflared.yml run exeg-ai
