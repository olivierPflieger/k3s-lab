import os
from flask import Flask, jsonify
import psycopg
from flask import render_template_string

app = Flask(__name__)
unhealthy = False

@app.get("/")
def index():
    try:
        
        if unhealthy:
            return jsonify(status='unhealthy'), 500
        
        with psycopg.connect(
            host=os.environ["DB_HOST"],
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            connect_timeout=3
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, nom FROM produits ORDER BY id")
                produits = cur.fetchall()

        return render_template_string("""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Mon application K3s</title>
        </head>
        <body>
            <h1>Bienvenue dans mon application !</h1>
            <p>Voici les produits de PostgreSQL :</p>

            <table border="1" cellpadding="10">
                <tr>
                    <th>ID</th>
                    <th>Produit</th>
                </tr>
                {% for produit in produits %}
                <tr>
                    <td>{{ produit[0] }}</td>
                    <td>{{ produit[1] }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """, produits=produits)

    except Exception as e:
        app.logger.exception("Erreur PostgreSQL")
        return "Base de données indisponible", 503

@app.get('/health')
def health():
    if unhealthy:
        return jsonify(status='unhealthy'), 500
    return jsonify(status='ok'), 200

@app.post('/crash')
def crash():
    global unhealthy
    unhealthy = True
    return jsonify(status='simulated failure enabled')
    
@app.post('/uncrash')
def fixcrash():
    global unhealthy
    unhealthy = False
    return jsonify(status='simulated failure resolved. System ok ')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
