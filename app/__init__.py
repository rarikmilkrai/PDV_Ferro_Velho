from flask import Flask
from app.database import init_db  # Função para inicializar o banco
from app.routes import bp         # Blueprint para rotas

def create_app():
    app = Flask(__name__)

    # Configurações do banco de dados SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data/ferro_velho.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa o banco de dados
    init_db()

    # Registra o Blueprint das rotas
    app.register_blueprint(bp)

    return app
