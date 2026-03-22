import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'database': 'smart_parking_db',
    'user': 'root',
    'password': ''
}

def inserer_image():
    # 1. On ouvre l'image en mode "lecture binaire" (rb = read binary)
    try:
        with open('parking_test.jpg', 'rb') as file:
            photo_binaire = file.read()
    except FileNotFoundError:
        print("❌ Erreur : L'image 'parking_test.jpg' est introuvable dans le dossier.")
        return

    # 2. On se connecte à la base de données
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 3. On met à jour le tout premier parking de la liste pour lui ajouter la photo
        # On utilise LIMIT 1 pour juste tester sur un seul parking
        sql = "UPDATE parkings SET photo = %s LIMIT 1"
        cursor.execute(sql, (photo_binaire,))
        conn.commit()
        
        print("✅ Succès ! L'image a été convertie en BLOB et insérée dans la base de données.")
    except Exception as e:
        print(f"Erreur SQL : {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    inserer_image()