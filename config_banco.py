import sqlite3

def inicializar():
    conn = sqlite3.connect('fabrica_blocos.db')
    cursor = conn.cursor()

    # Criar tabela de Blocos Prontos
    cursor.execute('''CREATE TABLE IF NOT EXISTS estoque_blocos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_bloco TEXT NOT NULL,
        quantidade_total INTEGER DEFAULT 0
    )''')

    # Criar tabela de Insumos
    cursor.execute('''CREATE TABLE IF NOT EXISTS insumos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT NOT NULL,
        quantidade REAL DEFAULT 0,
        unidade_medida TEXT
    )''')

    # Inserir Insumos Iniciais (Se não existirem)
    insumos_iniciais = [
        ('Cimento', 0, 'Sacos'),
        ('Areia', 0, 'm³'),
        ('Pedrisco', 0, 'kg'),
        ('Pó de Pedra', 0, 'kg'),
        ('Brita 0', 0, 'm³'),
        ('Brita 1', 0, 'm³')
    ]
    
    for item, qtd, uni in insumos_iniciais:
        cursor.execute("SELECT id FROM insumos WHERE item = ?", (item,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO insumos (item, quantidade, unidade_medida) VALUES (?, ?, ?)", (item, qtd, uni))

    # Inserir Produtos Iniciais (Se não existirem)
    produtos_iniciais = [
        "Bloco 10", "Bloco 15", "Bloco 20", 
        "Sextavado", "Intertravado", 
        "Meio Fio 50cm", "Meio Fio 60cm", "Laje"
    ]
    
    for prod in produtos_iniciais:
        cursor.execute("SELECT id FROM estoque_blocos WHERE tipo_bloco = ?", (prod,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO estoque_blocos (tipo_bloco, quantidade_total) VALUES (?, 0)", (prod,))

    conn.commit()
    conn.close()
    print("✅ Banco de dados configurado com os nomes oficiais!")

if __name__ == "__main__":
    inicializar()