from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from ai.ingest import ingest_excel_file
from ai.rag import answer_question

router = APIRouter(prefix='/api/ai', tags=['AI'])

class IngestRequest(BaseModel):
    session_id: str = Field(..., description="Session ID to associate the file with")
    filename: Optional[str] = Field(None, description="Original filename (optional)")

class IngestResponse(BaseModel):
    file_id: str
    filename: str
    sheets_processed: int
    chunks_created: int
    message: str

class QueryRequest(BaseModel):
    session_id: str = Field(..., description="Session ID for the conversation")
    question: str = Field(..., description="User's natural language question")
    top_k: Optional[int] = Field(5, description="Number of chunks to retrieve")

class SourceCitation(BaseModel):
    file_id: str
    filename: str
    sheet_name: str
    row_start: int
    row_end: int
    chunk_text: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    session_id: str
    question: str

@router.post("/ingest", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    request: IngestRequest = Depends()
):
    """
    Ingest an Excel file for a given session.
    """
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported")
    
    try:
        # Read file content
        contents = await file.read()
        
        # Call ingestion pipeline
        result = ingest_excel_file(
            file_content=contents,
            session_id=request.session_id,
            original_filename=request.filename or file.filename
        )
        
        return IngestResponse(
            file_id=result["file_id"],
            filename=result["filename"],
            sheets_processed=result["sheets_processed"],
            chunks_created=result["chunks_created"],
            message="File ingested successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Process a natural language question using RAG.
    """
    try:
        # Call RAG pipeline
        result = answer_question(
            session_id=request.session_id,
            question=request.question,
            top_k=request.top_k
        )
        
        # Convert sources to Pydantic models
        sources = []
        for source in result["sources"]:
            sources.append(SourceCitation(
                file_id=source["file_id"],
                filename=source["filename"],
                sheet_name=source["sheet_name"],
                row_start=source["row_start"],
                row_end=source["row_end"],
                chunk_text=source["chunk_text"]
            ))
        
        return QueryResponse(
            answer=result["answer"],
            sources=sources,
            session_id=request.session_id,
            question=request.question
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")