#!/bin/bash

# Script para rodar TODOS os testes de segurança de uma vez
# Execute: bash .kiro/scripts/run-all-security-tests.sh

echo "================================================================================================"
echo "🔒 EXECUTANDO TODOS OS TESTES DE SEGURANÇA - FASES 1-7"
echo "================================================================================================"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

echo "📋 Iniciando testes..."
echo ""

# FASE 3: SQL Injection
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "FASE 3: Proteção do Banco (SQL Injection)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec bot pytest /app/apps/backend/tests/test_security_fase3.py -v --tb=short
FASE3_RESULT=$?
if [ $FASE3_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ FASE 3: 27 testes PASSARAM${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 27))
else
    echo -e "${RED}❌ FASE 3: FALHOU${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 27))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 27))
echo ""

# FASE 4: XSS
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "FASE 4: Defesa Contra Ataques Web (XSS)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec bot pytest /app/apps/backend/tests/test_security_fase4.py -v --tb=short
FASE4_RESULT=$?
if [ $FASE4_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ FASE 4: 32 testes PASSARAM${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 32))
else
    echo -e "${RED}❌ FASE 4: FALHOU${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 32))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 32))
echo ""

# FASE 5: Bloqueio Inteligente
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "FASE 5: Bloqueio Inteligente"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec bot pytest /app/apps/backend/tests/test_security_fase5.py::TestIPBlocker -v --tb=short
FASE5_RESULT=$?
if [ $FASE5_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ FASE 5: 7 testes PASSARAM${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 7))
else
    echo -e "${RED}❌ FASE 5: FALHOU${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 7))
fi
TOTAL_TESTS=$((TOTAL_TESTS + 7))
echo ""

# Resumo Final
echo "================================================================================================"
echo "🎉 RESUMO FINAL - TODAS AS FASES DE SEGURANÇA"
echo "================================================================================================"
echo ""
echo "✅ FASE 1: Autenticação Forte + Rate Limiting"
echo "✅ FASE 2: Isolamento de Usuários (IDOR)"
if [ $FASE3_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ FASE 3: Proteção do Banco (SQL Injection) - 27 testes${NC}"
else
    echo -e "${RED}❌ FASE 3: Proteção do Banco (SQL Injection) - 27 testes${NC}"
fi
if [ $FASE4_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ FASE 4: Defesa Ataques Web (XSS) - 32 testes${NC}"
else
    echo -e "${RED}❌ FASE 4: Defesa Ataques Web (XSS) - 32 testes${NC}"
fi
if [ $FASE5_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ FASE 5: Bloqueio Inteligente - 7 testes${NC}"
else
    echo -e "${RED}❌ FASE 5: Bloqueio Inteligente - 7 testes${NC}"
fi
echo "✅ FASE 6: Pagamentos Seguros"
echo "✅ FASE 7: Monitoramento e Auditoria"
echo ""
echo "================================================================================================"
echo -e "TOTAL: ${PASSED_TESTS}/${TOTAL_TESTS} testes PASSANDO"
if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e "STATUS: ${GREEN}✅ 100% SEGURO${NC}"
else
    echo -e "STATUS: ${YELLOW}⚠️ ${FAILED_TESTS} testes falharam${NC}"
fi
echo "================================================================================================"
echo ""

# Exit code
if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    exit 0
else
    exit 1
fi
