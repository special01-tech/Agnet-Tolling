# 🤖 KWAME AI - Agent PydanticAI avec Outils Intégrés

Un agent intelligent basé sur PydanticAI avec des outils intégrés pour la recherche web, la météo, l'extraction de contenu et la gestion du calendrier.

## 🚀 Fonctionnalités

### 🧠 Modèles IA Supportés
- **🦆 Llama 3.3 70b** - Rapide et efficace pour tâches quotidiennes
- **🧠 GPT 5.2** - Équilibré et puissant pour analyses complexes  
- **⚡ Gemini Flash** - Ultra-rapide pour réponses instantanées

### 🛠️ Outils Intégrés
- **🔍 Recherche Web** - Recherche en temps réel avec Tavily
- **🌤️ Météo** - Informations météo actuelles et prévisions
- **📄 Extraction Web** - Extraction et analyse de contenu d'articles
- **📅 Calendrier** - Gestion des événements (stockage local)
- **📧 Email** - Envoi d'emails automatiques via Gmail

### 🌐 Interface Web
- Interface web moderne et responsive
- Support multi-modèles
- Conversation en temps réel
- Historique des messages

## 📦 Installation

### Prérequis
- Python 3.8+
- Git

### Installation rapide
```bash
# Cloner le dépôt
git clone git@github.com:FredyHoundayi/pydantic-agent.git
cd pydantic-agent

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Configuration
1. Copier le fichier d'environnement :
```bash
cp .env.example .env
```

2. Configurer les clés API dans `.env` :
```env
# Clés API
GROQ_API_KEY=votre_clé_groq
TAVILY_API_KEY=votre_clé_tavily
GETWEATHER_API_KEY=votre_clé_meteo
GOOGLE_API_KEY=votre_clé_google

# Langfuse (optionnel)
LANGFUSE_SECRET_KEY=votre_secret_key
LANGFUSE_PUBLIC_KEY=votre_public_key
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

## 🚀 Lancement

### Interface Web
```bash
source venv/bin/activate
uvicorn agentic:app --host 0.0.0.0 --port 8000 --reload
```

L'interface sera accessible sur **http://localhost:8000**

### Docker
```bash
# Build and run with Docker
docker build -t kwame-ai .
docker run -p 8000:8000 --env-file .env kwame-ai
```

### Déploiement sur Render
1. Connecter votre dépôt GitHub à Render.com
2. Importer le dépôt `git@github.com:FredyHoundayi/pydantic-agent.git`
3. Render détectera automatiquement le Dockerfile
4. Configurer les variables d'environnement dans le dashboard Render
5. Déployer !

### Ligne de commande
```bash
source venv/bin/activate
python agentic.py
```

## 📚 Utilisation

### Recherche Web
```
"cherche les dernières nouvelles sur l'IA"
"trouve des informations sur Python"
```

### Météo
```
"météo à Paris"
"prévisions météo pour Londres"
```

### Extraction de contenu
```
"analyse l'article https://example.com"
"extrais le contenu de https://news.com/article"
```

### Calendrier
```
"montre mes événements aujourd'hui"
"crée un événement: Réunion le 2026-03-15 de 14:00 à 16:00"
"montre mes événements pour les 7 prochains jours"
```

### Email
```
"envoie un email à contact@example.com avec sujet Rapport et message Voici le rapport..."
```

## 📁 Structure du Projet

```
pydantic-agent/
├── agentic.py              # Fichier principal de l'agent
├── Dockerfile              # Configuration Docker pour Render
├── tools/                  # Outils intégrés
│   ├── calendar_manager.py  # Gestion du calendrier
│   ├── tavily_search.py    # Recherche web
│   ├── weather_tool.py     # Météo
│   ├── link_retriever.py   # Extraction web
│   └── send_mail.py       # Email
├── .env.example           # Configuration exemple
├── requirements.txt        # Dépendances
├── README.md             # Documentation
└── kwame_*.json         # Données locales (calendrier, emails)
```

## 🔧 Configuration des Outils

### Google Calendar (Optionnel)
Pour utiliser Google Calendar au lieu du stockage local :
1. Créer un projet Google Cloud
2. Activer l'API Google Calendar
3. Télécharger `credentials.json`
4. Placer le fichier à la racine du projet

### Gmail SMTP
L'outil email utilise Gmail SMTP avec :
- Serveur : `smtp.gmail.com:465`
- Authentification par app password

## 🐛 Dépannage

### Problèmes courants
- **Import errors** : Vérifiez que toutes les dépendances sont installées
- **API keys** : Assurez-vous que les clés API sont correctes dans `.env`
- **Calendar errors** : Si Google Calendar n'est pas configuré, l'agent utilise le stockage JSON local

### Logs
Les logs sont sauvegardés dans `kwame_ai.log` pour le débogage.

## 🤝 Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à :
- Reporter des bugs
- Proposer des améliorations
- Ajouter de nouveaux outils

## 📄 Licence

Ce projet est sous licence MIT.

## 👨‍💻 Auteur

Créé par **Fredy Houndayi** - Agent intelligent KWAME AI

---

🚀 **KWAME AI est prêt à vous aider avec tous vos projets !**
