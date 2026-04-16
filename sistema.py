import sqlite3

def conectar():
    return sqlite3.connect('fabrica_blocos.db')

def registrar_producao_total(tipo, qtd, gastos):
    conn = conectar()
    cursor = conn.cursor()
    
    # Atualiza o estoque do produto pronto
    cursor.execute("UPDATE estoque_blocos SET quantidade_total = quantidade_total + ? WHERE tipo_bloco = ?", (qtd, tipo))
    
    # Desconta cada material usado
    for item, gasto in gastos.items():
        if gasto > 0:
            cursor.execute("UPDATE insumos SET quantidade = quantidade - ? WHERE item = ?", (gasto, item))
            
    conn.commit()
    conn.close()

def adicionar_estoque_insumo(item, qtd):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE insumos SET quantidade = quantidade + ? WHERE item = ?", (qtd, item))
    conn.commit()
    conn.close()