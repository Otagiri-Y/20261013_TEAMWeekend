import streamlit as st

from search import highlight_match
from search_fulltext import search_fulltext

def render(pages):
    st.subheader("会議録検索")
    
    keyword = st.text_input(
        "検索キーワード",
        placeholder="例：稟議書、効率化、ペーパーレス"
    )

    if not keyword.strip():
        st.info("キーワードを入力してください。")
        return

    results = search_fulltext(keyword, pages)

    if not results:
        st.warning("該当する会議録は見つかりませんでした。")
        return

    st.write(f"検索結果：{len(results)}件")

    for result in results:
        st.markdown(f"### {result.get('title', '会議名なし')}")
        
        meeting_date = (
            result.get("held_on")
            or result.get("crawled_at")
            or result.get("meeting_date")
            or "日付不明"
        )
        
        st.caption(f"開催日：{meeting_date}")
        
        preview = result.get("preview", "")
        highlighted_preview = highlight_match(preview, keyword)
        
        st.markdown(highlighted_preview)
        st.divider()