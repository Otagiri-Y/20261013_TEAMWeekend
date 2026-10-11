import streamlit as st

from database import get_meeting
from search import highlight_terms


def go_back():
    """「検索結果に戻る」ボタンが押されたときの処理。"""

    # 「全体を見る」画面を閉じる（見ている会議のIDを空にする）
    st.session_state["selected_meeting_id"] = None

    # 検索語を、検索画面の入力欄に戻す
    st.session_state["search_keyword"] = st.session_state.get("saved_keyword", "")


def render_detail(meeting_id, keyword):
    """議事録の全体を表示する画面。検索語に色を付ける。"""

    st.button("← 検索結果に戻る", on_click=go_back)

    meeting = get_meeting(meeting_id)

    # 見つからなかったときは、メッセージを出して終わる
    if meeting is None:
        st.warning("該当の議事録がありません。")
        return

    st.subheader(meeting["title"])
    st.caption(f"開催日：{meeting['held_on']}")

    # 検索語に色を付けた全文を、HTMLとして表示する
    marked_text = highlight_terms(meeting["raw_text"], keyword)
    st.markdown(
        f'<div style="line-height: 1.8;">{marked_text}</div>',
        unsafe_allow_html=True
    )