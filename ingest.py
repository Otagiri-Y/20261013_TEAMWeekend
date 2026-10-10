import hashlib
import re
from extract import extract_text
from database import insert_meeting, insert_chunks

MIN_CHUNK_LEN = 3
MAX_CHUNK_LEN = 400

def split_chunks(text: str) -> list[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    chunks = []
    for block in re.split(r"\n\s*\n", text):
        block = re.sub(r"[\t\u3000]+", " ", block).strip()
        if len(block) < MIN_CHUNK_LEN:
            continue
        if len(block) <= MAX_CHUNK_LEN:
            chunks.append(block.replace("\n", " "))
            continue
        buf = ""
        for sent in re.split(r"(?<=[。！？!?\n])", block):
            if buf and len(buf) + len(sent) > MAX_CHUNK_LEN:
                chunks.append(buf.strip())
                buf = ""
            buf += sent
        if len(buf.strip()) >= MIN_CHUNK_LEN:
            chunks.append(buf.strip())
    return chunks

def ingest_meeting(file_name, data, title, held_on) -> dict:
    result = {"状態": "failed", "会議id": None, "段落数": 0, "エラー内容": None}
    try:
        text = extract_text(file_name, data)
        chunks = split_chunks(text)
        if not chunks:
            raise ValueError("本文が空です")
        file_hash = hashlib.sha256(data).hexdigest()
        title = (title or "").strip() or file_name
        meeting_id = insert_meeting(title, held_on, file_name, file_hash, text)
        if meeting_id is None:
            result["状態"] = "duplicate"
            result["エラー内容"] = "同じ内容のファイルが登録済みです"
            return result
        count = insert_chunks(meeting_id, chunks)
        result.update({"状態": "success", "会議id": meeting_id, "段落数": count})
    except Exception as e:
        result["エラー内容"] = str(e)
    return result