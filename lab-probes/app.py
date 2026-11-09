import os
from flask import Flask, jsonify
import psycopg

app = Flask(__name__)
unhealthy = False

@app.get('/health')
def health():
    if unhealthy:
        return jsonify(status='unhealthy'), 500
    return jsonify(status='ok'), 200

@app.get('/db')
def db():
    try:
        with psycopg.connect(
            host=os.getenv('DB_HOST', 'postgres-svc'),
            port=int(os.getenv('DB_PORT', '5432')),
            dbname=os.getenv('DB_NAME', 'postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.environ['DB_PASSWORD'],
            connect_timeout=3,
        ) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT NOW()')
                timestamp = cur.fetchone()[0]
        return jsonify(database_time=timestamp.isoformat())
    except (psycopg.Error, KeyError, ValueError) as exc:
        app.logger.warning('Database request failed: %s', type(exc).__name__)
        return jsonify(error='database unavailable'), 503

@app.post('/crash')
def crash():
    global unhealthy
    unhealthy = True
    return jsonify(status='simulated failure enabled')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
