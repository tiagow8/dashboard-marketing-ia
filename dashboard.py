import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="AI Marketing Dashboard", layout="wide")

st.title("📊 Dashboard de Marketing com IA")
st.caption("Análise de campanhas + ChatGPT integrado")

# =========================
# API KEY
# =========================
api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password")

client = None
if api_key:
    client = OpenAI(api_key=api_key)

# =========================
# UPLOAD CSV
# =========================
arquivo = st.file_uploader("📂 Envie seu CSV", type=["csv"])

if arquivo:

    df = pd.read_csv(arquivo)
    df.columns = df.columns.str.lower().str.strip()

    # =========================
    # MÉTRICAS
    # =========================
    df["ctr"] = (df["cliques"] / df["impressoes"]) * 100
    df["cpc"] = df["custo"] / df["cliques"].replace(0, 1)
    df["cpa"] = df["custo"] / df["conversoes"].replace(0, 1)
    df["roi"] = df["receita"] / df["custo"]

    # =========================
    # FILTROS
    # =========================
    st.sidebar.header("🎯 Filtros")

    canais = st.sidebar.multiselect(
        "Canal",
        df["canal"].unique(),
        default=df["canal"].unique()
    )

    df = df[df["canal"].isin(canais)]

    # =========================
    # KPIs
    # =========================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📈 CTR Médio", f"{df['ctr'].mean():.2f}%")
    col2.metric("💰 CPC Médio", f"R${df['cpc'].mean():.2f}")
    col3.metric("📉 CPA Médio", f"R${df['cpa'].mean():.2f}")
    col4.metric("🚀 ROI Médio", f"{df['roi'].mean():.2f}")

    # =========================
    # GRÁFICO
    # =========================
    st.subheader("📊 ROI por Canal")

    canal_group = df.groupby("canal").agg({
        "receita": "sum",
        "custo": "sum"
    })

    canal_group["roi"] = canal_group["receita"] / canal_group["custo"]

    fig = px.bar(
        canal_group,
        y="roi",
        title="ROI por Canal",
        color=canal_group.index
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # TABELA
    # =========================
    st.subheader("📋 Dados")
    st.dataframe(df, use_container_width=True)

    # =========================
    # CHATGPT
    # =========================
    st.subheader("💬 Chat com IA")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    pergunta = st.text_input("Pergunte algo sobre os dados")

    if st.button("Enviar") and pergunta:

        if not client:
            st.error("Insira sua API Key na sidebar")
        else:
            with st.spinner("IA analisando..."):

                resumo = df.describe().to_string()

                prompt = f"""
                Você é um especialista em marketing digital.

                Dados:
                {resumo}

                Pergunta:
                {pergunta}

                Responda de forma clara e estratégica.
                """

                resposta = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[
                        {"role": "system", "content": "Você é especialista em marketing"},
                        {"role": "user", "content": prompt}
                    ]
                )

                resposta_texto = resposta.choices[0].message.content

                st.session_state.chat.append(("Você", pergunta))
                st.session_state.chat.append(("IA", resposta_texto))

    # =========================
    # HISTÓRICO
    # =========================
    for autor, msg in st.session_state.chat:
        if autor == "Você":
            st.markdown(f"🧑 **Você:** {msg}")
        else:
            st.markdown(f"🤖 **IA:** {msg}")

else:
    st.info("Envie um CSV para começar")