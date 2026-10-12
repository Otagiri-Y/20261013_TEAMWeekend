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

        st.divider()