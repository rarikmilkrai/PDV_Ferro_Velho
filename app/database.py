import os
import sqlite3


def init_db():
    if not os.path.exists('data'):
        os.makedirs('data')

    connection = sqlite3.connect('data/ferro_velho.db')
    cursor = connection.cursor()

    # Criação da tabela de itens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL
        )
    ''')

    # Remover tabela transacoes se ela já existir
    cursor.execute('DROP TABLE IF EXISTS transacoes')

    # Recriar a tabela de transações com a coluna 'item_id'
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            peso REAL NOT NULL,
            valor_pago REAL,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(item_id) REFERENCES itens(id)
        )
    ''')

    # Adicionar a coluna preco_transacao se ela não existir
    try:
        cursor.execute('ALTER TABLE transacoes ADD COLUMN preco_transacao REAL;')
        print("Coluna 'preco_transacao' adicionada com sucesso.")
    except sqlite3.OperationalError:
        print("A coluna 'preco_transacao' já existe ou ocorreu um erro.")

    connection.commit()
    connection.close()

    print("Banco de dados e tabelas criados com sucesso.")
