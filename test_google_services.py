import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("1. TEST ENVOI EMAIL VIA GMAIL API (HTTPS PORT 443)")
print("=" * 60)
from tools.send_mail import send_email
res_mail = send_email(
    subject="[KWAME AI] Test Gmail API HTTPS Render Ready",
    message="Félicitations Gabin !\n\nL'authentification Google OAuth2 (Calendar, Drive, Gmail Send) fonctionne à 100% via l'API Gmail HTTPS sur le port 443.",
    confirmation="oui"
)
print("Résultat envoi Gmail API :")
print(res_mail)

print("\n" + "=" * 60)
print("2. TEST GOOGLE CALENDAR (CRÉATION, LISTE, SUPPRESSION)")
print("=" * 60)
from tools.calendar_manager import (
    create_event, get_todays_events, get_upcoming_events, 
    update_event, delete_event
)

# A. Créer un événement de test
print("\n--- A. Création événement ---")
create_res = create_event(
    title="Soutenance Assignment Agent IA",
    date="2026-10-25",
    start_time="10:00",
    end_time="11:00",
    description="Test de confirmation automatique et API Google Calendar"
)
print(create_res)

# B. Lister les événements
print("\n--- B. Liste des événements à venir ---")
upcoming_res = get_upcoming_events(7)
print(upcoming_res)

# Extraction de l'ID créé pour le test de suppression
import re
match = re.search(r"ID : `([^`]+)`", create_res)
if match:
    ev_id = match.group(1)
    print(f"\n--- C. Test refus suppression sans confirmation ---")
    del_unconf = delete_event(ev_id, confirmation="")
    print(del_unconf)

    print(f"\n--- D. Test suppression avec confirmation ---")
    del_conf = delete_event(ev_id, confirmation="oui")
    print(del_conf)

print("\n" + "=" * 60)
print("3. TEST GOOGLE DRIVE (LECTURE SEULE)")
print("=" * 60)
from tools.drive_tool import search_drive_tool
drive_res = search_drive_tool("", max_results=3)
print("Résultat Drive :")
print(drive_res)

print("\n" + "=" * 60)
print("TOUS LES SERVICES GOOGLE TESTÉS !")
print("=" * 60)
