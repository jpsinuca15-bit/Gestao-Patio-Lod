import streamlit as st
import sqlite3
import pandas as pd

# 1. FUNÇÕES DE BANCO DE DADOS
def conectar():
    return sqlite3.connect('fabrica_blocos.db')

def carregar_dados(query):
    conn = conectar()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Gestão de Pátio LOD", layout="wide")
st.title("🏗️ Gestão de Pátio LOD")

# 3. MENU LATERAL
menu = st.sidebar.radio("Navegação", ["Painel Geral", "Lançar Produção", "Estoque Insumos"])

# --- 1. PAINEL GERAL ---
if menu == "Painel Geral":
    st.header("📊 Controle de Estoque Atual")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Insumos (Matéria-prima)")
        df_insumos = carregar_dados("SELECT item, quantidade, unidade FROM insumos")
        st.dataframe(df_insumos, use_container_width=True)

    with col2:
        st.subheader("Produtos Prontos")
        df_blocos = carregar_dados("SELECT tipo, quantidade_total FROM estoque_blocos")
        st.dataframe(df_blocos, use_container_width=True)

# --- 2. LANÇAR PRODUÇÃO ---
elif menu == "Lançar Produção":
    st.header("➕ Registrar Nova Produção")
    
    with st.form("form_producao"):
        produto = st.selectbox("Selecione o Bloco Produzido", ["Bloco de 10", "Bloco de 15", "Bloco de 20", "Bloco Intertravado"])
        quantidade = st.number_input("Quantidade Produzida (unidades)", min_value=1, step=1)
        btn_produzir = st.form_submit_state = st.form_submit_button("Confirmar Lançamento")
        
        if btn_produzir:
            # Aqui entra a lógica de descontar insumos que fizemos antes
            st.success(f"Produção de {quantidade} unidades de {produto} registrada!")

# --- 3. ESTOQUE INSUMOS ---
elif menu == "Estoque Insumos":
    st.header("📥 Entrada de Materiais")
    st.info("Use esta área para repor Cimento, Areia ou Brita.")
    
    with st.form("form_insumos"):
        insumo = st.selectbox("Material Recebido", ["Cimento", "Areia", "Brita"])
        qtd_entrada = st.number_input("Quantidade Recebida", min_value=0.1)
        btn_insumo = st.form_submit_button("Atualizar Estoque")
        
        if btn_insumo:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("UPDATE insumos SET quantidade = quantidade + ? WHERE item = ?", (qtd_entrada, insumo))
            conn.commit()
            conn.close()
            st.success(f"Estoque de {insumo} atualizado com sucesso!")