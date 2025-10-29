import os
from typing import List, Dict, Any, Optional
import logging
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import Document

from services.embedding_service import EnhancedEmbeddingService
from services.nasdaq_service import NasdaqDataService
from models.filters import DocumentFilter, SearchQuery

logger = logging.getLogger(__name__)

class EnhancedRAGService:
    def __init__(self):
        self.embedding_service = EnhancedEmbeddingService()
        self.nasdaq_service = NasdaqDataService()
        self.llm = OpenAI(temperature=0, model_name="gpt-3.5-turbo")
        
        # Definir prompt template mejorado
        self.prompt_template = PromptTemplate(
            template="""Eres un asistente financiero especializado en análisis de reportes anuales y datos de mercado.

Contexto del documento:
{context}

Información actual de mercado (si aplica):
{market_data}

Pregunta del usuario: {question}

Instrucciones:
1. Basa tu respuesta principalmente en el contexto del documento proporcionado
2. Complementa con la información de mercado cuando sea relevante
3. Si la información solicitada no está en el contexto, usa la información de mercado disponible
4. Sé preciso y claro en tus explicaciones financieras
5. Incluye datos específicos cuando estén disponibles

Respuesta:""",
            input_variables=["context", "market_data", "question"]
        )
    
    async def get_enhanced_response(self, search_query: SearchQuery) -> Dict[str, Any]:
        """Obtener respuesta mejorada con filtros y datos en tiempo real"""
        try:
            # Realizar búsqueda semántica con filtros
            context_docs = self.embedding_service.similarity_search_with_filters(
                query=search_query.query,
                filters=search_query.filters,
                k=search_query.max_results
            )
            
            # Extraer contexto de los documentos
            context = "\n\n".join([doc.page_content for doc in context_docs])
            
            # Obtener información de mercado si hay un ticker específico
            market_data = ""
            if search_query.filters and search_query.filters.ticker:
                company_info = await self.nasdaq_service.get_company_info(search_query.filters.ticker)
                stock_data = await self.nasdaq_service.get_stock_data(search_query.filters.ticker)
                
                market_data = f"""
Información de {search_query.filters.ticker}:
- Empresa: {company_info.get('name', 'N/A')}
- Sector: {company_info.get('sector', 'N/A')}
- Precio actual: ${stock_data.get('current_price', 'N/A')}
- Cambio: {stock_data.get('change_percent', 'N/A')}%
- Capitalización de mercado: ${company_info.get('market_cap', 'N/A'):,}
"""
            
            # Generar respuesta usando el LLM
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.embedding_service.vector_store.as_retriever(),
                chain_type_kwargs={"prompt": self.prompt_template}
            )
            
            # Preparar input para la cadena
            enhanced_input = {
                "context": context,
                "market_data": market_data,
                "question": search_query.query
            }
            
            response = qa_chain.run(enhanced_input)
            
            return {
                "response": response,
                "source_documents": [
                    {
                        "filename": doc.metadata.get("filename", "Unknown"),
                        "company_name": doc.metadata.get("company_name", "Unknown"),
                        "ticker": doc.metadata.get("ticker", "Unknown"),
                        "year": doc.metadata.get("year", "Unknown"),
                        "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
                    }
                    for doc in context_docs
                ],
                "market_data": market_data.strip() if market_data else None,
                "filters_applied": search_query.filters.dict() if search_query.filters else None
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced RAG response: {e}")
            return {
                "response": "Lo siento, hubo un error procesando tu consulta.",
                "source_documents": [],
                "error": str(e)
            }
    
    async def get_available_filters(self) -> Dict[str, Any]:
        """Obtener filtros disponibles en la base de datos"""
        try:
            collection = self.embedding_service.vector_store._collection.get()
            metadatas = collection['metadatas']
            
            companies = set()
            tickers = set()
            years = set()
            doc_types = set()
            
            for metadata in metadatas:
                if metadata.get('company_name'):
                    companies.add(metadata['company_name'])
                if metadata.get('ticker'):
                    tickers.add(metadata['ticker'])
                if metadata.get('year'):
                    years.add(metadata['year'])
                if metadata.get('document_type'):
                    doc_types.add(metadata['document_type'])
            
            return {
                "available_companies": sorted(list(companies)),
                "available_tickers": sorted(list(tickers)),
                "available_years": sorted(list(years), reverse=True),
                "available_document_types": sorted(list(doc_types)),
                "total_documents": len(metadatas)
            }
        except Exception as e:
            logger.error(f"Error getting available filters: {e}")
            return {}