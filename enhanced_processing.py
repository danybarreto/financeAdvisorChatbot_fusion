import asyncio
import logging
from services.embedding_service import EnhancedEmbeddingService
from services.nasdaq_service import NasdaqDataService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhanced_functionality():
    """Probar la funcionalidad mejorada"""
    
    # Probar servicio de embeddings con filtros
    embedding_service = EnhancedEmbeddingService()
    
    # Ejemplo de filtros
    from models.filters import DocumentFilter
    
    filters = DocumentFilter(
        company_name="Apple",
        year=2023
    )
    
    # Probar filtrado
    filtered_ids = embedding_service.filter_documents(filters)
    print(f"Documentos filtrados: {len(filtered_ids)}")
    
    # Probar búsqueda semántica con filtros
    results = embedding_service.similarity_search_with_filters(
        query="financial performance",
        filters=filters,
        k=3
    )
    
    print("Resultados de búsqueda con filtros:")
    for doc in results:
        print(f"- {doc.metadata.get('filename')}")
    
    # Probar servicio Nasdaq
    nasdaq_service = NasdaqDataService()
    company_info = await nasdaq_service.get_company_info("AAPL")
    print(f"\nInformación de Apple: {company_info.get('name')}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_functionality())