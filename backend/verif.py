import requests
import json

# Ta nouvelle clé API
API_KEY = "AIzaSyCfnUsEQgKyI6fjR8BRks5oSBjSuu1qP4o"

# On teste 1.5 Flash (le plus compatible)
MODEL = "gemini-1.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

def tester_connexion():
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": "Bonjour ! Es-tu opérationnel pour le projet AgriTech ?"}]
        }]
    }

    print(f"--- Tentative avec le modèle : {MODEL} ---")
    
    try:
        response = requests.post(URL, headers=headers, data=json.dumps(data))
        result = response.json()
        
        if response.status_code == 200:
            texte = result['candidates'][0]['content']['parts'][0]['text']
            print("\n✅ SUCCÈS ! L'IA RÉPOND :")
            print("-" * 30)
            print(texte)
            print("-" * 30)
            print(f"\n👉 Dans ton app.py, utilise : '{MODEL}'")
            
        elif response.status_code == 404:
            print(f"\n❌ Le modèle {MODEL} n'est pas trouvé. Test du modèle 2.0-flash...")
            # On change juste le nom et on relance une fois
            nouvel_url = URL.replace("gemini-1.5-flash", "gemini-2.0-flash")
            r2 = requests.post(nouvel_url, headers=headers, data=json.dumps(data))
            print("Résultat 2.0-flash :", r2.status_code, r2.text[:100])

        elif response.status_code == 429:
            print("\n⚠️ QUOTA : Google limite encore les requêtes.")
            print("Patiente 2 minutes ou passe sur ta connexion mobile (4G).")
            
        else:
            print(f"\n❌ ERREUR {response.status_code} :", result)
            
    except Exception as e:
        print("\n❌ ERREUR TECHNIQUE :", e)

if __name__ == "__main__":
    tester_connexion()