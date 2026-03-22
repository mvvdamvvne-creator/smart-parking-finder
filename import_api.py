import requests
import mysql.connector
from mysql.connector import Error

# --- CONFIGURATION BASE DE DONNÉES ---
DB_CONFIG = {
    'host': 'localhost',
    'database': 'smart_parking_db',
    'user': 'root',
    'password': ''
}

def fetch_and_save_parkings():
    print("⏳ Connexion à l'API OpenStreetMap en cours...")
    
    # L'URL de l'API Overpass (OpenStreetMap)
    overpass_url = "http://overpass-api.de/api/interpreter"
    
   # La requête : On utilise le code ISO du Maroc (MA) pour cibler tout le pays
    # On ajoute un "timeout:180" car chercher dans tout le pays prend un peu plus de temps !
    overpass_query = """
    [out:json][timeout:180];
    area["ISO3166-1"="MA"][admin_level="2"]->.searchArea;
    (
      node["amenity"="parking"](area.searchArea);
      way["amenity"="parking"](area.searchArea);
      relation["amenity"="parking"](area.searchArea);
    );
    out center;
    """
    
    # On envoie la demande à l'API
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    
    elements = data.get('elements', [])
    print(f"✅ L'API a trouvé {len(elements)} parkings à Agadir !")
    
    # On se connecte à notre base de données MySQL
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        compteur = 0
        for element in elements:
            # On récupère le nom (s'il n'y a pas de nom, on l'appelle "Parking Public")
            tags = element.get('tags', {})
            nom = tags.get('name', 'Parking Public Agadir')
            
            # On récupère les coordonnées GPS (latitude et longitude)
            lat = element.get('lat') or element.get('center', {}).get('lat')
            lon = element.get('lon') or element.get('center', {}).get('lon')
            
            if lat and lon:
                # On insère les vraies données de l'API dans NOTRE base de données
                # On invente des valeurs par défaut pour les places et le prix car l'API ne donne pas ça en direct
                sql = """INSERT INTO parkings (nom, adresse, latitude, longitude, places_totales, places_dispo, tarif, est_couvert, est_gratuit) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                valeurs = (nom, "Agadir, Maroc", lat, lon, 100, 50, 10.00, False, False)
                
                try:
                    cursor.execute(sql, valeurs)
                    compteur += 1
                except Exception as e:
                    pass # On ignore si le parking existe déjà ou s'il y a une petite erreur
        
        conn.commit()
        print(f"🎉 Succès ! {compteur} vrais parkings du Maroc ont été ajoutés à la base de données.")
        
    except Error as e:
        print(f"Erreur MySQL : {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    fetch_and_save_parkings()