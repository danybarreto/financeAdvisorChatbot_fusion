from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DocumentFilter(BaseModel):
    """Filtros para búsqueda de documentos"""
    company_name: Optional[str] = Field(None, description="Nombre de la empresa o parte del nombre")
    ticker: Optional[str] = Field(None, description="Símbolo de la empresa (ej: AAPL, MSFT)")
    year: Optional[int] = Field(None, description="Año del reporte")
    start_date: Optional[str] = Field(None, description="Fecha de inicio para filtro por rango")
    end_date: Optional[str] = Field(None, description="Fecha de fin para filtro por rango")
    document_type: Optional[str] = Field(None, description="Tipo de documento (Annual Report, 10-K, etc.)")
    
    class Config:
        schema_extra = {
            "example": {
                "company_name": "Apple",
                "ticker": "AAPL",
                "year": 2023,
                "document_type": "Annual Report"
            }
        }

class SearchQuery(BaseModel):
    """Consulta de búsqueda con filtros"""
    query: str = Field(..., description="Consulta de búsqueda en lenguaje natural")
    filters: Optional[DocumentFilter] = Field(None, description="Filtros para aplicar a la búsqueda")
    max_results: int = Field(10, description="Número máximo de resultados a retornar")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What were the main financial highlights?",
                "filters": {
                    "company_name": "Apple",
                    "year": 2023
                },
                "max_results": 5
            }
        }