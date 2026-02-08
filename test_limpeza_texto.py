"""
Testa a limpeza de texto da IA
"""
from app.services.conhecimento.conhecimento_service import ConhecimentoService

# Texto com introdução da IA
texto_com_ia = """Com certeza! Para alimentar uma base de conhecimento de IA, a estrutura precisa ser clara, rica em detalhes e cobrir o máximo de cenários possíveis (as famosas "bordas" do atendimento).

Criei a Sorriso de Elite - Clínica Odontológica Integrada. O texto abaixo está estruturado para que a sua IA entenda não apenas os preços, mas a "personalidade" e as regras do negócio.

---

SORRISO DE ELITE - CLÍNICA ODONTOLÓGICA INTEGRADA

Informações Gerais:
Nome: Sorriso de Elite
Tipo: Clínica odontológica completa
Especialidades: Odontologia geral, estética, ortodontia, implantes, periodontia

Horário de Funcionamento:
Segunda a sexta: 08:00 às 19:00
Sábados: 08:00 às 13:00
Domingos e feriados: Fechado
"""

print("📝 TEXTO ORIGINAL:")
print("=" * 80)
print(texto_com_ia[:500])
print(f"\nTamanho: {len(texto_com_ia)} caracteres")

print("\n🧹 APLICANDO LIMPEZA...")
print("=" * 80)

texto_limpo = ConhecimentoService._limpar_texto_ia(texto_com_ia)

print("\n✨ TEXTO LIMPO:")
print("=" * 80)
print(texto_limpo[:500])
print(f"\nTamanho: {len(texto_limpo)} caracteres")

print("\n📊 RESULTADO:")
print("=" * 80)
print(f"Removido: {len(texto_com_ia) - len(texto_limpo)} caracteres")
print(f"Redução: {((len(texto_com_ia) - len(texto_limpo)) / len(texto_com_ia) * 100):.1f}%")

# Verificar se removeu as linhas da IA
linhas_ia_removidas = [
    "Com certeza!" in texto_com_ia and "Com certeza!" not in texto_limpo,
    "Criei a Sorriso" in texto_com_ia and "Criei a Sorriso" not in texto_limpo,
    "sua IA" in texto_com_ia and "sua IA" not in texto_limpo
]

print(f"\n✅ Linhas da IA removidas: {sum(linhas_ia_removidas)}/{len(linhas_ia_removidas)}")
print(f"✅ Conteúdo útil mantido: {'SORRISO DE ELITE' in texto_limpo}")
