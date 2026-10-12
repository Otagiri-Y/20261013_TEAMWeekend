import streamlit as st
 
from search import highlight_match
from ranking import rebuild_index, get_engine
from search_fulltext import add_sections
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
 
    rebuild_index(pages)
    results = get_engine().search(keyword, top_n=20)
    results = [add_sections(r, keyword) for r in results]
 
    if not results:
        st.warning("該当する会議録は見つかりませんでした。")
        return
 
    st.write(f"検索結果：{len(results)}件")
 
    for result in results:
        title = result.get("title", "会議名なし")
        highlighted_title = highlight_match(title, keyword)
 
        st.markdown(
            f"### {highlighted_title}",
            unsafe_allow_html=True
        )
 
        meeting_date = (
            result.get("held_on")
            or result.get("meeting_date")
            or result.get("crawled_at")
            or "日付不明"
        )
 
        st.caption(f"開催日：{meeting_date}")
 
        preview = result.get("preview", "")
 
        if preview:
            st.markdown("**📋 会議の概要**")
            highlighted_preview = highlight_match(preview, keyword)
            st.markdown(
                highlighted_preview,
                unsafe_allow_html=True
            )
 
        decision = result.get("decision", "")
 
        st.markdown("**✅ 決定事項**")
 
        if decision:
            st.write(decision)
        else:
            st.caption("決定事項の記載がありません。")
 
        pending = result.get("pending", "")
 
        st.markdown("**📝 継続検討事項・宿題**")
 
        if pending:
            st.write(pending)
        else:
            st.caption("継続検討事項・宿題の記載がありません。")
 
        meeting_id = result.get("meeting_id") or result.get("url")
 
        st.button(
            "全体を見る",
            key=f"view_{result['id']}",
            on_click=open_detail,
            args=(int(meeting_id), keyword)
        )
 
        st.divider()