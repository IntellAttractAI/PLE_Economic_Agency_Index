import streamlit as st
import pandas as pd
import pydeck as pdk
import openai
from streamlit.components.v1 import html

PARQUET_PATH = "data/eai_geo.parquet"
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
YOUTUBE_CHANNEL_ID = st.secrets.get("YOUTUBE_CHANNEL_ID", "")
openai.api_key = OPENAI_API_KEY

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()

st.set_page_config(layout="wide", page_title="EAI Dashboard & Quiz")
mode = st.sidebar.selectbox("Mode", ["Dashboard", "Quiz"], index=0)

if mode == "Dashboard":
    st.title("Post-Labor Economics: Economic Agency Index")
    df = load_data(PARQUET_PATH)
    if not df.empty:
        years = sorted(df['year'].unique())
        year = st.sidebar.slider("Year", int(min(years)), int(max(years)), int(max(years)))
        df_year = df[df['year'] == year]
        layer = pdk.Layer(
            "GeoJsonLayer",
            data=df_year,
            get_fill_color="[255 * (1 - eai), 255 * eai, 50]",
            pickable=True,
        )
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=pdk.ViewState(latitude=37.5, longitude=-96, zoom=3)))
        st.sidebar.download_button("Download Data", df_year.to_parquet(), file_name="eai.parquet")
    else:
        st.write("No data available.")

    st.sidebar.markdown("### Chatbot")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    question = st.sidebar.text_input("Ask a question")
    if st.sidebar.button("Send") and question:
        st.session_state.messages.append({"role": "user", "content": question})
        resp = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=st.session_state.messages)
        answer = resp.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.sidebar.write(answer)

    if YOUTUBE_CHANNEL_ID:
        html(f'<iframe width="100%" height="200" src="https://www.youtube.com/embed?listType=user_uploads&list={YOUTUBE_CHANNEL_ID}" frameborder="0" allowfullscreen></iframe>', height=200)

elif mode == "Quiz":
    st.title("EAI Knowledge Quiz")
    questions = [
        ("What does the Economic Agency Index measure?", ["Balance of earned, property, and transfer income", "Total GDP", "Employment rate", "Inflation"], 0),
        ("Which BEA table supplies the core data?", ["CAINC7", "CAINC1", "SAINC1", "QCEW"], 0),
        ("Which component is subtracted in the EAI formula?", ["Earned-income share", "Property-income share", "Transfer-income share", "Population"], 2),
        ("Which visualization library is used for the map?", ["pydeck", "matplotlib", "bokeh", "seaborn"], 0),
        ("A z-score of 0 indicates?", ["Value equals mean", "Value equals median", "Value is zero", "Value equals sd"], 0),
        ("Which service hosts the mobile code?", ["Expo", "Apache", "Kubernetes", "Django"], 0),
        ("What does the slider control?", ["Year", "County", "Color", "API"], 0),
        ("Preferred data storage format?", ["Parquet", "CSV", "TXT", "XML"], 0),
        ("Which dataset fills suppressed cells?", ["IRS SOI AGI", "Census TIGER", "OECD", "World Bank"], 0),
        ("Score >=80% results in?", ["Badge image", "Reload", "Reset", "Close"], 0),
    ]
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = [None] * len(questions)

    for i, (q, opts, _) in enumerate(questions):
        st.session_state.quiz_answers[i] = st.radio(q, opts, key=f"q{i}")

    if st.button("Submit Quiz"):
        score = 0
        for (q, opts, correct), ans in zip(questions, st.session_state.quiz_answers):
            if opts.index(ans) == correct:
                score += 1
        percent = score / len(questions) * 100
        st.write(f"Your score: {percent:.0f}%")
        if percent >= 80:
            try:
                st.image("badge.png")
            except Exception:
                st.write("Badge")
