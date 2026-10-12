import re
import unicodedata

from search import expand_query, normalize_text


def _make_preview(text: str, query: str, ctx: int = 200) -> str:
    if not text:
        return ""

    text = normalize_text(text)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) <= ctx:
        return text

    sentences = re.split(r"(?<=[。！？!?])", text)
    selected = []
    total = 0

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        if total + len(sentence) > ctx and selected:
            break

        selected.append(sentence)
        total += len(sentence)

    preview = "".join(selected).strip()

    if len(preview) < len(text):
        preview += "..."

    return preview


def _extract_section(text: str, headings: list[str]) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    heading_aliases = {
        "decision": [
            "決定事項",
            "決定内容",
            "決定結果",
            "協議結果",
            "合意事項",
            "決議事項",
            "決定事項・対応事項",
        ],
        "pending": [
            "継続検討事項・宿題",
            "継続検討事項",
            "未決事項",
            "未決事項・課題",
            "今後の宿題",
            "宿題事項",
            "宿題",
            "対応事項",
            "今後の対応",
            "今後のアクション",
            "アクションアイテム",
            "次回までの対応",
            "次回までの確認事項",
            "継続課題",
            "残課題",
            "課題・対応事項",
        ],
    }

    category = (
        "decision"
        if any(h in heading_aliases["decision"] for h in headings)
        else "pending"
    )

    aliases = heading_aliases[category]

    next_headings = set(
        heading_aliases["decision"]
        + heading_aliases["pending"]
        + [
            "協議内容",
            "開催日",
            "開催時刻",
            "開催場所",
            "出席者",
            "参加者",
            "議題",
            "備考",
            "次第",
            "背景・目的",
        ]
    )

    heading_pattern = "|".join(
        re.escape(h) for h in sorted(aliases, key=len, reverse=True)
    )

    next_pattern = "|".join(
        re.escape(h) for h in sorted(next_headings, key=len, reverse=True)
    )

    prefix_pattern = r"(?:[0-9０-９]+[.．、)]\s*|[（(][0-9０-９]+[）)]\s*|【\s*)?"
    suffix_pattern = r"(?:\s*】)?"

    pattern = (
        rf"^[ \t　]*{prefix_pattern}(?:{heading_pattern}){suffix_pattern}[ \t　]*[:：]?[ \t　]*(?:\n|$)"
        rf"(.*?)"
        rf"(?=^[ \t　]*{prefix_pattern}(?:{next_pattern}){suffix_pattern}[ \t　]*[:：]?[ \t　]*(?:\n|$)|\Z)"
    )

    match = re.search(
        pattern,
        text,
        re.MULTILINE | re.DOTALL
    )

    if not match:
        return ""

    return re.sub(r"\s+", " ", match.group(1)).strip()

def search_fulltext(query: str, pages: list) -> list:
    if not query.strip():
        return []

    results = []
    queries = expand_query(query)

    for page in pages:
        kw = page.get("keywords", [])

        if isinstance(kw, str):
            kw = [
                k.strip()
                for k in kw.split(",")
                if k.strip()
            ]

        full_text = page.get("full_text", "") or ""

        text = " ".join([
            page.get("title", "") or "",
            page.get("description", "") or "",
            full_text,
            " ".join(kw),
        ])

        normalized_text = normalize_text(text).lower()

        match_count = sum(
            normalized_text.count(normalize_text(q).lower())
            for q in queries
            if normalize_text(q).strip()
        )

        if match_count > 0:
            result = page.copy()

            result["match_count"] = match_count

            result["preview"] = _make_preview(
                full_text or page.get("description", ""),
                query
            )

            result["decision"] = _extract_section(
                full_text,
                ["決定事項", "決定内容", "決定結果", "協議結果", "合意事項"]
            )

            result["pending"] = _extract_section(
                full_text,
                [
                    "継続検討事項・宿題",
                    "継続検討事項",
                    "未決事項",
                    "今後の宿題",
                    "宿題事項",
                    "宿題",
                    "対応事項",
                    "今後の対応",
                    "今後のアクション",
                    "アクションアイテム",
                    "次回までの対応",
                    "次回までの確認事項",
                    "継続課題",
                    "残課題",
                    "課題・対応事項",
                ]
            )

            results.append(result)

    results.sort(
        key=lambda x: x["match_count"],
        reverse=True
    )

    return results

def add_sections(result: dict, query: str) -> dict:
    """TF-IDFの検索結果1件に、概要・決定事項・宿題を付けて返す。"""
 
    full_text = result.get("full_text", "") or ""
    result = result.copy()
    result["preview"] = _make_preview(full_text, query)
    result["decision"] = _extract_section(
        full_text,
        ["決定事項", "決定内容", "決定結果", "協議結果", "合意事項"]
    )
    result["pending"] = _extract_section(
        full_text,
        ["継続検討事項・宿題", "継続検討事項", "未決事項", "今後の宿題", "宿題"]
    )
    return result