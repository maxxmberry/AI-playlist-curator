# Agentic AI Playlist Curator Project — Maxx Berry

---

## 1. Project Overview

**Project idea:** *(Describe your project in 2–3 sentences. What problem does your agent solve?)*  
My project is to create an AI agent who can assist anyone is finding new music, as well as curate new playlists for them based on their preferences. Users can tell the agent what kind of music they like to listen to by listing preferences like favorite songs, artists, genres, etc. From there, the user can also ask the agent to curate a playlist for them based on the music they were talking about. One feature I hope to add is a connection to Spotify so users can have the agent create the playlist directly in Spotify for them.

**Target domain:** *(What kind of data/knowledge does your agent need?)*  
The agent will require a very large corpus of ideally all music that has ever been published in the world and will store the music data and metadata. I am using MusicBrainz and Setlist FM as my sources of data.

**Target users:** *(Who would use this? What would they ask it?)*  
The target market for my music AI agent is anyone who wants help finding music to listen to and creating playlists. From a casual music listener to some of the biggest "audiophiles", this app is made for anyone who likes music and wants to find more of what they like and have a playlist made for them to listen to. 

---

## 2. LLM Provider Selection

Choose your provider(s) and document why. You may use one provider for everything or mix providers for different components.

### Available Options

| Provider | Generation | Embeddings | Vision | Free Tier Notes |
|----------|-----------|------------|--------|----------------|
| Google Gemini (AI Studio) | ✅ gemini-2.0-flash | ✅ text-embedding-004 | ✅ native | ~15 RPM, 1M TPD |
| Groq | ✅ Llama 3, Mistral, Gemma | ❌ | ❌ | Fast inference, rate limited |
| OpenRouter | ✅ many models | varies | varies | Free tier on some models, pay-per-token on others |
| AWS Bedrock | ✅ Claude, Llama, etc. | ✅ Titan Embeddings | varies | Requires AWS account, free tier limited |
| Ollama (local) | ✅ any open model | ✅ nomic-embed-text | ✅ LLaVA | Requires local GPU or Colab |
| HuggingFace (local embeddings) | ❌ | ✅ sentence-transformers | ❌ | Runs on CPU in Codespaces |

**Our choice:**

- **Generation:** *(provider + model)*
- **Embeddings:** *(provider + model)*
- **Vision (if needed):** *(provider + model)*
- **Why:** *(cost, speed, quality, multimodal needs, etc.)*

### LangChain Integration

```python
# Generation — pick one:
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

# Embeddings — pick one:
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
```

---

## 3. Corpus & Data Plan

**What data will your agent use?**

