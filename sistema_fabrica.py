import sqlite3

# ==============================
# CONEXÃO COM BANCO
# ==============================
conn = sqlite3.connect("fabrica.db")
cursor = conn.cursor()

# ==============================
# CRIAÇÃO DAS TABELAS
# ==============================
def criar_tabelas():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS insumos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        quantidade REAL,
        custo_unitario REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        preco_venda REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receita (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        insumo_id INTEGER,
        quantidade REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS producao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        quantidade INTEGER
    )
    """)

    conn.commit()

# ==============================
# INSUMOS
# ==============================
def cadastrar_insumo(nome, quantidade, custo):
    cursor.execute("INSERT INTO insumos (nome, quantidade, custo_unitario) VALUES (?, ?, ?)",
                   (nome, quantidade, custo))
    conn.commit()

def entrada_estoque(insumo_id, quantidade):
    cursor.execute("UPDATE insumos SET quantidade = quantidade + ? WHERE id = ?",
                   (quantidade, insumo_id))
    conn.commit()

def listar_insumos():
    cursor.execute("SELECT * FROM insumos")
    return cursor.fetchall()

# ==============================
# PRODUTOS
# ==============================
def cadastrar_produto(nome, preco_venda):
    cursor.execute("INSERT INTO produtos (nome, preco_venda) VALUES (?, ?)",
                   (nome, preco_venda))
    conn.commit()

def listar_produtos():
    cursor.execute("SELECT * FROM produtos")
    return cursor.fetchall()

# ==============================
# RECEITA (COMPOSIÇÃO DO PRODUTO)
# ==============================
def adicionar_receita(produto_id, insumo_id, quantidade):
    cursor.execute("INSERT INTO receita (produto_id, insumo_id, quantidade) VALUES (?, ?, ?)",
                   (produto_id, insumo_id, quantidade))
    conn.commit()

# ==============================
# CALCULAR CUSTO DO PRODUTO
# ==============================
def calcular_custo(produto_id):
    cursor.execute("""
    SELECT i.custo_unitario, r.quantidade
    FROM receita r
    JOIN insumos i ON r.insumo_id = i.id
    WHERE r.produto_id = ?
    """, (produto_id,))
    
    dados = cursor.fetchall()
    custo_total = sum(custo * qtd for custo, qtd in dados)
    
    return custo_total

# ==============================
# PRODUÇÃO
# ==============================
def produzir(produto_id, quantidade):
    # Buscar receita
    cursor.execute("""
    SELECT insumo_id, quantidade
    FROM receita
    WHERE produto_id = ?
    """, (produto_id,))
    
    receita = cursor.fetchall()

    # Verificar estoque
    for insumo_id, qtd in receita:
        cursor.execute("SELECT quantidade FROM insumos WHERE id = ?", (insumo_id,))
        estoque = cursor.fetchone()[0]

        if estoque < qtd * quantidade:
            print("Estoque insuficiente!")
            return

    # Baixar estoque
    for insumo_id, qtd in receita:
        cursor.execute("""
        UPDATE insumos 
        SET quantidade = quantidade - ?
        WHERE id = ?
        """, (qtd * quantidade, insumo_id))

    # Registrar produção
    cursor.execute("INSERT INTO producao (produto_id, quantidade) VALUES (?, ?)",
                   (produto_id, quantidade))

    conn.commit()
    print("Produção realizada com sucesso!")

# ==============================
# RELATÓRIO
# ==============================
def relatorio_produtos():
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()

    for p in produtos:
        custo = calcular_custo(p[0])
        lucro = p[2] - custo
        print(f"Produto: {p[1]}")
        print(f"Custo: R$ {custo:.2f}")
        print(f"Venda: R$ {p[2]:.2f}")
        print(f"Lucro: R$ {lucro:.2f}")
        print("-" * 30)

# ==============================
# MENU
# ==============================
def menu():
    while True:
        print("\n--- SISTEMA DE PRODUÇÃO ---")
        print("1 - Cadastrar insumo")
        print("2 - Listar insumos")
        print("3 - Cadastrar produto")
        print("4 - Listar produtos")
        print("5 - Adicionar receita")
        print("6 - Produzir")
        print("7 - Relatório")
        print("0 - Sair")

        op = input("Escolha: ")

        if op == "1":
            nome = input("Nome: ")
            qtd = float(input("Quantidade: "))
            custo = float(input("Custo unitário: "))
            cadastrar_insumo(nome, qtd, custo)

        elif op == "2":
            for i in listar_insumos():
                print(i)

        elif op == "3":
            nome = input("Nome: ")
            preco = float(input("Preço de venda: "))
            cadastrar_produto(nome, preco)

        elif op == "4":
            for p in listar_produtos():
                print(p)

        elif op == "5":
            produto_id = int(input("ID do produto: "))
            insumo_id = int(input("ID do insumo: "))
            qtd = float(input("Quantidade usada: "))
            adicionar_receita(produto_id, insumo_id, qtd)

        elif op == "6":
            produto_id = int(input("ID do produto: "))
            qtd = int(input("Quantidade a produzir: "))
            produzir(produto_id, qtd)

        elif op == "7":
            relatorio_produtos()

        elif op == "0":
            break

# ==============================
# INICIAR
# ==============================
criar_tabelas()
menu()