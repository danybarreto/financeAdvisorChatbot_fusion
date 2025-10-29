import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from models.filters import DocumentFilter

logger = logging.getLogger(__name__)

class EnhancedEmbeddingService:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
        self.persist_directory = persist_directory
    
    def extract_metadata_from_filename(self, filename: str) -> Dict[str, Any]:
        """Extraer metadatos del nombre del archivo"""
        try:
            # Patrones comunes en nombres de reportes financieros
            # Ejemplo: "Apple_AAPL_2023_Annual_Report.pdf"
            patterns = [
                r'(?P<company>[\w\s]+)_(?P<ticker>[A-Z]+)_(?P<year>\d{4})_(?P<type>[\w\s]+)\.pdf',
                r'(?P<ticker>[A-Z]+)_(?P<year>\d{4})_(?P<type>[\w\s]+)\.pdf',
                r'(?P<company>[\w\s]+)_(?P<year>\d{4})_(?P<type>[\w\s]+)\.pdf'
            ]
            
            metadata = {
                'filename': filename,
                'company_name': '',
                'ticker': '',
                'year': None,
                'document_type': 'Unknown'
            }
            
            for pattern in patterns:
                match = re.match(pattern, filename, re.IGNORECASE)
                if match:
                    groups = match.groupdict()
                    metadata.update({k: v for k, v in groups.items() if v})
                    break
            
            # Si no encontramos con patrones, intentar extraer información básica
            if not metadata['year']:
                year_match = re.search(r'(\d{4})', filename)
                if year_match:
                    metadata['year'] = int(year_match.group(1))
            
            if not metadata['ticker']:
                # Buscar ticker en mayúsculas (generalmente 1-5 letras)
                ticker_match = re.search(r'([A-Z]{1,5})', filename)
                if ticker_match:
                    metadata['ticker'] = ticker_match.group(1)
            
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata from {filename}: {e}")
            return {'filename': filename}
    
    def filter_documents(self, filters: Optional[DocumentFilter] = None) -> List[str]:
        """Filtrar documentos basado en los criterios proporcionados"""
        try:
            # Obtener todos los metadatos de la base de datos vectorial
            collection = self.vector_store._collection.get()
            metadatas = collection['metadatas']
            documents = collection['documents']
            ids = collection['ids']
            
            filtered_ids = []
            
            for i, metadata in enumerate(metadatas):
                if self._matches_filters(metadata, filters):
                    filtered_ids.append(ids[i])
            
            return filtered_ids
        except Exception as e:
            logger.error(f"Error filtering documents: {e}")
            return []
    
    def _matches_filters(self, metadata: Dict[str, Any], filters: Optional[DocumentFilter]) -> bool:
        """Verificar si un documento coincide con los filtros"""
        if not filters:
            return True
        
        # Filtrar por nombre de empresa
        if filters.company_name and filters.company_name.lower() not in metadata.get('company_name', '').lower():
            return False
        
        # Filtrar por ticker
        if filters.ticker and filters.ticker.upper() != metadata.get('ticker', '').upper():
            return False
        
        # Filtrar por año
        if filters.year and filters.year != metadata.get('year'):
            return False
        
        # Filtrar por tipo de documento
        if filters.document_type and filters.document_type.lower() not in metadata.get('document_type', '').lower():
            return False
        
        # Filtrar por rango de fechas
        doc_year = metadata.get('year')
        if doc_year:
            if filters.start_date:
                start_year = int(filters.start_date[:4]) if filters.start_date else None
                if start_year and doc_year < start_year:
                    return False
            
            if filters.end_date:
                end_year = int(filters.end_date[:4]) if filters.end_date else None
                if end_year and doc_year > end_year:
                    return False
        
        return True
    
    def similarity_search_with_filters(
        self, 
        query: str, 
        filters: Optional[DocumentFilter] = None,
        k: int = 4
    ) -> List[Document]:
        """Búsqueda semántica con filtros aplicados"""
        try:
            # Primero filtrar los documentos
            filtered_ids = self.filter_documents(filters)
            
            if filtered_ids:
                # Si hay filtros, buscar solo en los documentos filtrados
                where_filter = {"id": {"$in": filtered_ids}} if filtered_ids else None
                results = self.vector_store.similarity_search(
                    query=query,
                    k=min(k, len(filtered_ids)) if filtered_ids else k,
                    filter=where_filter
                )
            else:
                # Si no hay filtros o no hay documentos que coincidan, búsqueda normal
                results = self.vector_store.similarity_search(query=query, k=k)
            
            return results
        except Exception as e:
            logger.error(f"Error in similarity search with filters: {e}")
            return []