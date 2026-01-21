import time
import streamlit as st
from dotenv import load_dotenv

from webscrap import extract_meaningful_text

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.schema import TextNode
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --------------------------------------------------
# SAFETY: Disable LLM completely (NO OpenAI ever)
# --------------------------------------------------
Settings.llm = None

# --------------------------------------------------
# Local Embeddings (NO API KEY)
# --------------------------------------------------
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

load_dotenv()

# --------------------------------------------------
# Streamlit Config
# --------------------------------------------------
st.set_page_config(
    page_title="Website Q&A Bot",
    layout="wide"
)

# --------------------------------------------------
# Session State
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Enter a website URL and ask questions based only on its content."
        }
    ]

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "website_loaded" not in st.session_state:
    st.session_state.website_loaded = False

# --------------------------------------------------
# Helper Functions
# --------------------------------------------------
def stream_data(text: str):
    for word in text.split():
        yield word + " "
        time.sleep(0.03)

def chunk_text(text, chunk_size=900, overlap=120):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("🌐 Website Q&A Chatbot (No LLM)")

# Chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# URL input
url_input = st.text_input(
    "Enter Website URL",
    placeholder="https://example.com"
)

# --------------------------------------------------
# Website Processing
# --------------------------------------------------
if url_input and not st.session_state.website_loaded:
    with st.spinner("🔍 Extracting and indexing website..."):
        result = extract_meaningful_text(url_input)

        if result["status"] != "success":
            st.error(f"❌ {result['message']}")
            st.stop()

        title = result["title"]
        text = result["content"]

        if not text.strip():
            st.error("❌ No meaningful content found.")
            st.stop()

        chunks = chunk_text(text)

        nodes = [
            TextNode(
                text=chunk,
                metadata={
                    "source_url": url_input,
                    "title": title
                }
            )
            for chunk in chunks
        ]

        index = VectorStoreIndex(nodes, show_progress=True)

        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=5
        )

        st.session_state.retriever = retriever
        st.session_state.website_loaded = True

    st.success(f"✅ Website loaded successfully: **{title}**")

# --------------------------------------------------
# Chat Input (PURE EXTRACTIVE QA)
# --------------------------------------------------
if prompt := st.chat_input(
    "Ask a question about the website...",
    disabled=not st.session_state.website_loaded
):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("assistant"):
        with st.spinner("🔎 Searching website content..."):
            results = st.session_state.retriever.retrieve(prompt)

            if not results:
                answer = "The answer is not available on the provided website."
            else:
                # Extract top matching chunks
                answer = "\n\n".join(
                    r.node.text for r in results[:3]
                )

            st.write_stream(stream_data(answer))

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
