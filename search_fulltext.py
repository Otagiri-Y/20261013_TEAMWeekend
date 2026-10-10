import unicodedata

from search import expand_query, normalize_text


def _make_preview(text: str, query: str, ctx: int = 80) -> str:
    if not text or not query:
        return ""

    normalized_text = normalize_text(text).lower()
    normalized_query = normalize_text(query).lower()
    pos = normalized_text.find(normalized_query)

    if pos == -1:
        return (text[:200] + "...") if len(text) > 200 else text

    start = max(0, pos - ctx)
    end = min(len(text), pos + len(query) + ctx)

    preview = ""

    if start > 0:
        preview += "..."

    preview += text[start:end]

    if end < len(text):
        preview += "..."

    return preview


def search_fulltext(query: str, pages: list) -> list:
    if not query.strip():
        return []

    results = []
    queries = expand_query(query)

    for page in pages:
        kw = page.get("keywords", [])

        if isinstance(kw, str):
            kw = [k.strip() for k in kw.split(",") if k.strip()]

        text = " ".join([
            page.get("title", "") or "",
            page.get("description", "") or "",
            page.get("full_text", "") or "",
            " ".join(kw),
        ])

        normalized_text = normalize_text(text).lower()
        match_count = sum(
            normalized_text.count(normalize_text(q).lower())
            for q in queries
        )

        if match_count > 0:
            r = page.copy()
            r["match_count"] = match_count
            r["preview"] = _make_preview(
                page.get("full_text") or page.get("description", ""),
                query
            )
            results.append(r)

    results.sort(key=lambda x: x["match_count"], reverse=True)

    return results