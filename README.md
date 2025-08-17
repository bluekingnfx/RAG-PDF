# PDF Query Application

A Streamlit-based application that allows users to upload PDF documents and ask questions about their content using RAG (Retrieval-Augmented Generation) with LangChain and Ollama.

## Features

- **PDF Upload**: Upload PDF documents through a user-friendly interface
- **Document Processing**: Automatically processes and chunks PDF content for optimal retrieval
- **Question Answering**: Ask natural language questions about uploaded documents
- **Chat History**: Maintains conversation history with context sources
- **Vector Storage**: Uses ChromaDB for efficient document embedding storage
- **Local LLM**: Powered by Ollama's Gemma3:1b model for privacy and offline capability

## Prerequisites

- Python 3.8+
- Ollama installed with Gemma3:1b model
- Required Python packages (see requirements below)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/bluekingnfx/RAG-PDF.git
cd askPdf
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install and set up Ollama:

```bash
# Install Ollama from https://ollama.ai
ollama pull gemma3:1b
```

4. Create a `.env` file in the project root:

```env
HF_TOKEN=
LANGCHAIN_API_KEY=
LANGCHAIN_TRACING_V2=
LANGCHAIN_PROJECT=

CHROMA_COLLECTION_NAME=resource
```

## Environment Variables

Create a `.env` file with the following required variables:

| Variable                  | Description                                                   | Example          |
|---------------------------|---------------------------------------------------------------|------------------|
| `HF_TOKEN`                | HuggingFace API token for embedding model access   | `hf_xxx`         |
| `LANGCHAIN_API_KEY`       | API key for LangChain (optional, for advanced features)       | `lc_xxx`         |
| `LANGCHAIN_TRACING_V2`    | Enable LangChain tracing (optional)                           | `true`           |
| `LANGCHAIN_PROJECT`       | Name of the LangChain project (optional)                      | `my_project`     |
| `CHROMA_COLLECTION_NAME`  | Name for the ChromaDB collection to store document embeddings | `pdf_documents`  |

> **Note**: LangChain keys (`LANGCHAIN_API_KEY` and `LANGCHAIN_TRACING_V2`) are optional and only required if you want to enable project tracing or advanced LangChain features.

## Usage

1. Start the application:

```bash
streamlit run index.py
```

2. Open your browser and navigate to the displayed URL (typically `http://localhost:8501`)

3. Upload a PDF document using the file uploader

4. Once processed, ask questions about the document content

5. View chat history and context sources for each answer

## How It Works

### Document Processing (`main_func.py:UploadClass`)

1. **File Upload**: Saves uploaded PDF to temporary folder
2. **Document Loading**: Uses PyPDFLoader to extract text content
3. **Text Splitting**: Splits document into chunks (1000 chars, 100 overlap)
4. **Vectorization**: Creates embeddings using HuggingFace's all-MiniLM-L6-v2 model
5. **Storage**: Stores embeddings in ChromaDB for retrieval

### Question Processing (`main_func.py:ProcessTheQuestion`)

1. **Query Processing**: Takes user question as input
2. **Retrieval**: Searches similar document chunks using vector similarity
3. **Generation**: Uses Ollama's Gemma3:1b model to generate contextual answers
4. **Response**: Returns answer with source document references

### Interface (`index.py`)

- **Session Management**: Maintains upload status and chat history
- **File Upload Interface**: Streamlit file uploader for PDFs
- **Chat Interface**: Text area for questions with submit functionality
- **History Display**: Expandable chat history with context sources
- **Controls**: Sidebar with options to clear history, upload new documents

## File Structure

askPdf/

```txt

├── index.py          # Main Streamlit application interface
├── main_func.py      # Core functionality classes
├── .env              # Environment variables
├── requirements.txt  # Python dependencies
├── temp/             # Temporary folder for PDF processing
└── data/db/          # ChromaDB vector store directory

```

## Controls

- **🗑️ Clear Chat History**: Remove all previous conversations
- **📄 Upload New Document**: Upload a new PDF (previous embeddings preserved)
- **📗 Already Uploaded**: Skip upload if document is already processed

## Technical Details

- **Embedding Model**: HuggingFace all-MiniLM-L6-v2
- **LLM**: Ollama Gemma3:1b (local inference)
- **Vector Database**: ChromaDB with persistent storage
- **Text Splitter**: RecursiveCharacterTextSplitter (1000 chunk size, 100 overlap)
- **Framework**: Streamlit for web interface, LangChain for RAG pipeline

## Troubleshooting

- Ensure Ollama is running and Gemma3:1b model is available
- Check that all required packages are installed
- Verify `.env` file exists with correct variables
- Make sure the `data/db` directory has write permissions
