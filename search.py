import re
import unicodedata
import html

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

def find_match_ranges(text: str, query: str) -> list[tuple[int, int]]:
    """文章の中で、検索語が出てくる場所を (開始位置, 終了位置) のリストで返す。
    全角・半角、大文字・小文字の違いは同じ語として扱う。
    終了位置は、その文字を含まない位置（text[開始:終了] で語を取り出せる）。
    """

    # 検索語をスペースで分け、探しやすい形（半角・小文字）にそろえる
    words = []
    for word in query.split():
        normalized_word = normalize_text(word).lower()
        if normalized_word:
            words.append(normalized_word)

    if not words:
        return []

    # 文章を1文字ずつそろえながら、元の文章での位置を覚えておく
    normalized = ""
    index_map = []  # index_map[i] = そろえた文章の i 文字目が、元の文章の何文字目か
    for i, ch in enumerate(text):
        n = normalize_text(ch).lower()
        normalized += n
        index_map.extend([i] * len(n))

    # それぞれの語が出てくる場所を、すべて探す
    ranges = []
    for word in words:
        start = 0
        while True:
            pos = normalized.find(word, start)
            if pos == -1:
                break
            end = pos + len(word)
            # そろえた文章での位置を、元の文章での位置に直して記録する
            ranges.append((index_map[pos], index_map[end - 1] + 1))
            start = end

    # 重なっている場所は、1つにまとめる
    ranges.sort()
    merged = []
    for s, e in ranges:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))

    return merged

def highlight_terms(text: str, query: str) -> str:
    """文章の中の検索語に <mark> を付けた、表示用のHTML文字列を返す。
    改行は <br> に変える。
    """

    ranges = find_match_ranges(text, query)

    result = ""
    last = 0  # ここまでは書き終えた、という元の文章での位置

    for start, end in ranges:
        # 検索語の手前までは、そのまま書く
        result += html.escape(text[last:start])
        # 検索語の部分は、<mark> で囲んで書く
        result += "<mark>" + html.escape(text[start:end]) + "</mark>"
        last = end

    # 最後の検索語より後ろを、そのまま書く
    result += html.escape(text[last:])

    # 改行を <br> に変える（HTMLでは、改行文字だけでは改行されないため）
    return result.replace("\r\n", "\n").replace("\n", "<br>")