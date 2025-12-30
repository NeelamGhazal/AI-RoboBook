# rag-chatbot-setup

Setup Retrieval-Augmented Generation chatbot with OpenAI and vector database.

## Purpose
Create and integrate a RAG chatbot that answers questions about book content using OpenAI Agents/ChatKit SDK, Neon Postgres, and Qdrant Cloud.

## Tasks
1. Configure OpenAI Agents/ChatKit SDK
2. Setup Neon Serverless Postgres for chat history
3. Configure Qdrant Cloud for vector embeddings
4. Create document embedding pipeline
5. Build retrieval mechanism
6. Integrate chatbot UI in Docusaurus
7. Handle user text selection queries

## Components

### OpenAI Integration
- Setup OpenAI API client
- Configure ChatKit SDK or Agents API
- Create chat completion endpoints
- Handle streaming responses
- Implement context management

### Vector Database (Qdrant)
- Create collection for embeddings
- Store document chunks with metadata
- Configure similarity search
- Optimize retrieval parameters
- Handle document updates

### Database (Neon Postgres)
- Store chat history
- User session management
- Query logs and analytics
- Conversation context storage

### Frontend Integration
- Embed chatbot widget in Docusaurus
- Handle text selection events
- Display chat interface
- Stream AI responses
- Mobile-responsive design

## Environment Variables
- OPENAI_API_KEY
- NEON_DATABASE_URL
- QDRANT_API_KEY
- QDRANT_URL
- QDRANT_COLLECTION_NAME

## Chatbot Features
- Answer questions about book content
- Support text selection queries (user selects text, asks question about it)
- Maintain conversation history
- Cite sources from the book
- Handle follow-up questions

## Output
Fully functional RAG chatbot embedded in Docusaurus book