from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
import sqlite3

bp = Blueprint('routes', __name__)

# Rota para cadastrar um item
@bp.route('/itens', methods=['POST'])
def cadastrar_item():
    dados = request.json
    nome = dados.get('nome')
    preco = dados.get('preco')

    if not all([nome, preco]):
        return jsonify({"erro": "Campos obrigatórios: nome, preco"}), 400

    # Conectar ao banco e inserir o item
    connection = sqlite3.connect('data/ferro_velho.db')
    cursor = connection.cursor()

    # Verificar se o item já existe
    cursor.execute('SELECT id FROM itens WHERE nome = ?', (nome,))
    item_existente = cursor.fetchone()

    if item_existente:
        connection.close()
        return jsonify({"erro": f"Item '{nome}' já existe!"}), 400

    # Inserir o novo item no banco de dados
    cursor.execute('''
        INSERT INTO itens (nome, preco)
        VALUES (?, ?)
    ''', (nome, preco))
    connection.commit()
    connection.close()

    return jsonify({"mensagem": f"Item '{nome}' cadastrado com sucesso!"}), 201


@bp.route('/transacoes', methods=['POST'])
def registrar_transacao():
    dados = request.json
    nome_item = dados.get('nome_item')
    peso = dados.get('peso')

    if not all([nome_item, peso]):
        return jsonify({"erro": "Campos obrigatórios: nome_item, peso"}), 400

    # Conectar ao banco e buscar o preço do item pelo nome
    connection = sqlite3.connect('data/ferro_velho.db')
    cursor = connection.cursor()
    cursor.execute('SELECT id, preco FROM itens WHERE nome = ?', (nome_item,))
    item = cursor.fetchone()

    if not item:
        connection.close()
        return jsonify({"erro": "Item não encontrado!"}), 404

    item_id, preco_transacao = item  # Preço do item encontrado no banco

    # Calcular o valor a ser pago
    valor_pago = peso * preco_transacao  # Calcula o valor total a ser pago pela quantidade de peso

    # Insere a transação no banco de dados, incluindo o preço vigente e o valor pago
    cursor.execute('''
        INSERT INTO transacoes (item_id, peso, preco_transacao, valor_pago)
        VALUES (?, ?, ?, ?)
    ''', (item_id, peso, preco_transacao, valor_pago))
    connection.commit()
    connection.close()

    return jsonify({"mensagem": "Transação registrada com sucesso!"}), 201


# Rota para atualizar o preço de um item
@bp.route('/itens/<string:nome>', methods=['PUT'])
def atualizar_item(nome):
    dados = request.json
    novo_preco = dados.get('preco')

    if not novo_preco:
        return jsonify({"erro": "Campo obrigatório: preco"}), 400

    # Conectar ao banco de dados
    connection = sqlite3.connect('data/ferro_velho.db')
    cursor = connection.cursor()

    # Verificar se o item existe
    cursor.execute('SELECT id FROM itens WHERE nome = ?', (nome,))
    item = cursor.fetchone()

    if not item:
        connection.close()
        return jsonify({"erro": f"Item '{nome}' não encontrado!"}), 404

    # Atualizar o preço do item
    cursor.execute('UPDATE itens SET preco = ? WHERE nome = ?', (novo_preco, nome))
    connection.commit()
    connection.close()

    return jsonify({"mensagem": f"Preço do item '{nome}' atualizado para {novo_preco}!"}), 200


# Rota para listar todas as transações (GET)
@bp.route('/transacoes', methods=['GET'])
def listar_transacoes():
    connection = sqlite3.connect('data/ferro_velho.db')
    cursor = connection.cursor()

    cursor.execute(''' 
        SELECT t.id, i.nome AS item, t.preco_transacao, t.peso, t.valor_pago, t.data_hora 
        FROM transacoes t 
        JOIN itens i ON t.item_id = i.id
    ''')

    transacoes = cursor.fetchall()
    connection.close()

    deslocamento_fuso_horario = timedelta(hours=-3)

    resultado = []
    for t in transacoes:
        data_hora_utc = datetime.strptime(t[5], '%Y-%m-%d %H:%M:%S')
        data_hora_local = data_hora_utc + deslocamento_fuso_horario
        data_hora_local_str = data_hora_local.strftime('%Y-%m-%d %H:%M:%S')

        resultado.append({
            "id": t[0],
            "item": t[1],
            "preco_transacao": t[2],
            "peso": t[3],
            "valor_pago": t[4],
            "data_hora": data_hora_local_str
        })

    return jsonify(resultado)