| Source | Format | Approx Size | Notes |
|--------|--------|-------------|-------|
| *(e.g., product docs)* | *(PDF, CSV, etc.)* | *(# docs)* | |
| | | | |
| | | | |

**Chunking strategy:**
- Chunk size: *(and why)*
- Chunk overlap: *(and why)*
- Splitter: *(RecursiveCharacterTextSplitter, or other)*

**Image data (if applicable):**
- Description approach: *(Gemini vision, LLaVA, BLIP, CLIP)*
- How images link back to retrievable content: *(metadata, file paths)*

---

## 4. Architecture Overview

*(Draw or describe your pipeline. Update this as you build.)*

### Basic Text RAG Pipeline
```
Documents → Loaders → Chunking → Embeddings → Vector Store
                                                    ↓
User Query → Embed Query → Retrieve Top-K → Prompt + Context → LLM → Response
```

### With Agent Layer
```
User Query → Agent decides which tool to use:
    → Tool 1: RAG retriever (domain knowledge)
    → Tool 2: __________ (your second tool)
    → Tool 3: __________ (stretch goal)
    → Direct LLM response (no tool needed)
```

### Multimodal Extension (if applicable)
```
Images → Vision model / CLIP → Descriptions or embeddings → Vector Store
    ↓
Agent can retrieve text AND image-based results
```

---

## 5. Repo Structure

Choose the structure that fits your project's current complexity. Start simple, refactor if needed.

### Simple Structure (Good Starting Point)

```
project-name/
├── README.md                  # Setup instructions, architecture overview
├── requirements.txt
├── .env.example               # Template for API keys
├── .gitignore                 # Include .env, __pycache__, chroma_db/
├── data/
│   └── raw/                   # Your corpus files
├── src/
│   ├── config.py              # Provider setup, model selection
│   ├── ingest.py              # Loading, chunking, indexing
│   ├── retrieval.py           # Vector store, retriever
│   ├── agent.py               # Agent, tools, executor
│   └── utils.py               # Helpers
├── notebooks/
│   └── demo.ipynb             # Demonstrations and comparisons
└── docs/
    └── architecture.md
```

### Production-Style Structure (For Larger Projects or Later Refactor)

```
project-name/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── config/
│   └── settings.yaml          # Model params, retrieval settings, chunking config
├── data/
│   ├── raw/
│   └── processed/
├── prompts/
│   ├── system.txt             # System prompt for agent
│   ├── rag_template.txt       # RAG prompt template
│   └── router_template.txt    # Router/classification prompt
├── src/
│   ├── ingest/
│   │   ├── loaders.py         # Document loading logic
│   │   └── chunking.py        # Chunking strategies
│   ├── retrieval/
│   │   ├── vectorstore.py     # ChromaDB setup and management
│   │   └── retriever.py       # Retriever configuration
│   ├── tools/
│   │   ├── rag_tool.py        # RAG retriever as agent tool
│   │   ├── calculator.py      # Example second tool
│   │   └── ...                # Additional tools
│   ├── agent/
│   │   ├── agent.py           # Agent construction
│   │   └── executor.py        # Execution and orchestration
│   └── llm/
│       └── providers.py       # Factory for Gemini/Groq/etc.
├── notebooks/
│   └── demo.ipynb
└── docs/
    └── architecture.md
```

---

## 6. Track Selection

Choose the track that fits your project. You can start with Track A and upgrade later.

### Track A: Text-Only RAG (Foundational)
- Text corpus, text embeddings, text retrieval
- Works with any provider
- Focus: chunking, retrieval quality, agent tool selection

### Track B: Image RAG via Description (Intermediate)
- Images captioned by a vision model → stored as text → retrieved as text
- Gemini: native vision makes this straightforward
- Groq: pair with Gemini or HuggingFace BLIP for the vision step
- Focus: bridging modalities, preprocessing pipelines, metadata linking

### Track C: CLIP-Based Multimodal Retrieval (Advanced)
- CLIP embeds images and text into shared vector space
- True cross-modal search: text query → image results
- Requires `open-clip-torch`, separate from LLM provider
- Focus: embedding spaces, cross-modal retrieval, combining non-LangChain components

---

## 7. Development Milestones

*(Adjust timeline to match your course schedule)*

### Milestone 1: Infrastructure Setup
- [ ] GitHub repo created with chosen structure
- [ ] Codespace configured with Python, dependencies
- [ ] API keys stored as Codespace secrets
- [ ] LLM provider connected — can make a basic call through LangChain
- [ ] Vector store initialized — can add and query test embeddings

### Milestone 2: RAG Pipeline
- [ ] Corpus loaded and chunked
- [ ] Embeddings generated and stored in ChromaDB
- [ ] Retrieval chain works — queries return relevant chunks
- [ ] Side-by-side comparison: RAG vs. base LLM for 3+ queries

### Milestone 3: Agent Layer
- [ ] Retriever wrapped as LangChain tool
- [ ] At least one additional tool implemented
- [ ] Agent demonstrates tool selection with verbose trace
- [ ] Queries show agent choosing correct tool for different question types

### Milestone 4: Extensions (Stretch Goals)
- [ ] Additional tools (web search, code execution, APIs, etc.)
- [ ] Multimodal retrieval (Track B or C)
- [ ] Evaluation metrics for retrieval quality
- [ ] Production interface (Streamlit, Gradio)
- [ ] Multi-agent orchestration (LangGraph, CrewAI)
- [ ] Migration to Databricks or cloud infrastructure

---

## 8. Technical Reference

### Package Installation
```
# Base
langchain
langchain-chroma
langchain-community

# Providers (pick what you need)
langchain-google-genai
langchain-groq
langchain-huggingface

# Advanced tracks
open-clip-torch
```

### API Key Management
```python
# Store as Codespace secrets (Settings → Secrets → Codespaces)
# Access in code:
import os
key = os.environ["GOOGLE_API_KEY"]

# NEVER commit keys to the repo
# .env files go in .gitignore
```

### ChromaDB Persistence
```python
# Save to disk (persists in Codespaces between sessions)
vectorstore = Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")

# Reload
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

# Add chroma_db/ to .gitignore — don't commit vector stores
```

---

## 9. Future Directions

As your project matures, consider:

- **Databricks** — persistent Vector Search, MLflow experiment tracking, Unity Catalog for data governance
- **AWS Bedrock** — managed model hosting, enterprise-scale deployment
- **LangGraph** — stateful multi-agent orchestration with cycles and conditional logic
- **CrewAI** — role-based multi-agent coordination
- **LangSmith** — tracing, evaluation, and debugging for LangChain pipelines
- **Provider comparison** — same pipeline, different backends, measure quality/speed/cost
