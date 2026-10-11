import streamlit as st

from search import highlight_match
from search_fulltext import search_fulltext
from tab_detail import render_detail

def open_detail(meeting_id, keyword):  # ← 追加（この関数ごと）
    """「全体を見る」ボタンが押されたときの処理。"""

    # 見たい会議のIDと、そのときの検索語を、メモ帳に書いておく
    st.session_state["selected_meeting_id"] = meeting_id
    st.session_state["saved_keyword"] = keyword

def render(pages):
    # 見たい会議のIDがメモ帳にあれば、「全体を見る」画面を出して終わる
    selected_id = st.session_state.get("selected_meeting_id")
    if selected_id is not None:
        render_detail(selected_id, st.session_state.get("saved_keyword", ""))
        return

    st.subheader("会議録検索")
    
    keyword = st.text_input(
        "検索キーワード",
        placeholder="例：稟議書、効率化、ペーパーレス",
        key="search_keyword"
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

        st.button(
            "全体を見る",
            key=f"view_{result['id']}",
            on_click=open_detail,
            args=(result["meeting_id"], keyword)
        )
        st.divider()