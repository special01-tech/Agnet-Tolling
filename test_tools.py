import sys
import os

# Forcer l'encodage UTF-8 pour la console Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

print("="*60)
print("1. TEST DE L'OUTIL TAVILY SEARCH")
print("="*60)
from tools.tavily_search import tavily_search
try:
    res_tavily = tavily_search("Actualites recentes intelligence artificielle 2026", max_results=2)
    print("Resultat Tavily :")
    print(res_tavily[:500] + "..." if len(res_tavily) > 500 else res_tavily)
except Exception as e:
    print(f"Erreur Tavily : {e}")

print("\n" + "="*60)
print("2. TEST DE L'OUTIL METEO (COTONOU)")
print("="*60)
from tools.weather_tool import get_weather
try:
    res_weather = get_weather("Cotonou")
    print("Resultat Meteo Cotonou :")
    print(res_weather)
except Exception as e:
    print(f"Erreur Meteo : {e}")

print("\n" + "="*60)
print("3. TEST DE SECURITE ET CONFIRMATION EMAIL")
print("="*60)
from tools.send_mail import create_email_draft, send_email

# Test A : Tentative d'envoi vers un destinataire non autorise
print("\n--- Test 3A : Destinataire pirate ou non autorise ---")
hack_res = send_email("hacker@example.com", "Test piratage", "Message", confirmation="oui")
print("Reponse attendue (refus) :")
print(hack_res)

# Test B : Tentative d'envoi sans confirmation
print("\n--- Test 3B : Envoi sans confirmation ---")
unconfirmed_res = send_email(subject="Test non confirme", message="Message", confirmation="")
print("Reponse attendue (blocage confirmation) :")
print(unconfirmed_res)

# Test C : Creation d'un brouillon propre
print("\n--- Test 3C : Creation du brouillon ---")
draft_res = create_email_draft("Sujet Test", "Bonjour, ceci est un email de test de l'Agent IA Personnel.")
print("Brouillon genere :")
print(draft_res)

# Test D : Envoi reel vers l'adresse autorisee avec confirmation explicite
print("\n--- Test 3D : Envoi reel avec confirmation explicite ---")
send_res = send_email(
    subject="[KWAME AI] Test de validation des outils",
    message="Bonjour Gabin,\n\nCeci est le test officiel de validation de l'envoi d'email avec confirmation pour l'assignment Agent IA Personnel.",
    confirmation="oui"
)
print("Resultat Envoi Email :")
print(send_res)

print("\n" + "="*60)
print("FIN DES TESTS")
print("="*60)
