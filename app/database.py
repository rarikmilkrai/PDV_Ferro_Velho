import sqlite3

def init_db():
    connection = sqlite3.connect('data/ferro_velho.db')
    cursor = connection.cursor()

    # Criar tabela de itens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL
        )
    ''')

    # Verificar se a tabela transacoes já existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transacoes'")
    table_exists = cursor.fetchone()

    if table_exists:
        # Renomear tabela transacoes existente para um nome temporário
        cursor.execute('ALTER TABLE transacoes RENAME TO transacoes_old')

        # Criar nova tabela de transações sem ON DELETE CASCADE
        cursor.execute('''
            CREATE TABLE transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                peso REAL NOT NULL,
                valor_pago REAL,
                data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                preco_transacao REAL,
                FOREIGN KEY(item_id) REFERENCES itens(id) ON DELETE SET NULL
            )
        ''')

        # Copiar dados da tabela antiga para a nova tabela
        cursor.execute('''
            INSERT INTO transacoes (id, item_id, peso, valor_pago, data_hora, preco_transacao)
            SELECT id, item_id, peso, valor_pago, data_hora, preco_transacao FROM transacoes_old
        ''')

        # Remover a tabela antiga
        cursor.execute('DROP TABLE transacoes_old')
    else:
        # Criar nova tabela de transações se não existir
        cursor.execute('''
            CREATE TABLE transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                peso REAL NOT NULL,
                valor_pago REAL,
                data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                preco_transacao REAL,
                FOREIGN KEY(item_id) REFERENCES itens(id) ON DELETE SET NULL
            )
        ''')

    connection.commit()
    connection.close()

    print("Banco de dados e tabelas criados com sucesso.")

if __name__ == '__main__':
    init_db()