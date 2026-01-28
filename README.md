# Website Knowledge Assistant 🌐

A powerful RAG (Retrieval-Augmented Generation) application that turns any website into a conversational AI assistant. Chat with web pages, ask questions, and get accurate answers based on the site's content.

## 🚀 Features

- **Instant Indexing**: Scrape and process any website URL in seconds.
- **Smart Retrieval**: Uses advanced vector embeddings (`intfloat/e5-large-v2`) and FAISS for semantic search.
- **AI-Powered Answers**: Leverages Google's Gemini models for high-quality, context-aware responses.
- **Conversational Memory**: Remembers your chat history for natural follow-up questions.
- **Premium UI**: specific beautifully designed interface using Streamlit with custom CSS.
- **Configurable**: Adjust chunk sizes, overlap, and retrieval parameters to fine-tune performance.

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **LLM**: Google Gemini via [LangChain](https://www.langchain.com/)
- **Embeddings**: [SentenceTransformers](https://www.sbert.net/)
- **Vector Store**: [FAISS](https://github.com/facebookresearch/faiss)
- **Scraping**: `requests`, `beautifulsoup4`, `readability-lxml`

## 📋 Prerequisites

- Python 3.12 or higher
- A Google Cloud API Key with access to Gemini API

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd web-scrap-bot
   ```

2. **Set up a virtual environment (Optional but recommended)**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   
   Using pip:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or if you use `uv`:
   ```bash
   uv sync
   ```

## 🔑 Configuration

1. Create a `.env` file in the project root:
   ```bash
   type nul > .env  # Windows
   # or
   touch .env       # macOS/Linux
   ```

2. Add your Google API Key to the `.env` file:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```

   Alternatively, you can set it via Streamlit secrets (`.streamlit/secrets.toml`).

## 🏃‍♂️ Usage

Run the Streamlit application:

```bash
streamlit run main.py
```

Or if you are using `uv`:

```bash
uv run streamlit run main.py
```

1. Enter a website URL in the sidebar (e.g., `https://example.com`).
2. Click **Index Website**.
3. Once indexed, start chatting with the content in the main chat window!

## 📂 Project Structure

- `main.py`: The main entry point and Streamlit UI application.
- `ai_handler.py`: Handles interactions with the Google Gemini LLM and chat memory.
- `webscrap.py`: Logic for scraping and cleaning text from websites.
- `text_processing.py`: Chunking logic to split text into manageable pieces.
- `embedding.py`: Manages vector embeddings and FAISS index.
- `utils.py` (if applicable): Helper functions.


