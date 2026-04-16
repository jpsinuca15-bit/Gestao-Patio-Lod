import streamlit as st
import sqlite3
import pandas as pd

st.write("Conectando ao banco de dados...")
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
    


# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Pátio LOD", layout="wide")

st.title("🏗️ Gestão de Pátio LOD")

# Menu Lateral
menu = st.sidebar.radio("Navegação", ["Painel Geral", "Lançar Produção", "Estoque Insumos"])

if menu == "Painel Geral":
    st.subheader("📊 Controle de Estoque Atual")
    # Aqui você chamará as funções para mostrar os dados depois
    st.info("O sistema está online! Agora vamos conectar os dados.")

elif menu == "Lançar Produção":
    st.subheader("➕ Registrar Nova Produção")
    tipo = st.selectbox("Produto", ["Bloco de 10", "Bloco de 20", "Intertravado"])
    qtd = st.number_input("Quantidade produzida", min_value=1)
    if st.button("Confirmar Lançamento"):
        st.success(f"Produção de {qtd} unidades de {tipo} registrada!")

elif menu == "Estoque Insumos":
    st.subheader("📦 Entrada de Materiais")
    st.write("Área para reposição de cimento, areia e brita.")