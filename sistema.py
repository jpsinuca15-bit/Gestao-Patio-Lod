import streamlit as st
import sqlite3
import pandas as pd
import os

# 🔥 CAMINHO FIXO DO BANCO (ACABA COM BUG)
CAMINHO_DB = os.path.join(os.getcwd(), "fabrica_blocos.db")

def conectar():
    return sqlite3.connect(CAMINHO_DB, check_same_thread=False)

# 🔥 CRIA TABELAS CERTO
def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS insumos (
        item TEXT PRIMARY KEY,
        quantidade REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque_blocos (
        tipo TEXT PRIMARY KEY,
        quantidade_total REAL
    )
    """)

    conn.commit()
    conn.close()

# 🔥 CARREGAR DADOS
def carregar_dados(query):
    conn = conectar()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# 🔥 APP PRINCIPAL
def rodar_app():
    criar_tabelas()

    st.title("🏗️ Gestão de Pátio LOD")
    st.write("Banco usado:", CAMINHO_DB)

    receitas = {
        "Bloco de 10": "Cimento, Pó de Pedra, Pedrisco",
        "Bloco de 15": "Cimento, Pó de Pedra, Pedrisco",
        "Bloco de 20": "Cimento, Pó de Pedra, Pedrisco",
        "Bloco Sextavado": "Cimento, Brita 0, Areia, Pó de Pedra",
        "Bloco Intertravado": "Cimento, Brita 0, Areia, Pó de Pedra",
        "Meio Fio": "Cimento, Britão, Pó de Pedra, Areia",
        "Laje": "Cimento, Brita 0, Areia, Pó de Pedra"
    }

    menu = st.sidebar.radio("Menu", ["Painel", "Produção", "Entrada Insumos"])

    # =====================
    # 📊 PAINEL
    # =====================
    if menu == "Painel":
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Insumos")
            try:
                df = carregar_dados("SELECT item, quantidade FROM insumos")
                st.dataframe(df, use_container_width=True)
            except:
                st.warning("Sem dados")

        with col2:
            st.subheader("Produtos")
            try:
                df = carregar_dados("SELECT tipo, quantidade_total FROM estoque_blocos")
                st.dataframe(df, use_container_width=True)
            except:
                st.warning("Sem dados")

    # =====================
    # 🏭 PRODUÇÃO
    # =====================
    elif menu == "Produção":
        st.header("Nova Produção")

        produto = st.selectbox("Produto", list(receitas.keys()))
        st.info(receitas[produto])

        with st.form("prod"):
            qtd_prod = st.number_input("Quantidade", min_value=1)

            c1, c2, c3 = st.columns(3)

            with c1:
                cimento = st.number_input("Cimento", min_value=0.0)
                areia = st.number_input("Areia", min_value=0.0)

            with c2:
                po = st.number_input("Pó de Pedra", min_value=0.0)
                pedrisco = st.number_input("Pedrisco", min_value=0.0)

            with c3:
                brita0 = st.number_input("Brita 0", min_value=0.0)
                britao = st.number_input("Brita 1", min_value=0.0)

            if st.form_submit_button("Salvar"):
                conn = conectar()
                cursor = conn.cursor()

                materiais = [
                    ("Cimento", cimento),
                    ("Areia", areia),
                    ("Pó de Pedra", po),
                    ("Pedrisco", pedrisco),
                    ("Brita 0", brita0),
                    ("Brita 1", brita1),
                ]

                # 🔻 BAIXA INSUMOS
                for nome, valor in materiais:
                    if valor > 0:
                        cursor.execute("""
                        INSERT OR IGNORE INTO insumos (item, quantidade)
                        VALUES (?, 0)
                        """, (nome,))

                        cursor.execute("""
                        UPDATE insumos
                        SET quantidade = quantidade - ?
                        WHERE item = ?
                        """, (valor, nome))

                # 🔺 SOMA PRODUÇÃO
                cursor.execute("""
                INSERT INTO estoque_blocos (tipo, quantidade_total)
                VALUES (?, ?)
                ON CONFLICT(tipo) DO UPDATE SET
                quantidade_total = quantidade_total + excluded.quantidade_total
                """, (produto, qtd_prod))

                conn.commit()
                conn.close()

                st.success("Produção salva!")

    # =====================
    # 📥 ENTRADA
    # =====================
    elif menu == "Entrada Insumos":
        st.header("Entrada de Material")

        with st.form("entrada"):
            item = st.selectbox("Material", ["Cimento", "Areia", "Pó de Pedra", "Pedrisco", "Brita 0", "Britão"])
            qtd = st.number_input("Quantidade", min_value=0.0)

            if st.form_submit_button("Salvar"):
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

                st.success("Entrada salva!")