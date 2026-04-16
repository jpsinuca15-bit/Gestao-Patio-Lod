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

# 3. LÓGICA DE CONSUMO (Ajustado para Brita 1 e materiais corretos)
# Valores fictícios por unidade - AJUSTE conforme sua necessidade real
receitas = {
    "Bloco de 10": {"Cimento": 0.05, "Pó de Pedra": 0.01, "Pedrisco": 0.01},
    "Bloco de 15": {"Cimento": 0.07, "Pó de Pedra": 0.015, "Pedrisco": 0.015},
    "Bloco de 20": {"Cimento": 0.10, "Pó de Pedra": 0.02, "Pedrisco": 0.02},
    "Bloco Sextavado": {"Cimento": 0.12, "Brita 1": 0.02, "Areia": 0.02, "Pó de Pedra": 0.02},
    "Bloco Intertravado": {"Cimento": 0.08, "Brita 1": 0.015, "Areia": 0.015, "Pó de Pedra": 0.015},
    "Meio Fio de 50": {"Cimento": 0.20, "Brita 1": 0.05, "Pó de Pedra": 0.05, "Areia": 0.05},
    "Meio Fio de 80": {"Cimento": 0.35, "Brita 1": 0.08, "Pó de Pedra": 0.08, "Areia": 0.08},
    "Laje": {"Cimento": 0.15, "Brita 1": 0.03, "Areia": 0.03, "Pó de Pedra": 0.03}
}

# 4. MENU LATERAL
menu = st.sidebar.radio("Navegação", ["Painel Geral", "Lançar Produção", "Estoque Insumos"])

# --- 1. PAINEL GERAL ---
if menu == "Painel Geral":
    st.header("📊 Controle de Estoque") # Removido o "Atual" como pedido
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Insumos (Matéria-prima)")
        try:
            df_insumos = carregar_dados("SELECT item as Material, quantidade as Saldo FROM insumos")
            # Unidades corrigidas: Brita 1 agora é m³
            unidades = {
                "Cimento": "Unidades (Sacos)",
                "Areia": "m³",
                "Pedrisco": "m³",
                "Pó de Pedra": "m³",
                "Brita 0": "m³",
                "Brita 1": "m³" # Corrigido de 'un' para 'm³'
            }
            df_insumos['Unidade'] = df_insumos['Material'].map(unidades).fillna("un")
            st.dataframe(df_insumos, use_container_width=True)
        except:
            st.warning("Tabela de insumos não encontrada ou vazia.")

    with col2:
        st.subheader("Produtos Prontos (Pátio)")
        try:
            df_blocos = carregar_dados("SELECT tipo as Produto, quantidade_total as Estoque FROM estoque_blocos")
            st.dataframe(df_blocos, use_container_width=True)
        except:
            st.info("Aguardando primeiro lançamento de produção.")

# --- 2. LANÇAR PRODUÇÃO ---
elif menu == "Lançar Produção":
    st.header("➕ Registrar Nova Produção")
    
    produto = st.selectbox("O que foi fabricado?", list(receitas.keys()))
    
    # MOSTRAR OS MATERIAIS QUE SERÃO USADOS (A sua dúvida)
    st.info(f"**Materiais gastos por unidade de {produto}:**")
    for mat, qtd in receitas[produto].items():
        st.write(f"- {mat}: {qtd}")

    with st.form("form_producao"):
        quantidade = st.number_input("Quantidade produzida (unidades)", min_value=1, step=1)
        # Botão corrigido (Removido a barra ou erro de configuração visual)
        btn_produzir = st.form_submit_button("Confirmar Lançamento")
        
        if btn_produzir:
            try:
                conn = conectar()
                cursor = conn.cursor()
                
                cursor.execute("CREATE TABLE IF NOT EXISTS estoque_blocos (tipo TEXT PRIMARY KEY, quantidade_total REAL)")
                
                # Baixa automática nos insumos
                gastos = receitas[produto]
                for material, gasto_unitario in gastos.items():
                    total_gasto = gasto_unitario * quantidade
                    cursor.execute("UPDATE insumos SET quantidade = quantidade - ? WHERE item = ?", (total_gasto, material))
                
                # Aumenta estoque do produto pronto
                cursor.execute("INSERT INTO estoque_blocos (tipo, quantidade_total) VALUES (?, ?) ON CONFLICT(tipo) DO UPDATE SET quantidade_total = quantidade_total + ?", (produto, quantidade, quantidade))
                
                conn.commit()
                conn.close()
                st.success(f"Produção de {quantidade} {produto} registrada com sucesso!")
            except Exception as e:
                st.error(f"Erro ao processar: {e}")

# --- 3. ESTOQUE INSUMOS ---
elif menu == "Estoque Insumos":
    st.header("📥 Entrada de Materiais (Compra)")
    with st.form("form_insumos"):
        # Corrigido de 'Britão' para 'Brita 1'
        insumo = st.selectbox("Material Recebido", ["Cimento", "Areia", "Pedrisco", "Pó de Pedra", "Brita 0", "Brita 1"])
        unidade_label = "Sacos" if insumo == "Cimento" else "Metros Cúbicos (m³)"
        qtd_entrada = st.number_input(f"Quantidade em {unidade_label}", min_value=0.0, step=0.1)
        btn_insumo = st.form_submit_button("Adicionar ao Estoque")
        
        if btn_insumo:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS insumos (item TEXT PRIMARY KEY, quantidade REAL)")
            cursor.execute("INSERT INTO insumos (item, quantidade) VALUES (?, ?) ON CONFLICT(item) DO UPDATE SET quantidade = quantidade + ?", (insumo, qtd_entrada, qtd_entrada))
            conn.commit()
            conn.close()
            st.success(f"Entrada de {qtd_entrada} de {insumo} registrada!")