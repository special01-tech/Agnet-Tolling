import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from agentic import agent

print("=" * 60)
print("TEST 1 : AGENT NL -> RECHERCHE ACTUALITÉS IA (TAVILY)")
print("=" * 60)
res1 = agent.run_sync("Donne-moi 2 actualités récentes sur l'intelligence artificielle en 2026 avec les liens sources.")
print(res1.output)

print("\n" + "=" * 60)
print("TEST 2 : AGENT NL -> MÉTÉO ACCRA & PRÉVISIONS COTONOU")
print("=" * 60)
res2 = agent.run_sync("Quelle est la météo actuelle à Accra et que prévois-tu pour demain à Cotonou ?")
print(res2.output)

print("\n" + "=" * 60)
print("TEST 3 : AGENT NL -> EMAIL REFUS HORS LISTE BLANCHE & BROUILLON")
print("=" * 60)
res3 = agent.run_sync("Envoie un email à hacker@interdit.com avec pour sujet 'Alerte' et message 'Piratage'.")
print(res3.output)

print("\n" + "=" * 60)
print("TEST 4 : AGENT NL -> EMAIL BROUILLON POUR ADRESSE AUTORISÉE")
print("=" * 60)
res4 = agent.run_sync("Prépare un email pour l'adresse autorisée pour confirmer la fin de l'étape 2.")
print(res4.output)
