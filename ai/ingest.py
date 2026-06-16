import os
import pandas as pd
from typing import List, Dict, Any, Tuple
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import vector store and embeddings
from .vector_store import VectorStore
from .embeddings import get_embedding

# Chunking implementation
def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Recursive chunking strategy for text.
    Splits text into chunks of approximately chunk_size characters with overlap.
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Calculate end position
        end = start + chunk_size
        
        # If we're at the end of the text
        if end >= len(text):
            chunks.append(text[start:])
            break
        
        # Try to find a good break point (space, newline, or punctuation)
        break_chars = ['\n\n', '\n', '. ', '? ', '! ', '; ', ', ', ' ']
        found_break = False
        
        for break_char in break_chars:
            break_pos = text.rfind(break_char, start, end)
            if break_pos != -1 and break_pos > start + chunk_size // 2:
                end = break_pos + len(break_char)
                found_break = True
                break
        
        # If no good break found, just cut at chunk_size
        if not found_break:
            # Look for any whitespace
            for i in range(end, start, -1):
                if i < len(text) and text[i].isspace():
                    end = i + 1
                    found_break = True
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position for next chunk with overlap
        start = end - chunk_overlap
        if start < 0:
            start = 0
    
    return chunks

def process_excel_sheet(df: pd.DataFrame, sheet_name: str) -> List[Dict[str, Any]]:
    """
    Process a single Excel sheet into text chunks with metadata.
    """
    chunks = []
    
    # Convert dataframe to text representation
    text_parts = []
    
    # Add sheet name
    text_parts.append(f"Sheet: {sheet_name}")
    
    # Add column names
    columns = list(df.columns)
    text_parts.append(f"Columns: {', '.join(columns)}")
    
    # Add sample data (first few rows)
    sample_rows = min(50, len(df))
    for idx, row in df.head(sample_rows).iterrows():
        row_text = f"Row {idx + 1}: "
        row_values = []
        for col in columns:
            value = row[col]
            if pd.isna(value):
                value = ""
            row_values.append(f"{col}={value}")
        row_text += "; ".join(row_values)
        text_parts.append(row_text)
    
    # If there are more rows, add summary
    if len(df) > sample_rows:
        text_parts.append(f"... and {len(df) - sample_rows} more rows")
    
    # Add summary statistics for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        text_parts.append("\nSummary statistics:")
        for col in numeric_cols:
            stats = df[col].describe()
            text_parts.append(f"{col}: count={stats.get('count', 0):.0f}, mean={stats.get('mean', 0):.2f}, "
                            f"std={stats.get('std', 0):.2f}, min={stats.get('min', 0):.2f}, "
                            f"max={stats.get('max', 0):.2f}")
    
    full_text = "\n".join(text_parts)
    
    # Chunk the text
    text_chunks = chunk_text(full_text, chunk_size=1000, chunk_overlap=200)
    
    # Create chunk objects with metadata
    for i, chunk_text_content in enumerate(text_chunks):
        chunk_data = {
            'text': chunk_text_content,
            'chunk_index': i,
            'total_chunks': len(text_chunks),
            'sheet_name': sheet_name,
            'columns': columns,
            'total_rows': len(df),
            'sample_rows_included': sample_rows
        }
        chunks.append(chunk_data)
    
    return chunks

def ingest_excel(file_path: str, session_id: str, user_id: str) -> Dict[str, Any]:
    """
    Main ingestion function for Excel files.
    Reads Excel file, processes each sheet, chunks content, generates embeddings,
    and stores in vector database.
    """
    try:
        # Read Excel file
        logger.info(f"Ingesting Excel file: {file_path}")
        
        # Get file metadata
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Read all sheets from Excel
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        
        all_chunks = []
        total_rows = 0
        
        # Process each sheet
        for sheet_name in sheet_names:
            try:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                total_rows += len(df)
                
                # Process sheet into chunks
                sheet_chunks = process_excel_sheet(df, sheet_name)
                all_chunks.extend(sheet_chunks)
                
                logger.info(f"Processed sheet '{sheet_name}': {len(df)} rows, {len(sheet_chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error processing sheet '{sheet_name}': {str(e)}")
                continue
        
        if not all_chunks:
            raise ValueError("No valid data found in Excel file")
        
        # Generate embeddings for each chunk
        logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")
        
        chunk_records = []
        for chunk_data in all_chunks:
            try:
                # Generate embedding
                embedding = get_embedding(chunk_data['text'])
                
                # Create chunk record for database
                chunk_id = str(uuid.uuid4())
                
                record = {
                    'id': chunk_id,
                    'text': chunk_data['text'],
                    'embedding': embedding,
                    'metadata': {
                        'file_name': file_name,
                        'file_size': file_size,
                        'session_id': session_id,
                        'user_id': user_id,
                        'chunk_index': chunk_data['chunk_index'],
                        'total_chunks': chunk_data['total_chunks'],
                        'sheet_name': chunk_data['sheet_name'],
                        'columns': chunk_data['columns'],
                        'total_rows': chunk_data['total_rows'],
                        'sample_rows_included': chunk_data['sample_rows_included'],
                        'ingestion_timestamp': datetime.utcnow().isoformat()
                    }
                }
                
                chunk_records.append(record)
                
            except Exception as e:
                logger.error(f"Error generating embedding for chunk: {str(e)}")
                continue
        
        # Store in vector database
        logger.info(f"Storing {len(chunk_records)} chunks in vector database...")
        
        vector_store = VectorStore()
        inserted_count = vector_store.upsert_chunks(chunk_records)
        
        # Create file metadata record
        file_metadata = {
            'file_id': str(uuid.uuid4()),
            'file_name': file_name,
            'file_path': file_path,
            'file_size': file_size,
            'user_id': user_id,
            'session_id': session_id,
            'total_sheets': len(sheet_names),
            'total_rows': total_rows,
            'total_chunks': len(chunk_records),
            'ingestion_timestamp': datetime.utcnow().isoformat()
        }
        
        # Store file metadata
        vector_store.store_file_metadata(file_metadata)
        
        logger.info(f"Successfully ingested {inserted_count} chunks from {file_name}")
        
        return {
            'success': True,
            'file_name': file_name,
            'total_sheets': len(sheet_names),
            'total_rows': total_rows,
            'total_chunks': len(chunk_records),
            'inserted_chunks': inserted_count,
            'file_metadata': file_metadata
        }
        
    except Exception as e:
        logger.error(f"Error ingesting Excel file: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'file_name': os.path.basename(file_path) if 'file_path' in locals() else 'unknown'
        }