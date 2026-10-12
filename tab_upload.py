from datetime import date
from pathlib import Path

import streamlit as st

from extract import extract_text
from ingest import extract_held_on, ingest_meeting


def make_title(file_name):  # file_name = ファイル名
    # 1. file_name の拡張子を除く。結果を「会議名（title）」と呼ぶ
    title = Path(file_name).stem
    # 2. 会議名（title）を返す
    return title


def guess_held_on(uploaded_file):  # uploaded_file = アップロードされたファイル
    # 1. ファイルから本文（text）を取り出す。読めなければ、空の開催日を返して終わる
    try:
        text = extract_text(uploaded_file.name, uploaded_file.getvalue())
    except ValueError:
        return ""
    # 2. 本文から開催日を取り出して返す
    return extract_held_on(text)


def render():
    st.subheader("会議録アップロード")

    # 1. 複数のファイルを選べる欄を出す
    uploaded_files = st.file_uploader(
        "会議録ファイルを選択してください（複数可）",
        type=["docx", "pdf", "txt"],
        accept_multiple_files=True,
    )

    # 2. ファイルごとに、会議名と開催日の入力欄を並べる（自動で入った値を、手で直せる）
    inputs = []
    for uploaded_file in uploaded_files:
        st.caption(f"📄 {uploaded_file.name}")
        col_title, col_date = st.columns([3, 1])
        title = col_title.text_input(
            "会議名",
            value=make_title(uploaded_file.name),
            key=f"title_{uploaded_file.file_id}",
        )
        held_on = col_date.text_input(
            "開催日（例：2026-10-08）",
            value=guess_held_on(uploaded_file),
            key=f"held_on_{uploaded_file.file_id}",
        )
        inputs.append((uploaded_file, title.strip(), held_on.strip()))

    # 3. 「登録」が押されたときの処理
    if st.button("会議録を登録"):
        if not inputs:
            st.warning("会議録ファイルを選択してください。")
            return

        success_count = 0
        duplicate_names = []
        failed = []

        for uploaded_file, title, held_on in inputs:
            # 開催日が入っているときだけ、日付として正しいか確かめる
            if held_on:
                try:
                    date.fromisoformat(held_on)
                except ValueError:
                    failed.append(f"{uploaded_file.name}（開催日の形式が違います）")
                    continue

            result = ingest_meeting(
                uploaded_file.name,
                uploaded_file.getvalue(),
                title,
                held_on,
            )
            status = result.get("状態")
            if status == "success":
                success_count += 1
            elif status == "duplicate":
                duplicate_names.append(uploaded_file.name)
            else:
                reason = result.get("エラー内容") or "登録に失敗しました"
                failed.append(f"{uploaded_file.name}（{reason}）")

        # 4. 結果を表示する
        if success_count > 0:
            st.success(f"{success_count}件の会議録を登録しました！")
            st.cache_resource.clear()  # 検索側のデータを、次の操作で読み直させる
        if duplicate_names:
            st.warning("登録済みのファイル：" + "、".join(duplicate_names))
        if failed:
            st.error("登録に失敗したファイル：" + "、".join(failed))