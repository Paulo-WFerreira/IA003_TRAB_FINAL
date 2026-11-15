import streamlit as st

st.set_page_config(page_title="Planos de saúde no RS · IA003", page_icon=":material/monitoring:", layout="wide")

pagina = st.navigation([
    st.Page("paginas/inicio.py", title="Início", icon=":material/home:", default=True),
    st.Page("paginas/painel1_populacao.py", title="Painel 1 · População", icon=":material/groups:",
            url_path="populacao"),
    st.Page("paginas/painel2_amostra.py", title="Painel 2 · Amostra", icon=":material/filter_alt:",
            url_path="amostra"),
    st.Page("paginas/painel3_inferencia.py", title="Painel 3 · Inferência", icon=":material/functions:",
            url_path="inferencia"),
])
pagina.run()
