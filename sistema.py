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

# 3. REFERÊNCIA DE MATERIAIS (O que gasta em cada um)
receitas_referencia = {
    "Bloco de 10": "Cimento, Pó de Pedra, Pedrisco",
    "Bloco de 15": "Cimento, Pó de Pedra, Pedrisco",
    "Bloco de 20": "Cimento, Pó de Pedra, Pedrisco",
    "Bloco Sextavado": "Cimento, Brita 1, Areia, Pó de Pedra",
    "Bloco Intertravado": "Cimento, Brita 1, Areia, Pó de Pedra",
    "Meio Fio de 50": "Cimento, Brita 1, Pó de Pedra, Areia",
    "Meio Fio de 80": "Cimento, Brita 1, Pó de Pedra, Areia",
    "Laje": "Cimento, Brita 1, Areia, Pó de Pedra"
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
            # Pega apenas Material e Saldo para evitar erro de coluna 'unidade'
            df_insumos = carregar_dados("SELECT item as Material, quantidade as Saldo FROM insumos")
            
            # Lógica para definir a unidade na tela (Sem precisar de coluna no banco)
            def definir_unidade(material):
                if material == "Cimento":
                    return "Sacos"
                return "m³"
            
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
    st.info(f"💡 **O que costuma gastar:** {receitas_referencia[produto]}")

    with st.form("form_producao_manual"):
        qtd_prod = st.number_input(f"Quantidade de {produto} fabricada", min_value=1, step=1)
        
        st.divider()
        st.write("### Informe o gasto real para dar baixa automática:")
        
        c1, c2 = st.columns(2)
        with c1:
            g_cimento = st.number_input("Cimento (Sacos)", min_value=0.0, step=0.1)
            g_areia = st.number_input("Areia (m³)", min_value=0.0, step=0.1)
            g_po_pedra = st.number_input("Pó de Pedra (m³)", min_value=0.0, step=0.1)
        with c2:
            g_brita1 = st.number_input("Brita 1 (m³)", min_value=0.0, step=0.1)
            g_pedrisco = st.number_input("Pedrisco (m³)", min_value=0.0, step=0.1