import requests

API_KEY = "AIzaSyAHobWluS8otx2r8zYGyWpuKD947_6ahII"
url = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"

response = requests.get(url)
if response.status_code == 200:
    models = response.json()
    print("--- MODÈLES DISPONIBLES POUR TA CLÉ ---")
    for m in models.get('models', []):
        print(f"- {m['name']}")
else:
    print(f"Erreur {response.status_code} : {response.text}")