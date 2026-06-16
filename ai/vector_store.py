import os
import json
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import Json
from psycopg2.extensions import connection, cursor

class VectorStore:
    """PgVector store for embeddings and metadata."""
    def __init__(self):
        # Lazy initialization: connection created inside methods
        self._conn = None
        self.dimension = 1536  # Must match embedding model

    def _get_connection(self) -> connection:
        """Establish PostgreSQL connection if not already connected."""
        if self._conn is None or self._conn.closed:
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                raise ValueError("DATABASE_URL environment variable not set")
            self._conn = psycopg2.connect(db_url)
            # Ensure pgvector extension and required tables exist
            self._initialize_schema()
        return self._conn

    def _initialize_schema(self):
        """Create pgvector extension and required tables if they don't exist."""
        with self._conn.cursor() as cur:
            # Enable pgvector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create chunks table with vector column
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    embedding vector({self.dimension}),
                    metadata JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT embedding_dim CHECK (vector_dims(embedding) = {self.dimension})
                );
            """)
            
            # Create index for cosine similarity search
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_cosine 
                ON document_chunks USING ivfflat (embedding vector_cosine_ops);
            """)
            
            self._conn.commit()

    def upsert(self, id: str, vector: List[float], metadata: Dict[str, Any]):
        """Insert or update a vector with metadata."""
        conn = self._get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO document_chunks (id, embedding, metadata)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata;
            """, (id, vector, Json(metadata)))
            conn.commit()

    def search(self, query_embedding: List[float], top_k: int = 5, **filters) -> List[Dict[str, Any]]:
        """Search for similar vectors using cosine similarity.
        
        Args:
            query_embedding: The query vector to compare against
            top_k: Number of results to return
            **filters: Optional metadata filters (e.g., filename='data.xlsx')
        
        Returns:
            List of matches with id, embedding, metadata, and similarity score
        """
        if len(query_embedding) != self.dimension:
            raise ValueError(f"Query embedding dimension {len(query_embedding)} "
                           f"does not match expected dimension {self.dimension}")
        
        conn = self._get_connection()
        with conn.cursor() as cur:
            # Build WHERE clause from filters
            where_clauses = []
            params = [query_embedding, top_k]
            
            for key, value in filters.items():
                where_clauses.append(f"metadata->>%s = %s")
                params.extend([key, str(value)])
            
            where_sql = " AND ".join(where_clauses)
            if where_sql:
                where_sql = "WHERE " + where_sql
            
            # Execute cosine similarity search
            cur.execute(f"""
                SELECT 
                    id,
                    embedding,
                    metadata,
                    1 - (embedding <=> %s) as similarity
                FROM document_chunks
                {where_sql}
                ORDER BY embedding <=> %s
                LIMIT %s;
            """, params)
            
            results = []
            for row in cur.fetchall():
                results.append({
                    "id": row[0],
                    "embedding": row[1],
                    "metadata": row[2],
                    "similarity": float(row[3])
                })
            
            return results

    def close(self):
        """Close the database connection."""
        if self._conn and not self._conn.closed:
            self._conn.close()