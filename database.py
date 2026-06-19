import sqlite3
import os

DB_PATH = "fabrica.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ==============================
# CRIAÇÃO DAS TABELAS
# ==============================
def criar_tabelas():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS insumos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        quantidade REAL DEFAULT 0,
        custo_unitario REAL DEFAULT 0,
        unidade TEXT DEFAULT 'un',
        estoque_minimo REAL DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco_venda REAL DEFAULT 0,
        descricao TEXT DEFAULT ''
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receita (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        insumo_id INTEGER,
        quantidade REAL,
        FOREIGN KEY (produto_id) REFERENCES produtos(id),
        FOREIGN KEY (insumo_id) REFERENCES insumos(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS producao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        quantidade INTEGER,
        data_producao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimentacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        insumo_id INTEGER,
        tipo TEXT,
        quantidade REAL,
        data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        observacao TEXT DEFAULT '',
        FOREIGN KEY (insumo_id) REFERENCES insumos(id)
    )
    """)

    conn.commit()
    conn.close()

# ==============================
# INSUMOS
# ==============================
def cadastrar_insumo(nome, quantidade, custo, unidade, estoque_minimo):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO insumos (nome, quantidade, custo_unitario, unidade, estoque_minimo) VALUES (?, ?, ?, ?, ?)",
        (nome, quantidade, custo, unidade, estoque_minimo)
    )
    conn.commit()
    conn.close()

def entrada_estoque(insumo_id, quantidade, observacao=""):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE insumos SET quantidade = quantidade + ? WHERE id = ?",
        (quantidade, insumo_id)
    )
    cursor.execute(
        "INSERT INTO movimentacoes (insumo_id, tipo, quantidade, observacao) VALUES (?, 'ENTRADA', ?, ?)",
        (insumo_id, quantidade, observacao)
    )
    conn.commit()
    conn.close()

def listar_insumos():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM insumos ORDER BY nome")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def deletar_insumo(insumo_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM insumos WHERE id = ?", (insumo_id,))
    conn.commit()
    conn.close()

def atualizar_insumo(insumo_id, nome, custo, unidade, estoque_minimo):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE insumos SET nome=?, custo_unitario=?, unidade=?, estoque_minimo=? WHERE id=?",
        (nome, custo, unidade, estoque_minimo, insumo_id)
    )
    conn.commit()
    conn.close()

# ==============================
# PRODUTOS
# ==============================
def cadastrar_produto(nome, preco_venda, descricao=""):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO produtos (nome, preco_venda, descricao) VALUES (?, ?, ?)",
        (nome, preco_venda, descricao)
    )
    conn.commit()
    conn.close()

def listar_produtos():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos ORDER BY nome")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def deletar_produto(produto_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM receita WHERE produto_id = ?", (produto_id,))
    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    conn.commit()
    conn.close()

# ==============================
# RECEITA
# ==============================
def adicionar_receita(produto_id, insumo_id, quantidade):
    conn = get_conn()
    cursor = conn.cursor()
    # Evita duplicata
    cursor.execute(
        "SELECT id FROM receita WHERE produto_id=? AND insumo_id=?",
        (produto_id, insumo_id)
    )
    existe = cursor.fetchone()
    if existe:
        cursor.execute(
            "UPDATE receita SET quantidade=? WHERE produto_id=? AND insumo_id=?",
            (quantidade, produto_id, insumo_id)
        )
    else:
        cursor.execute(
            "INSERT INTO receita (produto_id, insumo_id, quantidade) VALUES (?, ?, ?)",
            (produto_id, insumo_id, quantidade)
        )
    conn.commit()
    conn.close()

def listar_receita(produto_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.id, i.nome, i.unidade, r.quantidade, i.custo_unitario,
               (r.quantidade * i.custo_unitario) as custo_total
        FROM receita r
        JOIN insumos i ON r.insumo_id = i.id
        WHERE r.produto_id = ?
    """, (produto_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def deletar_item_receita(receita_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM receita WHERE id = ?", (receita_id,))
    conn.commit()
    conn.close()

# ==============================
# CUSTO DO PRODUTO
# ==============================
def calcular_custo(produto_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.custo_unitario, r.quantidade
        FROM receita r
        JOIN insumos i ON r.insumo_id = i.id
        WHERE r.produto_id = ?
    """, (produto_id,))
    dados = cursor.fetchall()
    conn.close()
    return sum(row[0] * row[1] for row in dados)

# ==============================
# PRODUÇÃO
# ==============================
def verificar_estoque_producao(produto_id, quantidade):
    """Retorna lista de insumos com estoque insuficiente"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.nome, i.quantidade, r.quantidade * ? as necessario
        FROM receita r
        JOIN insumos i ON r.insumo_id = i.id
        WHERE r.produto_id = ?
    """, (quantidade, produto_id))
    rows = cursor.fetchall()
    conn.close()
    insuficientes = []
    for nome, estoque, necessario in rows:
        if estoque < necessario:
            insuficientes.append({
                "insumo": nome,
                "estoque": estoque,
                "necessario": necessario
            })
    return insuficientes

def produzir(produto_id, quantidade):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT insumo_id, quantidade FROM receita WHERE produto_id = ?
    """, (produto_id,))
    receita = cursor.fetchall()

    # Baixar estoque e registrar movimentação
    for insumo_id, qtd in receita:
        cursor.execute(
            "UPDATE insumos SET quantidade = quantidade - ? WHERE id = ?",
            (qtd * quantidade, insumo_id)
        )
        cursor.execute(
            "INSERT INTO movimentacoes (insumo_id, tipo, quantidade, observacao) VALUES (?, 'SAÍDA', ?, ?)",
            (insumo_id, qtd * quantidade, f"Produção: {quantidade} unidades do produto {produto_id}")
        )

    cursor.execute(
        "INSERT INTO producao (produto_id, quantidade) VALUES (?, ?)",
        (produto_id, quantidade)
    )
    conn.commit()
    conn.close()
    return True

# ==============================
# RELATÓRIOS
# ==============================
def relatorio_produtos():
    produtos = listar_produtos()
    resultado = []
    for p in produtos:
        custo = calcular_custo(p["id"])
        lucro = p["preco_venda"] - custo
        margem = (lucro / p["preco_venda"] * 100) if p["preco_venda"] > 0 else 0
        resultado.append({
            "id": p["id"],
            "nome": p["nome"],
            "custo": custo,
            "preco_venda": p["preco_venda"],
            "lucro": lucro,
            "margem": margem
        })
    return resultado

def historico_producao():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.nome as produto, pr.quantidade, pr.data_producao,
               (pr.quantidade * prod.preco_venda) as faturamento
        FROM producao pr
        JOIN produtos prod ON pr.produto_id = prod.id
        JOIN produtos p ON pr.produto_id = p.id
        ORDER BY pr.data_producao DESC
        LIMIT 50
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def historico_movimentacoes(insumo_id=None):
    conn = get_conn()
    cursor = conn.cursor()
    if insumo_id:
        cursor.execute("""
            SELECT i.nome, m.tipo, m.quantidade, m.data, m.observacao
            FROM movimentacoes m
            JOIN insumos i ON m.insumo_id = i.id
            WHERE m.insumo_id = ?
            ORDER BY m.data DESC LIMIT 50
        """, (insumo_id,))
    else:
        cursor.execute("""
            SELECT i.nome, m.tipo, m.quantidade, m.data, m.observacao
            FROM movimentacoes m
            JOIN insumos i ON m.insumo_id = i.id
            ORDER BY m.data DESC LIMIT 50
        """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def insumos_criticos():
    """Retorna insumos abaixo do estoque mínimo"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nome, quantidade, estoque_minimo, unidade
        FROM insumos
        WHERE quantidade <= estoque_minimo
        ORDER BY (quantidade - estoque_minimo) ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def totais_dashboard():
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM insumos")
    total_insumos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(quantidade) FROM producao")
    total_produzido = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT SUM(pr.quantidade * p.preco_venda)
        FROM producao pr
        JOIN produtos p ON pr.produto_id = p.id
    """)
    faturamento_total = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT COUNT(*) FROM insumos WHERE quantidade <= estoque_minimo
    """)
    alertas = cursor.fetchone()[0]

    conn.close()
    return {
        "total_insumos": total_insumos,
        "total_produtos": total_produtos,
        "total_produzido": total_produzido,
        "faturamento_total": faturamento_total,
        "alertas": alertas
    }

# Inicializa as tabelas ao importar
criar_tabelas()