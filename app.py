import streamlit as st
import pandas as pd
from database import (
    criar_tabelas,
    cadastrar_insumo, listar_insumos, entrada_estoque, deletar_insumo, atualizar_insumo,
    cadastrar_produto, listar_produtos, deletar_produto,
    adicionar_receita, listar_receita, deletar_item_receita,
    calcular_custo, verificar_estoque_producao, produzir,
    relatorio_produtos, historico_producao, historico_movimentacoes,
    insumos_criticos, totais_dashboard
)

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(
    page_title="GestorBloco Pro",
    page_icon="🧱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================
# CSS PERSONALIZADO
# ==============================
st.markdown("""
<style>
    /* Fundo principal cinza concreto */
    .stApp {
        background-color: #1C1C1E;
        color: #F0F0F0;
    }

    /* Sidebar escura com borda laranja */
    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 3px solid #E8630A;
    }

    [data-testid="stSidebar"] .stRadio label {
        color: #F0F0F0 !important;
        font-size: 15px;
        padding: 6px 0;
    }

    /* Título principal */
    h1 {
        color: #E8630A !important;
        font-family: 'Arial Black', sans-serif;
        letter-spacing: -1px;
    }

    h2, h3 {
        color: #F0F0F0 !important;
    }

    /* Cards de métrica */
    [data-testid="metric-container"] {
        background-color: #2C2C2E;
        border: 1px solid #3A3A3C;
        border-radius: 10px;
        padding: 16px;
        border-left: 4px solid #E8630A;
    }

    [data-testid="stMetricValue"] {
        color: #E8630A !important;
        font-size: 28px !important;
        font-weight: 800 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #AEAEB2 !important;
        font-size: 13px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Botões */
    .stButton > button {
        background-color: #E8630A;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        font-size: 14px;
        padding: 10px 20px;
        transition: all 0.2s;
        width: 100%;
    }

    .stButton > button:hover {
        background-color: #FF7A22;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(232, 99, 10, 0.4);
    }

    /* Inputs */
    .stTextInput > div > input,
    .stNumberInput > div > input,
    .stSelectbox > div > div {
        background-color: #2C2C2E !important;
        border: 1px solid #3A3A3C !important;
        color: #F0F0F0 !important;
        border-radius: 8px !important;
    }

    /* Tabelas */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Alertas */
    .alerta-critico {
        background-color: #3A1C1C;
        border-left: 4px solid #FF453A;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #FF6B6B;
        font-weight: 600;
    }

    .alerta-ok {
        background-color: #1C3A2A;
        border-left: 4px solid #30D158;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #4CD964;
        font-weight: 600;
    }

    /* Divisor */
    hr {
        border-color: #3A3A3C;
        margin: 20px 0;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #2C2C2E;
        border-radius: 10px;
        padding: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #AEAEB2;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        color: #E8630A !important;
        background-color: #3A3A3C;
        border-radius: 8px;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #2C2C2E;
        border-radius: 8px;
        color: #F0F0F0 !important;
    }

    /* Selectbox label */
    .stSelectbox label, .stTextInput label, .stNumberInput label {
        color: #AEAEB2 !important;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Logo/Header da sidebar */
    .sidebar-logo {
        text-align: center;
        padding: 20px 10px 10px;
        border-bottom: 1px solid #3A3A3C;
        margin-bottom: 20px;
    }

    .sidebar-logo h2 {
        color: #E8630A !important;
        font-size: 22px;
        margin: 0;
        font-weight: 900;
        letter-spacing: -0.5px;
    }

    .sidebar-logo p {
        color: #AEAEB2;
        font-size: 11px;
        margin: 4px 0 0;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Badge de alerta na sidebar */
    .badge-alerta {
        background: #FF453A;
        color: white;
        border-radius: 12px;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: 700;
        margin-left: 8px;
    }

    /* Sucesso e erro customizados */
    .stSuccess {
        background-color: #1C3A2A !important;
        border-left: 4px solid #30D158 !important;
    }

    .stError {
        background-color: #3A1C1C !important;
        border-left: 4px solid #FF453A !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================
# SIDEBAR - NAVEGAÇÃO
# ==============================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <h2>🧱 GestorBloco</h2>
        <p>Sistema de Controle</p>
    </div>
    """, unsafe_allow_html=True)

    # Alerta rápido de estoque
    criticos = insumos_criticos()
    if criticos:
        st.markdown(f"""
        <div class="alerta-critico">
            ⚠️ {len(criticos)} insumo(s) em estoque crítico!
        </div>
        """, unsafe_allow_html=True)

    pagina = st.radio(
        "Menu",
        [
            "📊 Dashboard",
            "📦 Insumos",
            "🧱 Produtos",
            "📋 Receitas",
            "⚙️ Produção",
            "📈 Relatórios",
            "🔄 Movimentações"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <p style="color:#AEAEB2; font-size:11px; text-align:center;">
        GestorBloco Pro v1.0<br>
        <span style="color:#E8630A;">● Online</span>
    </p>
    """, unsafe_allow_html=True)


# ==============================
# PÁGINA: DASHBOARD
# ==============================
if pagina == "📊 Dashboard":
    st.title("📊 Dashboard Operacional")
    st.markdown("Visão geral da fábrica em tempo real")
    st.markdown("---")

    dados = totais_dashboard()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Insumos Cadastrados", dados["total_insumos"])
    with col2:
        st.metric("Produtos Cadastrados", dados["total_produtos"])
    with col3:
        st.metric("Total Produzido", f"{int(dados['total_produzido']):,} un")
    with col4:
        st.metric("Faturamento Total", f"R$ {dados['faturamento_total']:,.2f}")
    with col5:
        st.metric("⚠️ Alertas Estoque", dados["alertas"])

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### 🔴 Insumos em Estoque Crítico")
        criticos = insumos_criticos()
        if criticos:
            for item in criticos:
                st.markdown(f"""
                <div class="alerta-critico">
                    ⚠️ <strong>{item['nome']}</strong> — 
                    Estoque: {item['quantidade']:.1f} {item['unidade']} 
                    (mínimo: {item['estoque_minimo']:.1f})
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alerta-ok">
                ✅ Todos os insumos estão dentro do estoque mínimo!
            </div>
            """, unsafe_allow_html=True)

    with col_b:
        st.markdown("### 📦 Últimas Produções")
        historico = historico_producao()
        if historico:
            df = pd.DataFrame(historico[:5])
            df.columns = ["Produto", "Qtd", "Data", "Faturamento"]
            df["Faturamento"] = df["Faturamento"].apply(lambda x: f"R$ {x:,.2f}")
            df["Data"] = pd.to_datetime(df["Data"]).dt.strftime("%d/%m/%Y %H:%M")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma produção registrada ainda.")

    st.markdown("---")
    st.markdown("### 💰 Margem por Produto")
    relatorio = relatorio_produtos()
    if relatorio:
        df_r = pd.DataFrame(relatorio)
        df_r = df_r[["nome", "custo", "preco_venda", "lucro", "margem"]]
        df_r.columns = ["Produto", "Custo (R$)", "Venda (R$)", "Lucro (R$)", "Margem %"]
        df_r["Custo (R$)"] = df_r["Custo (R$)"].apply(lambda x: f"R$ {x:.4f}")
        df_r["Venda (R$)"] = df_r["Venda (R$)"].apply(lambda x: f"R$ {x:.4f}")
        df_r["Lucro (R$)"] = df_r["Lucro (R$)"].apply(lambda x: f"R$ {x:.4f}")
        df_r["Margem %"] = df_r["Margem %"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(df_r, use_container_width=True, hide_index=True)
    else:
        st.info("Cadastre produtos e receitas para ver as margens.")


# ==============================
# PÁGINA: INSUMOS
# ==============================
elif pagina == "📦 Insumos":
    st.title("📦 Gestão de Insumos")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["➕ Cadastrar", "📋 Listar Estoque", "📥 Entrada de Estoque"])

    with tab1:
        st.markdown("### Cadastrar Novo Insumo")
        col1, col2 = st.columns(2)
        with col1:
            nome_ins = st.text_input("Nome do Insumo", placeholder="Ex: Cimento CP-II")
            unidade_ins = st.selectbox("Unidade de Medida", ["kg", "L", "m³", "sc", "un", "m", "t"])
        with col2:
            qtd_ins = st.number_input("Quantidade Inicial", min_value=0.0, step=1.0, format="%.2f")
            custo_ins = st.number_input("Custo por Unidade (R$)", min_value=0.0, step=0.01, format="%.4f")

        estoque_min = st.number_input("Estoque Mínimo (alerta automático)", min_value=0.0, step=1.0, format="%.2f")

        if st.button("💾 Cadastrar Insumo"):
            if nome_ins.strip():
                cadastrar_insumo(nome_ins.strip(), qtd_ins, custo_ins, unidade_ins, estoque_min)
                st.success(f"✅ Insumo '{nome_ins}' cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Digite o nome do insumo.")

    with tab2:
        st.markdown("### Estoque Atual")
        insumos = listar_insumos()
        if insumos:
            df = pd.DataFrame(insumos)
            df = df[["id", "nome", "quantidade", "unidade", "custo_unitario", "estoque_minimo"]]
            df.columns = ["ID", "Nome", "Quantidade", "Unidade", "Custo Unit. (R$)", "Estoque Mín."]

            def colorir_linha(row):
                if row["Quantidade"] <= row["Estoque Mín."]:
                    return ["background-color: #3A1C1C"] * len(row)
                return [""] * len(row)

            st.dataframe(
                df.style.apply(colorir_linha, axis=1),
                use_container_width=True,
                hide_index=True
            )

            st.markdown("*🔴 Linhas em vermelho = abaixo do estoque mínimo*")

            st.markdown("---")
            st.markdown("### 🗑️ Remover Insumo")
            ids_ins = {f"{i['nome']} (ID: {i['id']})": i["id"] for i in insumos}
            sel_del = st.selectbox("Selecionar insumo para remover", list(ids_ins.keys()), key="del_ins")
            if st.button("🗑️ Remover Insumo Selecionado"):
                deletar_insumo(ids_ins[sel_del])
                st.success("Insumo removido.")
                st.rerun()
        else:
            st.info("Nenhum insumo cadastrado ainda. Vá em 'Cadastrar' para adicionar.")

    with tab3:
        st.markdown("### Registrar Entrada de Estoque")
        insumos = listar_insumos()
        if insumos:
            ids_map = {f"{i['nome']} — Estoque atual: {i['quantidade']} {i['unidade']}": i["id"] for i in insumos}
            sel_ent = st.selectbox("Insumo", list(ids_map.keys()))
            qtd_ent = st.number_input("Quantidade que está entrando", min_value=0.01, step=1.0, format="%.2f")
            obs_ent = st.text_input("Observação (opcional)", placeholder="Ex: Compra NF 0042")

            if st.button("📥 Registrar Entrada"):
                entrada_estoque(ids_map[sel_ent], qtd_ent, obs_ent)
                st.success(f"✅ Entrada de {qtd_ent} unidades registrada!")
                st.rerun()
        else:
            st.info("Nenhum insumo cadastrado. Cadastre insumos primeiro.")


# ==============================
# PÁGINA: PRODUTOS
# ==============================
elif pagina == "🧱 Produtos":
    st.title("🧱 Gestão de Produtos")
    st.markdown("---")

    tab1, tab2 = st.tabs(["➕ Cadastrar Produto", "📋 Listar Produtos"])

    with tab1:
        st.markdown("### Cadastrar Novo Produto")
        col1, col2 = st.columns(2)
        with col1:
            nome_prod = st.text_input("Nome do Produto", placeholder="Ex: Bloco 14x19x39")
            preco_prod = st.number_input("Preço de Venda (R$ por unidade)", min_value=0.0, step=0.01, format="%.4f")
        with col2:
            desc_prod = st.text_area("Descrição", placeholder="Ex: Bloco estrutural traço 1:6")

        if st.button("💾 Cadastrar Produto"):
            if nome_prod.strip():
                cadastrar_produto(nome_prod.strip(), preco_prod, desc_prod)
                st.success(f"✅ Produto '{nome_prod}' cadastrado!")
                st.rerun()
            else:
                st.error("❌ Digite o nome do produto.")

    with tab2:
        st.markdown("### Produtos Cadastrados")
        produtos = listar_produtos()
        if produtos:
            for p in produtos:
                custo = calcular_custo(p["id"])
                lucro = p["preco_venda"] - custo
                margem = (lucro / p["preco_venda"] * 100) if p["preco_venda"] > 0 else 0

                with st.expander(f"🧱 {p['nome']} — Venda: R$ {p['preco_venda']:.4f} | Lucro: R$ {lucro:.4f} | Margem: {margem:.1f}%"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Custo de Produção", f"R$ {custo:.4f}")
                    with col2:
                        st.metric("Preço de Venda", f"R$ {p['preco_venda']:.4f}")
                    with col3:
                        st.metric("Lucro por Unidade", f"R$ {lucro:.4f}")

                    if p["descricao"]:
                        st.markdown(f"*{p['descricao']}*")

                    if st.button(f"🗑️ Remover produto", key=f"del_prod_{p['id']}"):
                        deletar_produto(p["id"])
                        st.success("Produto removido.")
                        st.rerun()
        else:
            st.info("Nenhum produto cadastrado ainda.")


# ==============================
# PÁGINA: RECEITAS
# ==============================
elif pagina == "📋 Receitas":
    st.title("📋 Receitas de Produção")
    st.markdown("Define quais e quantos insumos são usados para produzir cada bloco")
    st.markdown("---")

    produtos = listar_produtos()
    insumos = listar_insumos()

    if not produtos:
        st.warning("Cadastre produtos primeiro.")
    elif not insumos:
        st.warning("Cadastre insumos primeiro.")
    else:
        tab1, tab2 = st.tabs(["➕ Adicionar Ingrediente", "📋 Ver Receitas"])

        with tab1:
            st.markdown("### Adicionar Insumo à Receita")
            col1, col2 = st.columns(2)
            with col1:
                prods_map = {p["nome"]: p["id"] for p in produtos}
                sel_prod = st.selectbox("Produto", list(prods_map.keys()), key="rec_prod")
            with col2:
                ins_map = {f"{i['nome']} ({i['unidade']})": i["id"] for i in insumos}
                sel_ins = st.selectbox("Insumo", list(ins_map.keys()), key="rec_ins")

            qtd_rec = st.number_input(
                "Quantidade usada por unidade produzida",
                min_value=0.0001,
                step=0.001,
                format="%.4f",
                help="Ex: para fazer 1 bloco, usa 1.5 kg de cimento → coloque 1.5"
            )

            if st.button("💾 Salvar na Receita"):
                adicionar_receita(prods_map[sel_prod], ins_map[sel_ins], qtd_rec)
                st.success(f"✅ Receita atualizada para '{sel_prod}'!")
                st.rerun()

        with tab2:
            st.markdown("### Composição de Cada Produto")
            prods_map2 = {p["nome"]: p["id"] for p in produtos}
            sel_prod2 = st.selectbox("Ver receita do produto:", list(prods_map2.keys()), key="ver_rec")

            receita = listar_receita(prods_map2[sel_prod2])
            if receita:
                custo_total = sum(r["custo_total"] for r in receita)
                st.markdown(f"**Custo total por unidade: R$ {custo_total:.4f}**")

                df_rec = pd.DataFrame(receita)
                df_rec = df_rec[["nome", "quantidade", "unidade", "custo_unitario", "custo_total"]]
                df_rec.columns = ["Insumo", "Qtd/Unidade", "Unidade", "Custo Unit. (R$)", "Custo Total (R$)"]
                st.dataframe(df_rec, use_container_width=True, hide_index=True)

                st.markdown("---")
                st.markdown("### 🗑️ Remover Insumo da Receita")
                rec_ids = {f"{r['nome']} — {r['quantidade']} {r['unidade']}": r["id"] for r in receita}
                sel_rem = st.selectbox("Insumo para remover", list(rec_ids.keys()))
                if st.button("Remover da Receita"):
                    deletar_item_receita(rec_ids[sel_rem])
                    st.success("Removido!")
                    st.rerun()
            else:
                st.info(f"Nenhum insumo adicionado à receita de '{sel_prod2}' ainda.")


# ==============================
# PÁGINA: PRODUÇÃO
# ==============================
elif pagina == "⚙️ Produção":
    st.title("⚙️ Registrar Produção")
    st.markdown("---")

    tab1, tab2 = st.tabs(["🔨 Produzir", "📜 Histórico"])

    with tab1:
        produtos = listar_produtos()
        if not produtos:
            st.warning("Cadastre produtos e suas receitas primeiro.")
        else:
            st.markdown("### Iniciar Produção")
            prods_map = {p["nome"]: p["id"] for p in produtos}
            sel_prod = st.selectbox("Produto a produzir", list(prods_map.keys()))
            qtd_prod = st.number_input("Quantidade de blocos", min_value=1, step=1)

            produto_id = prods_map[sel_prod]

            # Preview de insumos necessários
            receita = listar_receita(produto_id)
            if receita:
                st.markdown("#### 📊 Insumos necessários para essa produção:")
                preview = []
                for r in receita:
                    necessario = r["quantidade"] * qtd_prod
                    insumos_bd = listar_insumos()
                    insumo_bd = next((i for i in insumos_bd if i["nome"] == r["nome"]), None)
                    estoque_atual = insumo_bd["quantidade"] if insumo_bd else 0
                    ok = "✅" if estoque_atual >= necessario else "❌"
                    preview.append({
                        "Status": ok,
                        "Insumo": r["nome"],
                        "Necessário": f"{necessario:.2f} {r['unidade']}",
                        "Em Estoque": f"{estoque_atual:.2f} {r['unidade']}"
                    })

                df_prev = pd.DataFrame(preview)
                st.dataframe(df_prev, use_container_width=True, hide_index=True)

                # Verificar viabilidade
                insuficientes = verificar_estoque_producao(produto_id, qtd_prod)

                if insuficientes:
                    st.markdown("---")
                    st.error("❌ Estoque insuficiente para produzir:")
                    for item in insuficientes:
                        st.markdown(f"""
                        <div class="alerta-critico">
                            ❌ <strong>{item['insumo']}</strong>: 
                            necessário {item['necessario']:.2f}, 
                            disponível {item['estoque']:.2f}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    custo_total = sum(r["custo_total"] for r in receita) * qtd_prod
                    insumos_bd = listar_insumos()
                    prod_info = next((p for p in listar_produtos() if p["id"] == produto_id), None)
                    faturamento = prod_info["preco_venda"] * qtd_prod if prod_info else 0

                    st.markdown("---")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Custo Total", f"R$ {custo_total:.2f}")
                    with col2:
                        st.metric("Faturamento Previsto", f"R$ {faturamento:.2f}")
                    with col3:
                        st.metric("Lucro Previsto", f"R$ {faturamento - custo_total:.2f}")

                    if st.button(f"🚀 Confirmar Produção de {qtd_prod} unidades"):
                        produzir(produto_id, qtd_prod)
                        st.success(f"✅ {qtd_prod} blocos de '{sel_prod}' produzidos! Estoque atualizado.")
                        st.balloons()
                        st.rerun()
            else:
                st.warning(f"Produto '{sel_prod}' não tem receita cadastrada. Vá em 'Receitas' para adicionar.")

    with tab2:
        st.markdown("### Histórico de Produções")
        historico = historico_producao()
        if historico:
            df = pd.DataFrame(historico)
            df.columns = ["Produto", "Quantidade", "Data/Hora", "Faturamento"]
            df["Faturamento"] = df["Faturamento"].apply(lambda x: f"R$ {x:,.2f}")
            df["Data/Hora"] = pd.to_datetime(df["Data/Hora"]).dt.strftime("%d/%m/%Y %H:%M")
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma produção registrada ainda.")


# ==============================
# PÁGINA: RELATÓRIOS
# ==============================
elif pagina == "📈 Relatórios":
    st.title("📈 Relatórios e Análises")
    st.markdown("---")

    tab1, tab2 = st.tabs(["💰 Margem por Produto", "📦 Análise de Estoque"])

    with tab1:
        st.markdown("### Custo × Venda × Lucro")
        relatorio = relatorio_produtos()
        if relatorio:
            for item in relatorio:
                cor = "#30D158" if item["lucro"] > 0 else "#FF453A"
                st.markdown(f"""
                <div style="
                    background: #2C2C2E;
                    border-radius: 12px;
                    padding: 16px 20px;
                    margin: 10px 0;
                    border-left: 4px solid {cor};
                ">
                    <div style="font-size:17px; font-weight:800; color:#F0F0F0;">{item['nome']}</div>
                    <div style="margin-top:8px; display:flex; gap:30px; flex-wrap:wrap;">
                        <span style="color:#AEAEB2;">Custo: <strong style="color:#F0F0F0;">R$ {item['custo']:.4f}</strong></span>
                        <span style="color:#AEAEB2;">Venda: <strong style="color:#F0F0F0;">R$ {item['preco_venda']:.4f}</strong></span>
                        <span style="color:#AEAEB2;">Lucro: <strong style="color:{cor};">R$ {item['lucro']:.4f}</strong></span>
                        <span style="color:#AEAEB2;">Margem: <strong style="color:{cor};">{item['margem']:.1f}%</strong></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Tabela exportável
            st.markdown("---")
            st.markdown("### 📥 Exportar Dados")
            df_exp = pd.DataFrame(relatorio)
            df_exp.columns = ["ID", "Produto", "Custo (R$)", "Venda (R$)", "Lucro (R$)", "Margem (%)"]
            csv = df_exp.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Baixar CSV",
                csv,
                "relatorio_produtos.csv",
                "text/csv"
            )
        else:
            st.info("Cadastre produtos e receitas para gerar relatório.")

    with tab2:
        st.markdown("### Situação do Estoque")
        insumos = listar_insumos()
        if insumos:
            total_val = sum(i["quantidade"] * i["custo_unitario"] for i in insumos)
            st.metric("Valor Total em Estoque", f"R$ {total_val:,.2f}")
            st.markdown("---")

            df_ins = pd.DataFrame(insumos)
            df_ins["valor_total"] = df_ins["quantidade"] * df_ins["custo_unitario"]
            df_ins["status"] = df_ins.apply(
                lambda r: "🔴 Crítico" if r["quantidade"] <= r["estoque_minimo"] else "✅ OK", axis=1
            )
            df_ins = df_ins[["nome", "quantidade", "unidade", "custo_unitario", "valor_total", "estoque_minimo", "status"]]
            df_ins.columns = ["Insumo", "Qtd", "Unidade", "Custo Unit.", "Valor em Estoque", "Estoque Mín.", "Status"]
            st.dataframe(df_ins, use_container_width=True, hide_index=True)

            st.markdown("---")
            csv2 = df_ins.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Baixar CSV do Estoque", csv2, "estoque.csv", "text/csv")
        else:
            st.info("Nenhum insumo cadastrado.")


# ==============================
# PÁGINA: MOVIMENTAÇÕES
# ==============================
elif pagina == "🔄 Movimentações":
    st.title("🔄 Histórico de Movimentações")
    st.markdown("Entradas e saídas de todos os insumos")
    st.markdown("---")

    insumos = listar_insumos()

    opcoes = ["Todos"] + [i["nome"] for i in insumos]
    filtro = st.selectbox("Filtrar por insumo", opcoes)

    if filtro == "Todos":
        movs = historico_movimentacoes()
    else:
        insumo_sel = next(i for i in insumos if i["nome"] == filtro)
        movs = historico_movimentacoes(insumo_sel["id"])

    if movs:
        df = pd.DataFrame(movs)
        df.columns = ["Insumo", "Tipo", "Quantidade", "Data/Hora", "Observação"]
        df["Data/Hora"] = pd.to_datetime(df["Data/Hora"]).dt.strftime("%d/%m/%Y %H:%M")

        def color_tipo(val):
            if val == "ENTRADA":
                return "color: #30D158; font-weight: bold"
            elif val == "SAÍDA":
                return "color: #FF453A; font-weight: bold"
            return ""

        st.dataframe(
            df.style.applymap(color_tipo, subset=["Tipo"]),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma movimentação registrada ainda.")