# Rota para filtrar transações por período (POST)
@bp.route('/transacoes/filtro', methods=['POST'])
def filtrar_transacoes():
    dados = request.json
    data_inicial = dados.get('data_inicial')
    data_final = dados.get('data_final')

    # Verificar se as datas foram passadas corretamente
    if not all([data_inicial, data_final]):
        return jsonify({"erro": "Campos obrigatórios: data_inicial, data_final"}), 400

    # Converter as datas para o formato datetime
    try:
        data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d')
        data_final = datetime.strptime(data_final, '%Y-%m-%d')
    except ValueError:
        return jsonify({"erro": "Formato de data inválido. Use o formato 'YYYY-MM-DD'"}), 400

    connection = sqlite3.connect('data/ferro_velho.db')
    cursor = connection.cursor()

    # Monta a consulta SQL, agora usando a função DATE() para comparar apenas a data
    query = '''
        SELECT t.id, i.nome AS item, t.preco_transacao, t.peso, t.valor_pago, t.data_hora
        FROM transacoes t
        JOIN itens i ON t.item_id = i.id
        WHERE DATE(t.data_hora) BETWEEN ? AND ?
    '''

    # Ajustar as datas para o formato correto
    filtros = [data_inicial.strftime('%Y-%m-%d'), data_final.strftime('%Y-%m-%d')]

    cursor.execute(query, filtros)
    transacoes = cursor.fetchall()
    connection.close()

    deslocamento_fuso_horario = timedelta(hours=-3)

    resultado = []
    for t in transacoes:
        data_hora_utc = datetime.strptime(t[5], '%Y-%m-%d %H:%M:%S')
        data_hora_local = data_hora_utc + deslocamento_fuso_horario
        data_hora_local_str = data_hora_local.strftime('%Y-%m-%d %H:%M:%S')

        resultado.append({
            "id": t[0],
            "item": t[1],
            "preco_transacao": t[2],
            "peso": t[3],
            "valor_pago": t[4],
            "data_hora": data_hora_local_str
        })

    return jsonify(resultado)

# Rota para deletar uma transação por ID
@bp.route('/transacoes/<int:id>', methods=['DELETE'])
def deletar_transacao(id):
    connection = sqlite3.connect('data/ferro_velho.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM transacoes WHERE id = ?', (id,))
    connection.commit()
    connection.close()

    return jsonify({"mensagem": f"Transação com ID {id} deletada com sucesso!"}), 200


@bp.route('/itens/<string:nome>', methods=['DELETE'])
def deletar_item(nome):
    connection = sqlite3.connect('data/ferro_velho.db')
    cursor = connection.cursor()

    # Verificar se o item existe antes de tentar deletar
    cursor.execute('SELECT id FROM itens WHERE nome = ?', (nome,))
    item = cursor.fetchone()

    if not item:
        connection.close()
        return jsonify({"erro": f"Item '{nome}' não encontrado!"}), 404

    item_id = item[0]

    # Atualizar as transações associadas para remover a referência ao item
    cursor.execute('UPDATE transacoes SET item_id = NULL WHERE item_id = ?', (item_id,))

    # Deletar o item da tabela de itens
    cursor.execute('DELETE FROM itens WHERE nome = ?', (nome,))
    connection.commit()
    connection.close()

    return jsonify(
        {"mensagem": f"Item '{nome}' deletado com sucesso, mas as transações associadas não foram removidas!"}), 200
