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

# 3. DICIONÁRIO DE REFERÊNCIA (Apenas para você visualizar o que gasta)
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
            # Seleciona apenas o que existe para não dar erro de coluna
            df_insumos = carregar_dados("SELECT item as Material, quantidade as Saldo FROM insumos")
            unidades_map = {
                "Cimento": "Sacos",
                "Areia": "m³",
                "Pedrisco": "m³",
                "Pó de Pedra": "m³",
                "Brita 0": "m³",
                "Brita 1": "m³"
            }
            df_insumos['Unidade'] = df_insumos['Material'].map(unidades_map).fillna("m³")
            st.dataframe(df_insumos, use_container_width=True)
        except:
            st.warning("Estoque de insumos vazio ou tabela não criada.")

    with col2:
        st.subheader("Produtos Prontos (Pátio)")
        try:
            df_blocos = carregar_dados("SELECT tipo as Produto, quantidade_total as Estoque FROM estoque_blocos")
            st.dataframe(df_blocos, use_container_width=True)
        except:
            st.info("Nenhum produto no pátio ainda.")

# --- 2. LANÇAR PRODUÇÃO (MANUAL) ---
elif menu == "Lançar Produção":
    st.header("➕ Registrar Nova Produção")
    
    produto = st.selectbox("O que foi fabricado?", list(receitas_referencia.keys()))
    st.info(f"💡 **O que costuma gastar:** {receitas_referencia[produto]}")

    with st.form("form_producao_manual"):
        qtd_prod = st.number_input(f"Quantidade de {produto} fabricada", min_value=1, step=1)
        
        st.divider()
        st.write("### Informe o que foi gasto (Baixa Manual):")
        
        # Aqui você coloca manualmente quanto gastou de cada um
        g_cimento = st.number_input("Cimento gasto (Sacos)", min_value=0.0, step=0.1)
        g_areia = st.number_input("Areia gasta (m³)", min_value=0.0, step=0.1)
        g_po_pedra = st.number_input("Pó de Pedra gasto (m³)", min_value=0.0, step=0.1)
        g_brita1 = st.number_input("Brita 1 gasta (m³)", min_value=0.0, step=0.1)
        g_pedrisco = st.number_input("Pedrisco gasto (m³)", min_value=0.0, step=0.1)

        btn_confirmar = st.form_submit_button("Confirmar Produção e Baixar Estoque")
        
        if btn_confirmar:
            try:
                conn = conectar()
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS estoque_blocos (tipo TEXT PRIMARY KEY, quantidade_total REAL)")
                
                # Baixa manual nos materiais informados
                baixas = [
                    (g_cimento, "Cimento"), (g_areia, "Areia"), 
                    (g_po_pedra, "Pó de Pedra"), (g_brita1, "Brita 1"),
                    (g_pedrisco, "Pedrisco")
                ]
                
                for qtd, item in baixas:
                    if qtd > 0:
                        cursor.execute("UPDATE insumos SET quantidade = quantidade - ? WHERE item = ?", (qtd, item))
                
                # Aumenta o estoque do bloco
                cursor.execute("INSERT INTO estoque_blocos (tipo, quantidade_total) VALUES (?, ?) ON CONFLICT(tipo) DO UPDATE SET quantidade_total = quantidade_total + ?", (produto, qtd_prod, qtd_prod))
                
                conn.commit()
                conn.close()
                st.success(f"Registrado: {qtd_prod} {produto}. Estoque atualizado!")
            except Exception as e:
                st.error(f"Erro: {e}")

# --- 3. ESTOQUE INSUMOS ---
elif menu == "Estoque Insumos":
    st.header("📥 Entrada de Materiais")
    with st.form("form_insumos"):
        # Corrigido: 'Areia' escrito certo e 'Brita 1'
        insumo = st.selectbox("Material Recebido", ["Cimento", "Areia", "Pedrisco", "Pó de Pedra", "Brita 0", "Brita 1"])
        unid = "Sacos" if insumo == "Cimento" else "m³"
        qtd_entrada = st.number_input(f"Quantidade em {unid}", min_value=0.0, step=0.1)
        btn_insumo = st.form_submit_button("Salvar Entrada")
        
        if btn_insumo:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS insumos (item TEXT PRIMARY KEY, quantidade REAL)")
            cursor.execute("INSERT INTO insumos (item, quantidade) VALUES (?, ?) ON CONFLICT(item) DO UPDATE SET quantidade = quantidade + ?", (insumo, qtd_entrada, qtd_entrada))
            conn.commit()
            conn.close()
            st.success(f"Estoque de {insumo} atualizado!")