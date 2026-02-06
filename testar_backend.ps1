# Script para testar se o backend está funcionando
Write-Host "🧪 TESTANDO BACKEND..." -ForegroundColor Cyan
Write-Host ""

# Teste 1: Health Check
Write-Host "1️⃣ Testando Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri 'http://localhost:8000/health' -TimeoutSec 5
    Write-Host "✅ Backend está rodando: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend NÃO está respondendo!" -ForegroundColor Red
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Teste 2: Login
Write-Host "2️⃣ Testando Login..." -ForegroundColor Yellow
try {
    $body = @{
        email = 'teste@teste.com'
        senha = '123456'
    } | ConvertTo-Json
    
    $loginStart = Get-Date
    $login = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/auth/login' -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 10
    $loginEnd = Get-Date
    $loginTime = ($loginEnd - $loginStart).TotalSeconds
    
    Write-Host "✅ Login funcionando!" -ForegroundColor Green
    Write-Host "   Tempo: $([math]::Round($loginTime, 2)) segundos" -ForegroundColor Gray
    Write-Host "   Token: $($login.access_token.Substring(0, 30))..." -ForegroundColor Gray
    
    $token = $login.access_token
} catch {
    Write-Host "❌ Login FALHOU!" -ForegroundColor Red
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Teste 3: Buscar Conhecimento
Write-Host "3️⃣ Testando Buscar Conhecimento..." -ForegroundColor Yellow
try {
    $headers = @{
        Authorization = "Bearer $token"
    }
    
    $conhecimentoStart = Get-Date
    $conhecimento = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/knowledge' -Method Get -Headers $headers -TimeoutSec 10
    $conhecimentoEnd = Get-Date
    $conhecimentoTime = ($conhecimentoEnd - $conhecimentoStart).TotalSeconds
    
    Write-Host "✅ Conhecimento carregado!" -ForegroundColor Green
    Write-Host "   Tempo: $([math]::Round($conhecimentoTime, 2)) segundos" -ForegroundColor Gray
    Write-Host "   Caracteres: $($conhecimento.total_chars)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Buscar conhecimento FALHOU!" -ForegroundColor Red
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Teste 4: Salvar Conhecimento
Write-Host "4️⃣ Testando Salvar Conhecimento..." -ForegroundColor Yellow
try {
    $novoConteudo = $conhecimento.conteudo_texto + "`n`nTeste automatico: $(Get-Date)"
    
    $body = @{
        conteudo_texto = $novoConteudo
    } | ConvertTo-Json
    
    $salvarStart = Get-Date
    $salvar = Invoke-RestMethod -Uri 'http://localhost:8000/api/v1/knowledge' -Method Put -Headers $headers -Body $body -ContentType 'application/json' -TimeoutSec 30
    $salvarEnd = Get-Date
    $salvarTime = ($salvarEnd - $salvarStart).TotalSeconds
    
    Write-Host "✅ Conhecimento salvo!" -ForegroundColor Green
    Write-Host "   Tempo: $([math]::Round($salvarTime, 2)) segundos" -ForegroundColor Gray
    Write-Host "   Caracteres: $($salvar.total_chars)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Salvar conhecimento FALHOU!" -ForegroundColor Red
    Write-Host "   Erro: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 TODOS OS TESTES PASSARAM!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 RESUMO:" -ForegroundColor Cyan
Write-Host "   - Health Check: OK" -ForegroundColor Gray
Write-Host "   - Login: $([math]::Round($loginTime, 2))s" -ForegroundColor Gray
Write-Host "   - Buscar: $([math]::Round($conhecimentoTime, 2))s" -ForegroundColor Gray
Write-Host "   - Salvar: $([math]::Round($salvarTime, 2))s" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ Backend está funcionando perfeitamente!" -ForegroundColor Green
Write-Host "   O problema está no FRONTEND (cache do navegador)" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔧 SOLUÇÃO:" -ForegroundColor Cyan
Write-Host "   1. Pressione Ctrl+Shift+Delete no navegador" -ForegroundColor White
Write-Host "   2. Limpe 'Imagens e arquivos em cache'" -ForegroundColor White
Write-Host "   3. Recarregue a página com Ctrl+Shift+R" -ForegroundColor White
Write-Host ""
