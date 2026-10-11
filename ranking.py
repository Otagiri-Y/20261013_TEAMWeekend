from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SearchEngine:
    def __init__(self):
        self.pages = []
        self.vectorizer = TfidfVectorizer(
            analyzer="char",
            ngram_range=(2, 4)
        )
        self.tfidf_matrix = None

    def build_index(self, pages):
        """検索対象の段落をTF-IDFでベクトル化する。"""

        self.pages = pages

        documents = []

        for page in pages:
            keywords = page.get("keywords", [])

            if isinstance(keywords, list):
                keywords = " ".join(keywords)

            text = " ".join([
                page.get("title", "") or "",
                page.get("description", "") or "",
                page.get("full_text", "") or "",
                keywords or "",
            ])

            documents.append(text)

        if not documents:
            self.tfidf_matrix = None
            return

        self.tfidf_matrix = self.vectorizer.fit_transform(documents)

    def search(self, query, top_n=10):
        """検索語との類似度が高い段落を上位から返す。"""

        if not query.strip():
            return []

        if self.tfidf_matrix is None:
            return []

        query_vector = self.vectorizer.transform([query])

        similarities = cosine_similarity(
            query_vector,
            self.tfidf_matrix
        ).flatten()

        results = []

        for index, base_score in enumerate(similarities):
            if base_score <= 0:
                continue
        for index, base_score in enumerate(similarities):


            result = self.pages[index].copy()

            result["base_score"] = float(base_score)

            relevance_score = float(base_score)

            word_count = result.get("word_count")
            if word_count is not None and word_count < 50:
                relevance_score *= 0.7

            result["relevance_score"] = relevance_score

            results.append(result)

        results.sort(
            key=lambda x: x["relevance_score"],
            reverse=True
        )

        return results[:top_n]

_engine = SearchEngine()


def get_engine():
    return _engine


def rebuild_index(pages):
    _engine.build_index(pages)