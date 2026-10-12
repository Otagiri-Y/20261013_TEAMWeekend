import re
import unicodedata


def search_pages(query: str, pages: list) -> list:
    """キーワードでページを絞り込む（部分一致）"""

    if not query.strip():
        return [] 

    results = []
    query_lower = query.lower()

    for page in pages:          

        
        search_text = " ".join([
            page["title"],
            page["description"],
            " ".join(page["keywords"]),
        ])

       
        if query_lower in search_text.lower():
            results.append(page)   

    return results


def highlight_match(text: str, query: str) -> str:
    if not query:
        return text

    pattern = re.compile(
        re.escape(query),
        re.IGNORECASE
    )

    return pattern.sub(
        lambda m: f'<span style="background-color: #fff2a8; color: #333333; font-weight: bold; padding: 1px 2px; border-radius: 3px;">{m.group(0)}</span>',
        text
    )

def normalize_text(text: str) -> str:
    if not text:
        return ""
    return unicodedata.normalize("NFKC", str(text)).strip()


def expand_query(query: str) -> list:
    normalized_query = normalize_text(query)
    if not normalized_query:
        return []
    return [normalized_query]