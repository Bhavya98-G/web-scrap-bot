from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class VectorStoreManager:
    def __init__(self, model_name="intfloat/e5-large-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.chunk_metadata = []
        
    def build_index(self, chunks):
        self.chunk_metadata = chunks
        texts_to_embed = [f"passage: {c['chunk_text']}" for c in chunks]
        embeddings = self.model.encode(texts_to_embed, normalize_embeddings=True)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(np.array(embeddings, dtype='float32'))
        print(f"Index built with {self.index.ntotal} vectors.")
    
    def query(self, question, top_k=3):
        if self.index is None:
            raise ValueError("Index has not been built. Call build_index() first.")
        question_embedding = self.model.encode([f"query: {question}"], normalize_embeddings=True)
        distances , indices = self.index.search(np.array(question_embedding, dtype='float32'), top_k)
        results = []
        for idx in indices[0]:
            if idx != -1: # Ensure valid index
                results.append(self.chunk_metadata[idx])
        return results