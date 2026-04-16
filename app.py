import streamlit as st
import pandas as pd
import sqlite3
from sistema import registrar_producao_total, adicionar_estoque_insumo

# Configuração da Página
st.set_page_config(page_title="Gestão de Pátio LOD", layout="wide")

# Função para ler dados do banco
def carregar_dados(query):
    conn = sqlite3.connect('fabrica_blocos.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Menu Lateral
menu = st.sidebar.radio("Navegação", ["📊 Painel Geral", "📝 Lançar Produção", "🚛 Entrada de Insumos"])

# --- 1. PAINEL GERAL ---
if menu == "📊 Painel Geral":
    st.title("📊 Controle de Estoque Atual")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Insumos (Matéria-prima)")
        st.dataframe(carregar_dados("SELECT item, quantidade, unidade_medida FROM insumos"), use_container_width=True, hide_index=True)
    with col2:
        st.subheader("Produtos Prontos")
        st.dataframe(carregar_dados("SELECT tipo_bloco, quantidade_total FROM estoque_blocos"), use_container_width=True, hide_index=True)

# --- 2. LANÇAR PRODUÇÃO (CORRIGIDO) ---
elif menu == "📝 Lançar Produção":
    st.title("📝 Registrar Produção")
    
    # IMPORTANTE: O selectbox fica FORA do form para a tela atualizar assim que você mudar o produto
    tipo_selecionado = st.selectbox("Selecione o Produto", [
        "Bloco 10", "Bloco 15", "Bloco 20", 
        "Sextavado", "Intertravado", 
        "Meio Fio 50cm", "Meio Fio 60cm", 
        "Laje"
    ])

    with st.form("form_producao"):
        qtd = st.number_input("Quantidade Produzida", min_value=1, step=1)
        st.divider()
        
        # O título agora usa a variável tipo_selecionado para mudar na hora!
        st.write(f"### Materiais usados para: **{tipo_selecionado}**")
        
        gastos = {}

        # Lógica de campos que mudam conforme o produto
        if tipo_selecionado in ["Bloco 10", "Bloco 15", "Bloco 20"]:
            gastos["Pedrisco"] = st.number_input("Pedrisco Gasto (kg)", 0.0)
            gastos["Pó de Pedra"] = st.number_input("Pó de Pedra Gasto (kg)", 0.0)
            gastos["Cimento"] = st.number_input("Cimento Gasto (Sacos)", 0.0)

        elif tipo_selecionado in ["Sextavado", "Intertravado", "Meio Fio 50cm", "Meio Fio 60cm"]:
            gastos["Areia"] = st.number_input("Areia Gasta (m³)", 0.0)
            gastos["Brita 1"] = st.number_input("Brita 1 Gasta (m³)", 0.0)
            gastos["Pó de Pedra"] = st.number_input("Pó de Pedra Gasto (kg)", 0.0)
            gastos["Cimento"] = st.number_input("Cimento Gasto (Sacos)", 0.0)

        elif tipo_selecionado == "Laje":
            gastos["Cimento"] = st.number_input("Cimento Gasto (Sacos)", 0.0)
            gastos["Brita 0"] = st.number_input("Brita 0 Gasta (m³)", 0.0)
            gastos["Areia"] = st.number_input("Areia Gasta (m³)", 0.0)
            gastos["Pó de Pedra"] = st.number_input("Pó de Pedra Gasto (kg)", 0.0)

        if st.form_submit_button("Confirmar Produção"):
            registrar_producao_total(tipo_selecionado, qtd, gastos)
            st.success(f"Sucesso! Produção de {tipo_selecionado} registrada.")

# --- 3. ENTRADA DE INSUMOS ---
elif menu == "🚛 Entrada de Insumos":
    st.title("🚛 Entrada de Carga")
    with st.form("form_entrada"):
        item = st.selectbox("Material", ["Cimento", "Areia", "Pedrisco", "Pó de Pedra", "Brita 0", "Brita 1"])
        qtd_in = st.number_input("Quantidade Recebida", min_value=0.1)
        if st.form_submit_button("Registrar Entrada"):
            adicionar_estoque_insumo(item, qtd_in)
            st.success(f"Estoque de {item} atualizado!")