from flask import Flask, render_template, jsonify, request
import mysql.connector
from mysql.connector import Error
from decimal import Decimal
import base64

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
DB_CONFIG = {
    'host': 'localhost',
    'database': 'smart_parking_db',
    'user': 'root',
    'password': ''
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# --- WEB ROUTES (Serving your HTML pages) ---
@app.route('/')
@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/find-parking.html')
def find_parking():
    return render_template('find-parking.html')

@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/profile.html')
def profile():
    return render_template('profile.html')

@app.route('/reservation.html')
def reservation():
    return render_template('reservation.html')


# --- API ROUTES ---

@app.route('/api/parkings', methods=['GET'])
def api_get_parkings():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Erreur de connexion à la base de données"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM parkings LIMIT 50")
        parkings = cursor.fetchall()
        
        # On convertit les Decimal et les BLOBs pour que Flask puisse les lire
        for parking in parkings:
            for key, value in parking.items():
                if isinstance(value, Decimal):
                    parking[key] = float(value)
            
            # --- NOUVEAU : Traitement de la photo BLOB ---
            if parking.get('photo'):
                # On encode le BLOB binaire en texte Base64
                parking['photo'] = base64.b64encode(parking['photo']).decode('utf-8')
        
        return jsonify({"success": True, "parkings": parkings})
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"success": False, "message": "Erreur lors de la récupération des parkings"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    
    # Récupérer les infos envoyées par le formulaire
    nom = data.get('name')
    email = data.get('email')
    password = data.get('password')
    car_model = data.get('carModel', 'Conducteur standard') # Valeur par défaut
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Erreur de connexion à la base de données"}), 500

    cursor = conn.cursor()
    
    try:
        # On insère le nouvel utilisateur dans la base de données
        sql = """INSERT INTO utilisateurs (nom, email, mot_de_passe, modele_voiture) 
                 VALUES (%s, %s, %s, %s)"""
        valeurs = (nom, email, password, car_model)
        
        cursor.execute(sql, valeurs)
        conn.commit() # Valider l'insertion
        
        return jsonify({"success": True, "message": "Compte créé avec succès ! Vous pouvez maintenant vous connecter."})
        
    except mysql.connector.IntegrityError:
        # L'erreur "IntegrityError" se déclenche si l'email existe déjà
        return jsonify({"success": False, "message": "Cet email est déjà utilisé."}), 400
        
    finally:
        cursor.close()
        conn.close()


@app.route('/api/login', methods=['POST'])
def api_login():
    # On récupère les données envoyées par la page HTML
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Erreur de base de données"}), 500

    cursor = conn.cursor(dictionary=True)
    # On cherche l'utilisateur
    cursor.execute("SELECT * FROM utilisateurs WHERE email = %s AND mot_de_passe = %s", (email, password))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if user:
        # On supprime le mot de passe des données avant de les renvoyer au navigateur par sécurité
        user.pop('mot_de_passe', None)
        return jsonify({"success": True, "user": {"name": user['nom'], "carModel": user['modele_voiture'], "email": user['email']}})
    else:
        return jsonify({"success": False, "message": "Email ou mot de passe incorrect."}), 401


# --- START THE SERVER ---
# This MUST be at the very bottom of the file!
if __name__ == '__main__':
    app.run(debug=True, port=5000)