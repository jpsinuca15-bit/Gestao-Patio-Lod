import streamlit as st
import sqlite3
import pandas as pd
import os

# 🔥 GARANTE BANCO LIMPO (RODA UMA VEZ SÓ se quiser resetar)
# if os.path.exists("fabrica_blocos.db"):
#     os.remove("fabrica_blocos.db")

# 1. CONEXÃO
def conectar():
    return sqlite3.connect('fabrica_blocos.db', check_same_thread=False)

# 2. CRIAR TABELAS SEMPRE (EVITA ERRO)
def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque_blocos (
        tipo TEXT PRIMARY KEY,
        quantidade_total REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS insumos (
        item TEXT PRIMARY KEY,
        quantidade REAL
    )
    """)

    conn.commit()
    conn.close()

criar_tabelas()

# 3. CARREGAR DADOS
def carregar_dados(query):
    conn = conectar()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 4. CONFIGURAÇÃO
st.set_page_config(page_title="Gestão de Pátio LOD", layout="wide")
st.title("🏗️ Gestão de Pátio LOD")

# 5. RECEITAS
receitas_referencia = {
    "Bloco de 10": "Cimento, Pó de Pedra, Pedrisco",
    "Bloco de 15": "Cimento, Pó de Pedra, Pedrisco",
    "Bloco de 20": "Cimento, Pó de Pedra, Pedrisco",
    "Bloco Sextavado": "Cimento, Brita 0, Areia, Pó de Pedra",
    "Bloco Intertravado": "Cimento, Brita 0, Areia, Pó de Pedra",
    "Meio Fio": "Cimento, Britão, Pó de Pedra, Areia",
    "Laje": "Cimento, Brita 0, Areia, Pó de Pedra"
}

# 6. MENU
menu = st.sidebar.radio("Navegação", ["Painel Geral", "Lançar Produção", "Estoque Insumos"])

# =========================
# 📊 PAINEL
# =========================
if menu == "Painel Geral":
    st.header("📊 Controle de Estoque")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Insumos")
        try:
            df = carregar_dados("SELECT item as Material, quantidade as Saldo FROM insumos")
            st.dataframe(df, use_container_width=True)
        except:
            st.warning("Sem dados")

    with col2:
        st.subheader("Produtos")
        try:
            df = carregar_dados("SELECT tipo as Produto, quantidade_total as Estoque FROM estoque_blocos")
            st.dataframe(df, use_container_width=True)
        except:
            st.warning("Sem dados")

# =========================
# 🏭 PRODUÇÃO
# =========================
elif menu == "Lançar Produção":
    st.header("➕ Nova Produção")

    produto = st.selectbox("Produto", list(receitas_referencia.keys()))
    st.info(f"Receita: {receitas_referencia[produto]}")

    with st.form("form"):
        qtd_prod = st.number_input("Quantidade produzida", min_value=1)

        st.write("### Baixa de materiais")

        c1, c2, c3 = st.columns(3)

        with c1:
            cimento = st.number_input("Cimento", min_value=0.0)
            areia = st.number_input("Areia", min_value=0.0)

        with c2:
            po = st.number_input("Pó de Pedra", min_value=0.0)
            pedrisco = st.number_input("Pedrisco", min_value=0.0)

        with c3:
            brita0 = st.number_input("Brita 0", min_value=0.0)
            britao = st.number_input("Britão", min_value=0.0)

        if st.form_submit_button("Salvar"):
            conn = conectar()
            cursor = conn.cursor()

            # 🔻 BAIXA INSUMOS
            materiais = [
                ("Cimento", cimento),
                ("Areia", areia),
                ("Pó de Pedra", po),
                ("Pedrisco", pedrisco),
                ("Brita 0", brita0),
                ("Britão", britao),
            ]

            for nome, valor in materiais:
                if valor > 0:
                    cursor.execute("""
                    INSERT INTO insumos (item, quantidade)
                    VALUES (?, 0)
                    ON CONFLICT(item) DO NOTHING
                    """, (nome,))

                    cursor.execute("""
                    UPDATE insumos
                    SET quantidade = quantidade - ?
                    WHERE item = ?
                    """, (valor, nome))

            # 🔺 ADICIONA PRODUÇÃO
            cursor.execute("""
            INSERT INTO estoque_blocos (tipo, quantidade_total)
            VALUES (?, ?)
            ON CONFLICT(tipo) DO UPDATE SET
            quantidade_total = quantidade_total + excluded.quantidade_total
            """, (produto, qtd_prod))

            conn.commit()
            conn.close()

            st.success("Produção salva com sucesso!")

# =========================
# 📥 ENTRADA INSUMOS
# =========================
elif menu == "Estoque Insumos":
    st.header("📥 Entrada de Material")

    with st.form("entrada"):
        item = st.selectbox("Material", ["Cimento", "Areia", "Pó de Pedra", "Pedrisco", "Brita 0", "Britão"])
        qtd = st.number_input("Quantidade", min_value=0.0)

        if st.form_submit_button("Adicionar"):
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO insumos (item, quantidade)
            VALUES (?, ?)
            ON CONFLICT(item) DO UPDATE SET
            quantidade = quantidade + excluded.quantidade
            """, (item, qtd))

            conn.commit()
            conn.close()

            st.success("Entrada registrada!")