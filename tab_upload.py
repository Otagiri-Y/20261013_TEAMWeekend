import streamlit as st

from ingest import ingest_meeting


def render():
    st.subheader("会議録アップロード")

    uploaded_file = st.file_uploader(
        "会議録ファイルを選択してください",
        type=["docx", "pdf","txt"]
    )

    title = st.text_input(
        "会議名",
        placeholder="例：融資審査AI検討会"
    )

    held_on = st.date_input("開催日")

    if st.button("会議録を登録"):
        if uploaded_file is None:
            st.warning("会議録ファイルを選択してください。")
            return

        if not title.strip():
            st.warning("会議名を入力してください。")
            return

        result = ingest_meeting(
            uploaded_file.name,        # ファイル名
            uploaded_file.getvalue(),  # 中身（bytes）
            title.strip(),
            held_on.isoformat(),
        )

        if result.get("状態") == "success":
            st.success("会議録を登録しました！")
            st.cache_data.clear()

        elif result.get("状態") == "duplicate":
            st.warning("この会議録はすでに登録されています。")

        else:
            st.error(
                result.get("エラー内容", "会議録の登録に失敗しました。")
            )
