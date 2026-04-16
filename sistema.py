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
        try:
            df_insumos = carregar_dados("SELECT item, quantidade FROM insumos")
            st.dataframe(df_insumos, use_container_width=True)
        except:
            st.error("Erro ao carregar a tabela 'insumos'.")

    with col2:
        st.subheader("Produtos Prontos")
        try:
            df_blocos = carregar_dados("SELECT tipo, quantidade_total FROM estoque_blocos")
            st.dataframe(df_blocos, use_container_width=True)
        except:
            st.error("Erro ao carregar a tabela 'estoque_blocos'.")

# --- 2. LANÇAR PRODUÇÃO ---
elif menu == "Lançar Produção":
    st.header("➕ Registrar Nova Produção")
    
    with st.form("form_producao"):
        # LISTA ATUALIZADA DE PRODUTOS
        lista_produtos = [
            "Bloco de 10", "Bloco de 15", "Bloco de 20", 
            "Bloco Sextavado", "Bloco Intertravado", 
            "Laje", "Meio Fio de 50", "Meio Fio de 80"
        ]
        produto = st.selectbox("Selecione o Produto Fabricado", lista_produtos)
        quantidade = st.number_input("Quantidade Produzida (unidades)", min_value=1, step=1)
        btn_produzir = st.form_submit_button("Confirmar Lançamento")
        
        if btn_produzir:
            st.success(f"Produção de {quantidade} unidades de {produto} registrada!")

# --- 3. ESTOQUE INSUMOS ---
elif menu == "Estoque Insumos":
    st.header("📥 Entrada de Materiais")
    
    with st.form("form_insumos"):
        # ADICIONE AQUI SE TIVER MAIS MATERIAIS ALÉM DESSES
        lista_materiais = ["Cimento", "Areia", "Brita", "Pó de Pedra", "Pedrisco"]
        insumo = st.selectbox("Material Recebido", lista_materiais)
        qtd_entrada = st.number_input("Quantidade Recebida", min_value=0.0, step=0.1)
        btn_insumo = st.form_submit_button("Atualizar Estoque")
        
        if btn_insumo:
            try:
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("UPDATE insumos SET quantidade = quantidade + ? WHERE item = ?", (qtd_entrada, insumo))
                conn.commit()
                conn.close()
                st.success(f"Estoque de {insumo} atualizado!")
            except Exception as e:
                st.error(f"Erro no banco: {e}")