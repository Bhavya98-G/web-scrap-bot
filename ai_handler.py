import os
from dotenv import load_dotenv, find_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# 1. Load variables before initializing the LLM
try:
    api_key = st.secrets['GOOGLE_API_KEY']
except:
    load_dotenv(find_dotenv())
    api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY not found. Please ensure it is set in your .env file.")

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0,
    google_api_key=api_key
)

# 2. Simple Memory Implementation
class SimpleMemory:
    """Simple conversation memory that stores chat history as a string."""
    def __init__(self):
        self.history = []
    
    def load_memory_variables(self, inputs=None):
        """Return the chat history as a formatted string."""
        if not self.history:
            return {"chat_history": ""}
        
        formatted_history = []
        for entry in self.history:
            formatted_history.append(f"Human: {entry['input']}")
            formatted_history.append(f"Assistant: {entry['output']}")
        
        return {"chat_history": "\n".join(formatted_history)}
    
    def save_context(self, inputs, outputs):
        """Save the current interaction to history."""
        self.history.append({
            "input": inputs.get("input", ""),
            "output": outputs.get("output", "")
        })
    
    def clear(self):
        """Clear the conversation history."""
        self.history = []

memory = SimpleMemory()

prompt = PromptTemplate(
    input_variables=["chat_history", "context", "question", "metadata"],
    template="""
You are a helpful website assistant. Your primary role is to answer questions about the website content provided below.

However, you should also be able to:
1. Answer questions about our conversation history (e.g., "what was my previous question?")
2. Have natural conversations with the user
3. Provide helpful responses even for general questions

Chat History:
{chat_history}

Website Content:
{context}

Source: {metadata}

Instructions:
- If the question is about the website content, use the Content section above to answer
- If the question is about our conversation (e.g., previous questions), use the Chat History
- If the question is general or conversational, answer naturally and helpfully
- If you cannot find relevant information in either the content or chat history, say: "I don't have enough information to answer that question."

Question: {question}

Answer:
"""
)

def answer_question(question, retriever, url, title):
    docs = retriever.query(question)
    if not docs:
        return "The answer is not available on the provided website."

    context = "\n\n".join(doc['chunk_text'] for doc in docs)
    
    # Load history as a string
    history = memory.load_memory_variables({})["chat_history"]
    print(history)

    response = llm.invoke(
        prompt.format(
            context=context,
            question=question,
            metadata=f"URL: {url}, Title: {title}",
            chat_history=history
        )
    )
    
    # Extract text content from response
    # Handle both string and structured response formats
    if isinstance(response.content, str):
        answer = response.content
    elif isinstance(response.content, list):
        # Extract text from structured response
        answer = ""
        for item in response.content:
            if isinstance(item, dict) and 'text' in item:
                answer += item['text']
            elif hasattr(item, 'text'):
                answer += item.text
    else:
        answer = str(response.content)

    memory.save_context({"input": question}, {"output": answer})
    return answer