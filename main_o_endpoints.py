from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from models.filters import SearchQuery, DocumentFilter
from services.rag_service import EnhancedRAGService
from services.nasdaq_service import NasdaqDataService

router = APIRouter()
rag_service = EnhancedRAGService()
nasdaq_service = NasdaqDataService()

@router.post("/chat")
async def chat_with_filters(search_query: SearchQuery):
    """Endpoint de chat con soporte para filtros"""
    try:
        response = await rag_service.get_enhanced_response(search_query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filters/available")
async def get_available_filters():
    """Obtener filtros disponibles"""
    try:
        filters = await rag_service.get_available_filters()
        return filters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{symbol}/info")
async def get_company_info(symbol: str):
    """Obtener información de una empresa específica"""
    try:
        info = await nasdaq_service.get_company_info(symbol)
        if not info:
            raise HTTPException(status_code=404, detail="Company not found")
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stock/{symbol}/data")
async def get_stock_data(symbol: str, period: Optional[str] = "1mo"):
    """Obtener datos de stock en tiempo real"""
    try:
        data = await nasdaq_service.get_stock_data(symbol, period)
        if not data:
            raise HTTPException(status_code=404, detail="Stock data not found")
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/search")
async def search_documents(
    query: str,
    company_name: Optional[str] = None,
    ticker: Optional[str] = None,
    year: Optional[int] = None,
    document_type: Optional[str] = None,
    max_results: int = 10
):
    """Búsqueda de documentos con filtros por query parameters"""
    try:
        filters = DocumentFilter(
            company_name=company_name,
            ticker=ticker,
            year=year,
            document_type=document_type
        )
        
        search_query = SearchQuery(
            query=query,
            filters=filters,
            max_results=max_results
        )
        
        response = await rag_service.get_enhanced_response(search_query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))