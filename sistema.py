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

# 3. REFERÊNCIA DE RECEITAS (Para visualização)
receitas_referencia = {
    "Bloco de 10": "Cimento, Pó de Pedra, Pedrisco",
    "Bloco de 15": "Cimento, Pó de Pedra, Pedrisco",
    "Bloco de 20": "Cimento, Pó de Pedra, Pedrisco",
    "Bloco Sextavado": "Cimento, Brita 0, Areia, Pó de Pedra",
    "Bloco Intertravado": "Cimento, Brita 0, Areia, Pó de Pedra",
    "Meio Fio": "Cimento, Britão, Pó de Pedra, Areia",
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

# --- 2. LANÇAR PRODUÇÃO (BAIXA MANUAL COMPLETA) ---
elif menu == "Lançar Produção":
    st.header("➕ Registrar Nova Produção")
    produto = st.selectbox("O que foi fabricado?", list(receitas_referencia.keys()))
    st.info(f"💡 **Receita padrão:** {receitas_referencia[produto]}")

    with st.form("form_producao"):
        qtd_prod = st.number_input(f"Quantidade de {produto} fabricada", min_value=1, step=1)
        st.divider()
        st.write("### Informe o gasto total de materiais para baixar:")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            g_cimento = st.number_input("Cimento (Sacos)", min_value=0.0)
            g_areia = st.number_input("Areia (m³)", min_value=0.0)
        with c2:
            g_po_pedra = st.number_input("Pó de Pedra (m³)", min_value=0.0)
            g_pedrisco = st.number_input("Pedrisco (m³)", min_value=0.0)
        with c3:
            g_brita0 = st.number_input("Brita 0 (m³)", min_value=0.0)
            g_britao = st.number_input("Britão (m³)", min_value=0.0)
        
        btn = st.form_submit_button("Confirmar Lançamento")
        if btn:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS estoque_blocos (tipo TEXT PRIMARY KEY, quantidade_total REAL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS insumos (item TEXT PRIMARY KEY, quantidade REAL)")
            
            # Lista de todos os materiais possíveis para baixar
            baixas = [
                (g_cimento, "Cimento"), (g_areia, "Areia"), 
                (g_po_pedra, "Pó de Pedra"), (g_pedrisco, "Pedrisco"),
                (g_brita0, "Brita 0"), (g_britao, "Britão")
            ]
            
            for qtd, item in baixas:
                if qtd > 0:
                    cursor.execute("INSERT OR IGNORE INTO insumos (item, quantidade) VALUES (?, 0)", (item,))
                    cursor.execute("UPDATE insumos SET quantidade = quantidade - ? WHERE item = ?", (qtd, item))
            
            cursor.execute("INSERT INTO estoque_blocos (tipo, quantidade_total) VALUES (?, ?) ON CONFLICT(tipo) DO UPDATE SET quantidade_total = quantidade_total + ?", (produto, qtd_prod, qtd_prod))
            conn.commit()
            conn.close()
            st.success("Produção registrada e materiais baixados!")

# --- 3. ESTOQUE INSUMOS (LISTA COMPLETA) ---
elif menu == "Estoque Insumos":
    st.header("📥 Entrada de Materiais")
    with st.form("form_insumos"):
        insumo = st.selectbox("Material Recebido", ["Cimento", "Areia", "Pó de Pedra", "Pedrisco", "Brita 0", "Britão"])
        qtd = st.number_input("Quantidade", min_value=0.0)
        if st.form_submit_button("Salvar Entrada"):
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS insumos (item TEXT PRIMARY KEY, quantidade REAL)")
            cursor.execute("INSERT INTO insumos (item, quantidade) VALUES (?, ?) ON CONFLICT(item) DO UPDATE SET quantidade = quantidade + ?", (insumo, qtd, qtd))
            conn.commit()
            conn.close()
            st.success(f"Estoque de {insumo} atualizado!")