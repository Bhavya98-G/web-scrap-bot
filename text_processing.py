import re
import unicodedata
import hashlib
from typing import List, Dict, Optional


class TextChunker:
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        unit: str = "words"  # words | characters
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.unit = unit

    # -------------------------------
    # 1. TEXT CLEANING & NORMALIZATION
    # -------------------------------
    def clean_text(self, text: str) -> str:
        if not text:
            return ""

        text = unicodedata.normalize("NFKC", text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    # -------------------------------
    # 2. SEMANTIC SPLITTING
    # -------------------------------
    def semantic_split(self, text: str) -> List[str]:
        """
        Split text into semantic sections using:
        - Headings (if present)
        - Paragraph fallback
        """
        # Try heading-based split
        sections = re.split(r'\n\s*(?:#+|\d+\.)\s+', text)

        # If headings not found, fallback to paragraphs
        if len(sections) <= 1:
            sections = re.split(r'\n{2,}', text)

        return [s.strip() for s in sections if s.strip()]

    # -------------------------------
    # 3. CHUNKING LOGIC
    # -------------------------------
    def chunk_section(self, section: str) -> List[str]:
        chunks = []

        if self.unit == "characters":
            start = 0
            while start < len(section):
                end = start + self.chunk_size
                chunk = section[start:end]
                chunks.append(chunk)
                start = end - self.chunk_overlap

        else:  # default: words
            words = section.split()
            start = 0

            while start < len(words):
                end = start + self.chunk_size
                chunk_words = words[start:end]
                chunks.append(" ".join(chunk_words))
                start = end - self.chunk_overlap

        return chunks

    # -------------------------------
    # 4. MAIN PIPELINE
    # -------------------------------
    def process(
        self,
        raw_text: str
    ) -> List[Dict]:

        cleaned_text = self.clean_text(raw_text)
        sections = self.semantic_split(cleaned_text)

        final_chunks = []
        chunk_index = 0

        for section in sections:
            section_chunks = self.chunk_section(section)

            for chunk in section_chunks:
            #     chunk_id = self._generate_chunk_id(
            #         source_url, chunk_index
            #     )

                final_chunks.append({
                    # "chunk_id": chunk_id,
                    "chunk_index": chunk_index,
                    "chunk_text": chunk,
                })

                chunk_index += 1

        return final_chunks

    # -------------------------------
    # 5. HELPER
    # -------------------------------
    # def _generate_chunk_id(self, url: str, index: int) -> str:
    #     raw = f"{url}_{index}".encode("utf-8")
    #     return hashlib.md5(raw).hexdigest()
if __name__ == "__main__":
    text = """
    Introduction
    Text chunking is an important step in NLP pipelines.

    Why Chunking Matters
    Chunking helps preserve semantic meaning and improves retrieval quality.
    """

    chunker = TextChunker(
        chunk_size=50,
        chunk_overlap=10,
        unit="words"
    )

    chunks = chunker.process(
        raw_text=text
    )

    for c in chunks:
        print(c)
        print("-" * 80)
