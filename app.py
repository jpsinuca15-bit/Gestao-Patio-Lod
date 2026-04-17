import streamlit as st
import sqlite3
import pandas as pd
import os

# ===== BANCO =====
DB = os.path.join(os.getcwd(), "fabrica_blocos.db")

def conectar():
    return sqlite3.connect(DB, check_same_thread=False)

def criar_tabelas():
    conn = conectar()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS insumos (
        item TEXT PRIMARY KEY,
        quantidade REAL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS estoque_blocos (
        tipo TEXT PRIMARY KEY,
        quantidade_total REAL
    )
    """)

    conn.commit()
    conn.close()

def carregar(query):
    conn = conectar()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

criar_tabelas()

# ===== APP =====
st.set_page_config(page_title="Gestão", layout="wide")
st.title("🏗️ Gestão de Pátio")

menu = st.sidebar.radio("Menu", ["Painel", "Produção", "Entrada"])

# ===== PAINEL =====
if menu == "Painel":
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Insumos")
        try:
            df = carregar("SELECT * FROM insumos")
            st.dataframe(df, use_container_width=True)
        except:
            st.warning("Sem dados")

    with col2:
        st.subheader("Produtos")
        try:
            df = carregar("SELECT * FROM estoque_blocos")
            st.dataframe(df, use_container_width=True)
        except:
            st.warning("Sem dados")

# ===== PRODUÇÃO =====
elif menu == "Produção":
    st.header("Produção")

    produto = st.selectbox("Produto", [
        "Bloco 10", "Bloco 15", "Bloco 20"
    ])

    qtd_prod = st.number_input("Quantidade", min_value=1)

    cimento = st.number_input("Cimento", min_value=0.0)
    areia = st.number_input("Areia", min_value=0.0)

    if st.button("Salvar Produção"):
        conn = conectar()
        c = conn.cursor()

        # baixa insumos
        for nome, valor in [("Cimento", cimento), ("Areia", areia)]:
            if valor > 0:
                c.execute("""
                INSERT OR IGNORE INTO insumos (item, quantidade)
                VALUES (?, 0)
                """, (nome,))

                c.execute("""
                UPDATE insumos SET quantidade = quantidade - ?
                WHERE item = ?
                """, (valor, nome))

        # soma produção
        c.execute("""
        INSERT INTO estoque_blocos (tipo, quantidade_total)
        VALUES (?, ?)
        ON CONFLICT(tipo) DO UPDATE SET
        quantidade_total = quantidade_total + excluded.quantidade_total
        """, (produto, qtd_prod))

        conn.commit()
        conn.close()

        st.success("Produção salva")

# ===== ENTRADA =====
elif menu == "Entrada":
    st.header("Entrada de Material")

    item = st.selectbox("Material", ["Cimento", "Areia"])
    qtd = st.number_input("Quantidade", min_value=0.0)

    if st.button("Adicionar"):
        conn = conectar()
        c = conn.cursor()

        c.execute("""
        INSERT INTO insumos (item, quantidade)
        VALUES (?, ?)
        ON CONFLICT(item) DO UPDATE SET
        quantidade = quantidade + excluded.quantidade
        """, (item, qtd))

        conn.commit()
        conn.close()

        st.success("Entrada salva")