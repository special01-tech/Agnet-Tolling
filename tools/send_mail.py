import os
import smtplib
from email.mime.text import MIMEText
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

def get_allowed_recipient() -> tuple[Optional[str], Optional[str]]:
    """
    Récupère et valide l'adresse email autorisée depuis les variables d'environnement.
    Retourne (allowed_email, error_message).
    """
    allowed = os.getenv("ALLOWED_EMAIL_RECIPIENT")
    if not allowed or not allowed.strip():
        return None, "❌ Envoi bloqué : La variable d'environnement ALLOWED_EMAIL_RECIPIENT n'est pas définie dans le fichier .env."
    return allowed.strip().lower(), None


def create_email_draft(subject: str, message: str, receiver_email: Optional[str] = None) -> str:
    """
    Prépare un brouillon d'email sans l'envoyer.
    Permet à l'utilisateur de vérifier le destinataire, l'objet et le contenu
    avant de donner sa confirmation explicite.
    """
    allowed_email, error = get_allowed_recipient()
    if error:
        return error

    # Validation du destinataire par rapport à la liste blanche
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
    Envoie un email en utilisant SMTP après vérification stricte de l'autorisation
    et de la confirmation de l'utilisateur.
    
    Args:
        receiver_email (str, optionnel): Destinataire (doit correspondre à ALLOWED_EMAIL_RECIPIENT)
        subject (str): Sujet du mail
        message (str): Corps du message
        confirmation (str): Doit être explicitement 'oui', 'yes' ou 'confirmer'
        
    Returns:
        str: Message de statut
    """
    # 1. Vérification de la confirmation explicite
    valid_confirmations = {"oui", "yes", "confirmer", "valider", "confirm"}
    if not confirmation or confirmation.strip().lower() not in valid_confirmations:
        return (
            "⚠️ **Envoi bloqué : Confirmation obligatoire.**\n"
            "Vous devez d'abord présenter le brouillon et attendre que l'utilisateur confirme expressément par 'OUI' dans le chat."
        )

    # 2. Vérification de la liste blanche de destinataire
    allowed_email, error = get_allowed_recipient()
    if error:
        return error

    target_email = receiver_email.strip().lower() if receiver_email else allowed_email
    if target_email != allowed_email:
        return (
            f"❌ Envoi refusé : Le destinataire '{receiver_email}' n'est pas autorisé. "
            f"Seul l'envoi vers l'adresse autorisée '{allowed_email}' est permis."
        )

    # 3. Vérification des identifiants SMTP
    sender = (os.getenv("SMTP_EMAIL") or os.getenv("SMTP_USER") or "").strip()
    app_password = (os.getenv("SMTP_PASSWORD") or os.getenv("SMTP_APP_PASSWORD") or "").strip()
    smtp_server = (os.getenv("SMTP_SERVER") or "").strip() or "smtp.gmail.com"
    raw_port = (os.getenv("SMTP_PORT") or "").strip()
    smtp_port = int(raw_port) if raw_port.isdigit() else 465

    if not sender or not app_password:
        return "❌ Erreur configuration email: SMTP_EMAIL et/ou SMTP_PASSWORD manquant(s) dans le fichier .env."

    # 4. Préparation du message avec disclaimer automatique
    disclaimer = "\n\n---\nThis is an automated email sent by an AI agent and can be subject of incoherence. Please verify the information before acting."
    full_message = message + disclaimer
    
    msg = MIMEText(full_message)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = target_email
    
    # 5. Expédition sécurisée
    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender, app_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender, app_password)
                server.send_message(msg)

        return f"✅ Email envoyé avec succès à l'adresse autorisée {target_email} !"
    except Exception as e:
        return f"❌ Erreur lors de l'envoi de l'email: {str(e)}"

if __name__ == "__main__":
    print(create_email_draft("Test", "Bonjour", "test@test.com"))
