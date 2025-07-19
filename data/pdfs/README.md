# PDF Directory for RAG Database

This directory contains PDF files that will be processed to create the RAG (Retrieval-Augmented Generation) vector database.

## How to use:

1. **Add your PDF files** to this directory (`data/pdfs/`)
2. **Run the RAG creation pipeline**:
   ```bash
   python run_create_rag.py
   ```

## Optional parameters:

- `--pdf-dir`: Specify a different PDF directory
- `--clear-existing`: Clear existing documents before processing

## Examples:

```bash
# Use default directory (data/pdfs)
python run_create_rag.py

# Use custom directory
python run_create_rag.py --pdf-dir /path/to/your/pdfs

# Clear existing documents and reprocess
python run_create_rag.py --clear-existing
```

## What happens:

1. PDF files are processed and text is extracted
2. Text is split into chunks (configurable in `configs/rag.yaml`)
3. Chunks are embedded using OpenAI embeddings
4. Vectors are stored in ChromaDB at `data/vector_db/`

## Configuration:

Edit `configs/rag.yaml` to customize:
- Chunk size and overlap
- Embedding model
- Vector database settings 