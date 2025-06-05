"""
MFG Drone User Frontend
一般ユーザー用フロントエンド - リアルタイム映像表示
"""

from flask import Flask, render_template
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    return {"status": "healthy"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)