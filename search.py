import re
import unicodedata

def normalize_text(text: str) -> str:
    """全角・半角のゆれをそろえる（例: ＡＩ → AI）"""
    return unicodedata.normalize("NFKC", text or "")

def expand_query(query: str) -> list[str]:
    """検索語を、検索に使う語のリストにする"""
    q = query.strip()
    words = q.split()
    return [q] + [w for w in words if w != q]

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
    """説明文の中のキーワードを **太字** にする"""

    if not query:              
        return text

    pattern = re.compile(
        re.escape(query),        
        re.IGNORECASE                 
    )

   
    return pattern.sub(f"**{query}**", text)

