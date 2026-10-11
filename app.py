import streamlit as st
from database import init_db, get_search_pages, count_meetings
from tab_search import render as render_search
from tab_upload import render as render_upload

st.set_page_config(
    page_title="議事録検索アプリ",
    page_icon="🔍",
    layout="wide"
)

init_db()

@st.cache_resource
def load_pages():
    return get_search_pages()

pages = load_pages()

st.title("議事録検索")

with st.sidebar:
    st.header("登録状況")
    st.metric("会議数", count_meetings())

tab1, tab2 = st.tabs(["検索", "アップロード"])

with tab1:
    render_search(pages)

with tab2:
    render_upload()