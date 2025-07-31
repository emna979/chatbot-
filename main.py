from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import openai
import os
from dotenv import load_dotenv


# Charger la clé API depuis .env si besoin
load_dotenv()
openai.api_key = os.getenv("ap key")

app = FastAPI()

# Page d'accueil simple
@app.api_route("/", methods=["GET", "HEAD"])
def read_root():
    return {"message": "Bienvenue sur l'API du Chatbot Unilog"}

# Charger le contexte de la société Unilog
with open("data.txt", "r", encoding="utf-8") as f:
    company_context = f.read()

# Autoriser le CORS (important pour frontend HTML)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Remplace * par ton domaine si nécessaire
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèle de requête attendue
class ChatRequest(BaseModel):
    message: str

# Fonction de nettoyage des réponses
def nettoyer_reponse_brute(texte):
    if re.search(r'(\d{2} \d{3} \d{3})', texte):
        numero = re.search(r'(\d{2} \d{3} \d{3})', texte).group(1)
        return f"📞 Le numéro de téléphone de Unilog est : {numero}"

    if "poudrière" in texte.lower() or "adresse" in texte.lower():
        return "📍 L’adresse de Unilog est : Poudrières, Sfax, Tunisie."

    if "horaire" in texte.lower() or "quand" in texte.lower():
        return (
            "⏰ Horaires d’ouverture de Unilog :\n"
            "- Lundi à Jeudi : 9h00 – 18h00\n"
            "- Samedi : 9h00 – 13h00\n"
            "- Vendredi & Dimanche : fermé"
        )

    if "linkedin" in texte.lower() or "réseaux" in texte.lower():
        return "🔗 Voici le lien LinkedIn officiel de Unilog : [Unilog LinkedIn](https://www.linkedin.com/company/unilog-tn/)"

    return texte

# Appel OpenAI
def get_openai_response(question):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # ou "gpt-4"
        messages=[
            {"role": "system", "content": f"Voici les informations officielles de la société Unilog Sfax : {company_context}"},
            {"role": "user", "content": question}
        ]
    )
    return completion['choices'][0]['message']['content']

# Endpoint principal
@app.post("/chat")
async def chat(data: ChatRequest):
    question = data.message
    reponse_brute = get_openai_response(question)
    reponse_finale = nettoyer_reponse_brute(reponse_brute)
    return {"response": reponse_finale}


 
