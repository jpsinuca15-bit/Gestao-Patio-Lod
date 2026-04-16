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

# 3. REFERÊNCIA DE RECEITAS (Para visualização rápida)
receitas_referencia = {
    "Bloco de 10": "Cimento, Pó de Pedra, Pedrisco",
    "Bloco de 15": "Cimento, Pó de Pedra, Pedrisco",
    "Bloco de 20": "Cimento, Pó de Pedra, Pedrisco",
    "Bloco Sextavado": "Cimento, Brita 0, Areia, Pó de Pedra",
    "Bloco Intertravado": "Cimento, Brita 0, Areia, Pó de Pedra",
    "Meio Fio": "Cimento, Brita 1, Pó de Pedra, Areia",
    "Laje": "Cimento, Brita 0, Areia, Pó de Pedra"
}

# 4. MENU LATERAL
menu = st.sidebar.radio("Navegação", ["Painel Geral", "Lançar Produção", "Estoque Insumos"])

# --- 1. PAINEL GERAL ---
if menu == "Painel Geral":
    st.header("📊 Controle de Estoque")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Insumos (Matéria-prima)")
        try:
            df_insumos = carregar_dados("SELECT item as Material, quantidade as Saldo FROM insumos")
            def definir_unidade(material):
                return "Sacos" if material == "Cimento" else "m³"
            df_insumos['Unidade'] = df_insumos['Material'].apply(definir_unidade)
            st.dataframe(df_insumos, use_container_width=True)
        except:
            st.warning("Estoque de insumos vazio.")

    with col2:
        st.subheader("Produtos Prontos (Pátio)")
        try:
            df_blocos = carregar_dados("SELECT tipo as Produto, quantidade_total as Estoque FROM estoque_blocos")
            st.dataframe(df_blocos, use_container_width=True)
        except:
            st.info("Nenhum produto no pátio.")

# --- 2. LANÇAR PRODUÇÃO ---
elif menu == "Lançar Produção":
    st.header("➕ Registrar Nova Produção")
    produto = st.selectbox("O que foi fabricado?", list(receitas_referencia.keys()))
    st.info(f"💡 **Receita padrão:** {receitas_referencia[produto]}")

    with st.form("form_producao"):
        qtd_prod = st.number_input(f"Quantidade de {produto} fabricada", min_value=1, step=1)
        st.divider()
        st.write("### Informe o gasto TOTAL de materiais para baixar do estoque:")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            g_cimento = st.number_input("Cimento (Sacos)", min_value=0.0)
            g_areia = st.number_input("Areia (m³)", min_value=0.0)
        with c2:
            g_po_pedra = st.number_input("Pó de Pedra (m³)", min_value=0.0)
            g_pedrisco = st.number_input("Pedrisco (m³)", min_value=0.0)
        with c3:
            g_brita0 = st.number_input("Brita 0 (m³)", min_value=0.0)
            g_brita1 = st.number_input("Brita 1 (m³)", min_value=0.0) # Corrigido aqui
        
        btn = st.form_submit_button("Confirmar Lançamento")
        if btn:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS estoque_blocos (tipo TEXT PRIMARY KEY, quantidade_total REAL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS insumos (item TEXT PRIMARY KEY, quantidade REAL)")
            
            baixas = [
                (g_cimento, "Cimento"), (g_areia,