import os
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import vector store and embeddings
from .vector_store import VectorStore
from .embeddings import get_embedding

def retrieve_context(query: str, top_k: int = 5, session_id: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve relevant context for a query using vector similarity search.
    """
    try:
        # Generate embedding for the query
        query_embedding = get_embedding(query)
        
        # Search vector store
        vector_store = VectorStore()
        results = vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            session_id=session_id,
            user_id=user_id
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error retrieving context: {str(e)}")
        return []

def build_prompt(query: str, context_chunks: List[Dict[str, Any]]) -> str:
    """
    Build a prompt for the LLM with retrieved context.
    """
    if not context_chunks:
        return f"Question: {query}\n\nAnswer based on your general knowledge:"
    
    # Format context with citations
    context_parts = []
    for i, chunk in enumerate(context_chunks):
        metadata = chunk.get('metadata', {})
        file_name = metadata.get('file_name', 'Unknown file')
        sheet_name = metadata.get('sheet_name', 'Unknown sheet')
        chunk_index = metadata.get('chunk_index', 0)
        total_chunks = metadata.get('total_chunks', 1)
        
        citation = f"[Source {i+1}: {file_name}, Sheet: {sheet_name}, Chunk {chunk_index+1}/{total_chunks}]"
        context_parts.append(f"{citation}\n{chunk['text']}\n")
    
    context_text = "\n".join(context_parts)
    
    prompt = f"""You are a helpful data analyst assistant. Answer the user's question based ONLY on the provided context from Excel files. If the answer cannot be found in the context, say "I cannot find this information in the uploaded data."

Context from Excel files:
{context_text}

Question: {query}

Instructions:
1. Answer the question concisely and accurately using ONLY the context provided.
2. Cite your sources using the format [Source X] where X matches the source number above.
3. If the question requires calculations or comparisons, perform them based on the data in the context.
4. If multiple sources contain relevant information, synthesize them.
5. If the context doesn't contain enough information to answer, say "I cannot find this information in the uploaded data."

Answer:"""
    
    return prompt

def answer_question(query: str, session_id: str, user_id: str) -> Dict[str, Any]:
    """
    Main function to answer a question using RAG pipeline.
    """
    try:
        # Read Gemini API key lazily
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        # Retrieve relevant context
        logger.info(f"Retrieving context for query: {query[:50]}...")
        context_chunks = retrieve_context(query, top_k=5, session_id=session_id, user_id=user_id)
        
        if not context_chunks:
            logger.warning("No context retrieved for query")
            return {
                'answer': "I cannot find relevant information in the uploaded data to answer this question.",
                'sources': [],
                'query': query,
                'timestamp': datetime.utcnow().isoformat(),
                'success': True
            }
        
        # Build prompt
        prompt = build_prompt(query, context_chunks)
        
        # Initialize Gemini
        genai.configure(api_key=gemini_api_key)
        
        # Use gemini-2.0-flash model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Generate response
        logger.info("Generating answer with Gemini...")
        response = model.generate_content(prompt)
        
        # Extract answer text
        answer_text = response.text.strip() if response.text else "No response generated."
        
        # Prepare sources with metadata
        sources = []
        for chunk in context_chunks:
            metadata = chunk.get('metadata', {})
            source_info = {
                'file_name': metadata.get('file_name', 'Unknown'),
                'sheet_name': metadata.get('sheet_name', 'Unknown'),
                'chunk_index': metadata.get('chunk_index', 0),
                'total_chunks': metadata.get('total_chunks', 1),
                'columns': metadata.get('columns', []),
                'total_rows': metadata.get('total_rows', 0),
                'similarity_score': chunk.get('similarity_score', 0.0),
                'text_preview': chunk.get('text', '')[:200] + '...' if len(chunk.get('text', '')) > 200 else chunk.get('text', '')
            }
            sources.append(source_info)
        
        logger.info(f"Successfully generated answer for query")
        
        return {
            'answer': answer_text,
            'sources': sources,
            'query': query,
            'context_chunks_count': len(context_chunks),
            'timestamp': datetime.utcnow().isoformat(),
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        return {
            'answer': f"Error generating answer: {str(e)}",
            'sources': [],
            'query': query,
            'timestamp': datetime.utcnow().isoformat(),
            'success': False,
            'error': str(e)
        }