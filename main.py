import streamlit as st
from webscrap import extract_meaningful_text
from text_processing import TextChunker
from embedding import VectorStoreManager
from ai_handler import answer_question, memory
import time
from datetime import datetime

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="Website Knowledge Assistant",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS FOR PREMIUM UI
# ============================================================================
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e2e 0%, #2d2d44 100%);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label {
        color: #e0e0e0 !important;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Success/Error/Warning boxes */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid rgba(102, 126, 234, 0.3);
        background-color: rgba(255, 255, 255, 0.05);
        color: #e0e0e0;
    }
    
    /* Title styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 700;
        color: #667eea;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: rgba(102, 126, 234, 0.1);
        border-radius: 10px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
def initialize_session_state():
    """Initialize all session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "index" not in st.session_state:
        st.session_state.index = None
    
    if "indexed_url" not in st.session_state:
        st.session_state.indexed_url = None
    
    if "title" not in st.session_state:
        st.session_state.title = None
    
    if "indexing_time" not in st.session_state:
        st.session_state.indexing_time = None
    
    if "total_chunks" not in st.session_state:
        st.session_state.total_chunks = 0
    
    if "content_preview" not in st.session_state:
        st.session_state.content_preview = ""

initialize_session_state()

# ============================================================================
# CORE FUNCTIONS
# ============================================================================
def index_website(url: str) -> tuple:
    """
    Index a website by scraping, chunking, and building vector embeddings.
    
    Args:
        url: The website URL to index
        
    Returns:
        tuple: (vector_store, title, chunks_count, content_preview)
    """
    start_time = time.time()
    
    # Extract content
    result = extract_meaningful_text(url)
    
    if result["status"] == "error":
        st.error(f"❌ {result['message']}")
        return None, "", 0, ""
    
    # Chunk the text
    chunker = TextChunker(
        chunk_size=500,
        chunk_overlap=100,
        unit="words"
    )
    chunks = chunker.process(result["content"])
    
    # Build vector index
    vector_store = VectorStoreManager()
    vector_store.build_index(chunks)
    
    elapsed_time = time.time() - start_time
    
    # Get content preview (first 500 chars)
    content_preview = result["content"][:500] + "..." if len(result["content"]) > 500 else result["content"]
    
    return vector_store, result["title"], len(chunks), content_preview, elapsed_time


def typewriter_effect(text: str, speed: float = 0.02):
    """
    Display text with a typewriter effect.
    
    Args:
        text: Text to display
        speed: Speed of typing in seconds per character
        
    Returns:
        Streamlit placeholder with animated text
    """
    placeholder = st.empty()
    displayed_text = ""
    
    for char in text:
        displayed_text += char
        placeholder.markdown(displayed_text + "▌")
        time.sleep(speed)
    
    # Final display without cursor
    placeholder.markdown(displayed_text)
    return placeholder


def get_chatbot_response(query: str, index, url: str, title: str) -> str:
    """
    Get a response from the chatbot using RAG.
    
    Args:
        query: User's question
        index: Vector store index
        url: Indexed website URL
        title: Website title
        
    Returns:
        str: Chatbot response
    """
    try:
        response = answer_question(query, index, url, title)
        return response
    except Exception as e:
        return f"❌ Error generating response: {str(e)}"


def clear_chat_history():
    """Clear the chat history and memory"""
    st.session_state.messages = []
    memory.clear()
    st.success("✅ Chat history cleared!")


# ============================================================================
# SIDEBAR: CONFIGURATION & CONTROLS
# ============================================================================
with st.sidebar:
    st.markdown("### 🎯 Website Indexer")
    st.markdown("---")
    
    # URL Input
    url_input = st.text_input(
        "🔗 Enter Website URL",
        placeholder="https://example.com",
        help="Enter the URL of the website you want to chat with"
    )
    
    # Index Button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Index Website", use_container_width=True):
            if url_input:
                with st.spinner("🔄 Scraping and indexing..."):
                    result = index_website(url_input)
                    
                    if result[0] is not None:
                        st.session_state.index = result[0]
                        st.session_state.title = result[1]
                        st.session_state.total_chunks = result[2]
                        st.session_state.content_preview = result[3]
                        st.session_state.indexing_time = result[4]
                        st.session_state.indexed_url = url_input
                        
                        st.success(f"✅ Successfully indexed: **{result[1]}**")
                        st.balloons()
            else:
                st.error("⚠️ Please enter a valid URL")
    
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            clear_chat_history()
    
    st.markdown("---")
    
    # Display indexed website info
    if st.session_state.index is not None:
        st.markdown("### 📊 Indexed Website Info")
        
        st.metric("📄 Website Title", st.session_state.title or "N/A")
        st.metric("🔗 URL", st.session_state.indexed_url or "N/A")
        st.metric("📦 Total Chunks", st.session_state.total_chunks)
        
        if st.session_state.indexing_time:
            st.metric("⏱️ Indexing Time", f"{st.session_state.indexing_time:.2f}s")
        
        # Content preview in expander
        with st.expander("👁️ Content Preview"):
            st.text_area(
                "First 500 characters",
                st.session_state.content_preview,
                height=200,
                disabled=True
            )
    else:
        st.info("ℹ️ No website indexed yet. Enter a URL above to get started!")
    
    st.markdown("---")
    
    # Settings
    with st.expander("⚙️ Advanced Settings"):
        st.markdown("**Chunk Settings**")
        chunk_size = st.slider("Chunk Size (words)", 100, 1000, 500)
        chunk_overlap = st.slider("Chunk Overlap (words)", 0, 200, 100)
        
        st.markdown("**Retrieval Settings**")
        top_k = st.slider("Top K Results", 1, 10, 3)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #888; font-size: 12px;'>
            <p>🌐 Website Knowledge Assistant</p>
            <p>Powered by AI & Vector Search</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================================
# MAIN CHAT INTERFACE
# ============================================================================
st.title("🌐 Website Knowledge Assistant")
st.markdown("### Chat with any website using AI-powered search")

# Display status banner
if st.session_state.index is None:
    st.info("👈 **Get Started:** Enter a website URL in the sidebar and click 'Index Website'")
else:
    st.success(f"✅ **Ready to chat about:** {st.session_state.title}")

st.markdown("---")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Add timestamp for each message
        if "timestamp" in message:
            st.caption(f"🕒 {message['timestamp']}")

# Chat input
if prompt := st.chat_input("💬 Ask a question about the website..."):
    if not st.session_state.index:
        st.warning("⚠️ Please index a website in the sidebar first.")
    else:
        # Get current timestamp
        timestamp = datetime.now().strftime("%I:%M %p")
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"🕒 {timestamp}")
        
        # Add to history
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                response = get_chatbot_response(
                    prompt,
                    st.session_state.index,
                    st.session_state.indexed_url,
                    st.session_state.title
                )
            
            # Display response with typewriter effect
            typewriter_effect(response, speed=0.01)
            response_timestamp = datetime.now().strftime("%I:%M %p")
            st.caption(f"🕒 {response_timestamp}")
        
        # Add assistant response to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": response_timestamp
        })

# ============================================================================
# FOOTER STATISTICS
# ============================================================================
if st.session_state.messages:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💬 Total Messages", len(st.session_state.messages))
    
    with col2:
        user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.metric("👤 User Questions", user_messages)
    
    with col3:
        assistant_messages = len([m for m in st.session_state.messages if m["role"] == "assistant"])
        st.metric("🤖 AI Responses", assistant_messages)