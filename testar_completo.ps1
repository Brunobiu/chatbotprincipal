# Script de teste completo do sistema
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TESTE COMPLETO DO SISTEMA" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 1. Login
Write-Host "1️⃣ Testando Login..." -ForegroundColor Yellow
$body = @{
    email = "teste@teste.com"
    senha = "123456"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" -Method POST -Body $body -ContentType "application/json"
    $token = $response.access_token
    Write-Host "   ✅ Login OK" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Login FALHOU" -ForegroundColor Red
    exit 1
}

# 2. Salvar Conhecimento
Write-Host "`n2️⃣ Testando Salvar Conhecimento..." -ForegroundColor Yellow
$conhecimento = "Este é um teste completo do sistema. O conhecimento deve persistir no banco de dados após salvar. Vamos verificar se tudo está funcionando corretamente!"
$body2 = @{
    conteudo_texto = $conhecimento
} | ConvertTo-Json

try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/knowledge" -Method PUT -Body $body2 -ContentType "application/json" -Headers @{Authorization="Bearer $token"}
    Write-Host "   ✅ Salvou: $($response2.total_chars) caracteres" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Salvar FALHOU: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Buscar Conhecimento
Write-Host "`n3️⃣ Testando Buscar Conhecimento..." -ForegroundColor Yellow
Start-Sleep -Seconds 1
try {
    $response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/knowledge" -Method GET -Headers @{Authorization="Bearer $token"}
    Write-Host "   ✅ Recuperou: $($response3.total_chars) caracteres" -ForegroundColor Green
    
    if ($response3.total_chars -eq $conhecimento.Length) {
        Write-Host "   🎉 PERSISTIU CORRETAMENTE!" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Tamanho diferente do esperado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Buscar FALHOU" -ForegroundColor Red
}

# 4. Salvar Configurações
Write-Host "`n4️⃣ Testando Salvar Configurações..." -ForegroundColor Yellow
$config = @{
    tom = "formal"
    mensagem_saudacao = "Olá! Como posso ajudá-lo?"
    mensagem_fallback = "Desculpe, não tenho essa informação."
    mensagem_espera = "Aguarde um momento, por favor."
    mensagem_retorno_24h = "Olá! Posso ajudar agora?"
} | ConvertTo-Json

try {
    $response4 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/config" -Method PUT -Body $config -ContentType "application/json" -Headers @{Authorization="Bearer $token"}
    Write-Host "   ✅ Configurações salvas" -ForegroundColor Green
    Write-Host "   Tom: $($response4.tom)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Salvar configurações FALHOU: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Buscar Configurações
Write-Host "`n5️⃣ Testando Buscar Configurações..." -ForegroundColor Yellow
try {
    $response5 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/config" -Method GET -Headers @{Authorization="Bearer $token"}
    Write-Host "   ✅ Configurações recuperadas" -ForegroundColor Green
    Write-Host "   Tom: $($response5.tom)" -ForegroundColor Gray
    
    if ($response5.tom -eq "formal") {
        Write-Host "   🎉 CONFIGURAÇÕES PERSISTIRAM!" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Tom diferente do esperado" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Buscar configurações FALHOU" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TESTES CONCLUÍDOS!" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
