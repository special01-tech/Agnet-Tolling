import os
import base64
from email.mime.text import MIMEText
from typing import Optional
from dotenv import load_dotenv

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]

def get_allowed_recipient() -> tuple[Optional[str], Optional[str]]:
    """Récupère et valide l'adresse email autorisée depuis les variables d'environnement."""
    allowed = os.getenv("ALLOWED_EMAIL_RECIPIENT")
    if not allowed or not allowed.strip():
        return None, "❌ Envoi bloqué : La variable d'environnement ALLOWED_EMAIL_RECIPIENT n'est pas définie dans le fichier .env."
    return allowed.strip().lower(), None

def get_gmail_service():
    """
    Construit le service Gmail API v1 via HTTPS (Port 443) à partir de
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET et GOOGLE_REFRESH_TOKEN (100% compatible Render).
    """
    refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    # Mode 1 : Variables d'environnement cloud (Render)
    if refresh_token and client_id and client_secret:
        try:
            creds = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=SCOPES
            )
            creds.refresh(Request())
            return build("gmail", "v1", credentials=creds)
        except Exception as e:
            print(f"⚠️ Erreur initialisation Gmail API via refresh_token: {e}")

    # Mode 2 : Fallback fichier local token.json
    if os.path.exists("token.json"):
        try:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            return build("gmail", "v1", credentials=creds)
        except Exception as e:
            print(f"⚠️ Erreur token.json Gmail: {e}")

    return None

def create_email_draft(subject: str, message: str, receiver_email: Optional[str] = None) -> str:
    """
    Prépare un brouillon d'email sans l'envoyer.
    Permet à l'utilisateur de vérifier le destinataire, l'objet et le contenu
    avant de donner sa confirmation explicite.
    """
    allowed_email, error = get_allowed_recipient()
    if error:
        return error

    target_email = receiver_email.strip().lower() if receiver_email else allowed_email
    if target_email != allowed_email:
        return (
            f"❌ Destinataire non autorisé : '{receiver_email}'. "
            f"Pour des raisons de sécurité, les emails ne peuvent être adressés qu'à '{allowed_email}'."
        )

    draft_view = (
        f"📝 **BROUILLON D'EMAIL PRÊT POUR CONFIRMATION**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📬 **Destinataire :** {target_email}\n"
        f"📌 **Objet :** {subject}\n"
        f"📄 **Message :**\n{message}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ **Cet email N'A PAS encore été envoyé.**\n"
        f"Veuillez répondre explicitement **« OUI »** ou **« CONFIRMER »** dans le chat pour procéder à l'envoi."
    )
    return draft_view

def send_email(receiver_email: Optional[str] = None, subject: str = "Subject", message: str = "", confirmation: str = "") -> str:
    """
    Envoie un email en utilisant l'API Gmail HTTPS (Port 443, non bloqué par Render)
    après vérification stricte de l'autorisation et de la confirmation explicite.
    """
    # 1. Vérification de la confirmation explicite
    valid_confirmations = {"oui", "yes", "confirmer", "valider", "confirm"}
    if not confirmation or confirmation.strip().lower() not in valid_confirmations:
        return (
            "⚠️ **Envoi bloqué : Confirmation obligatoire.**\n"
            "Vous devez d'abord présenter le brouillon et attendre que l'utilisateur confirme expressément par 'OUI' dans le chat."
        )

    # 2. Vérification de la liste blanche
    allowed_email, error = get_allowed_recipient()
    if error:
        return error

    target_email = receiver_email.strip().lower() if receiver_email else allowed_email
    if target_email != allowed_email:
        return (
            f"❌ Envoi refusé : Le destinataire '{receiver_email}' n'est pas autorisé. "
            f"Seul l'envoi vers l'adresse autorisée '{allowed_email}' est permis."
        )

    # 3. Connexion à l'API Gmail HTTPS
    service = get_gmail_service()
    if service is None:
        return (
            "❌ Service Gmail API non connecté. "
            "Assurez-vous que GOOGLE_REFRESH_TOKEN, GOOGLE_CLIENT_ID et GOOGLE_CLIENT_SECRET sont configurés dans votre .env."
        )

    # 4. Construction du message MIME avec disclaimer automatique
    disclaimer = "\n\n---\nThis is an automated email sent by an AI agent and can be subject of incoherence. Please verify the information before acting."
    full_message = message + disclaimer

    mime_msg = MIMEText(full_message)
    mime_msg["to"] = target_email
    mime_msg["subject"] = subject

    raw_message = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode("utf-8")

    try:
        sent = service.users().messages().send(
            userId="me",
            body={"raw": raw_message}
        ).execute()
        msg_id = sent.get("id", "N/A")
        return f"✅ Email envoyé avec succès via l'API Gmail HTTPS à {target_email} ! (ID: `{msg_id}`)"
    except Exception as e:
        return f"❌ Erreur lors de l'envoi via l'API Gmail : {str(e)}"

if __name__ == "__main__":
    print(create_email_draft("Test", "Bonjour", "test@test.com"))
