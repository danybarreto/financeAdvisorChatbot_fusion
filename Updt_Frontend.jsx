import { useState, useEffect } from 'react';

const FiltersPanel = ({ onFiltersChange }) => {
    const [filters, setFilters] = useState({
        company_name: '',
        ticker: '',
        year: '',
        document_type: ''
    });
    
    const [availableFilters, setAvailableFilters] = useState({
        available_companies: [],
        available_tickers: [],
        available_years: [],
        available_document_types: []
    });

    useEffect(() => {
        // Cargar filtros disponibles
        fetchAvailableFilters();
    }, []);

    const fetchAvailableFilters = async () => {
        try {
            const response = await fetch('/api/filters/available');
            const data = await response.json();
            setAvailableFilters(data);
        } catch (error) {
            console.error('Error loading filters:', error);
        }
    };

    const handleFilterChange = (key, value) => {
        const newFilters = {
            ...filters,
            [key]: value
        };
        setFilters(newFilters);
        onFiltersChange(newFilters);
    };

    return (
        <div className="bg-white p-4 rounded-lg shadow-md mb-4">
            <h3 className="text-lg font-semibold mb-3">Filtros de Búsqueda</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Filtro por Empresa */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Empresa
                    </label>
                    <select
                        value={filters.company_name}
                        onChange={(e) => handleFilterChange('company_name', e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-md"
                    >
                        <option value="">Todas las empresas</option>
                        {availableFilters.available_companies.map(company => (
                            <option key={company} value={company}>
                                {company}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Filtro por Ticker */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Símbolo (Ticker)
                    </label>
                    <select
                        value={filters.ticker}
                        onChange={(e) => handleFilterChange('ticker', e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-md"
                    >
                        <option value="">Todos los tickers</option>
                        {availableFilters.available_tickers.map(ticker => (
                            <option key={ticker} value={ticker}>
                                {ticker}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Filtro por Año */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Año
                    </label>
                    <select
                        value={filters.year}
                        onChange={(e) => handleFilterChange('year', e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-md"
                    >
                        <option value="">Todos los años</option>
                        {availableFilters.available_years.map(year => (
                            <option key={year} value={year}>
                                {year}
                            </option>
                        ))}
                    </select>
                </div>

                {/* Filtro por Tipo de Documento */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Tipo de Documento
                    </label>
                    <select
                        value={filters.document_type}
                        onChange={(e) => handleFilterChange('document_type', e.target.value)}
                        className="w-full p-2 border border-gray-300 rounded-md"
                    >
                        <option value="">Todos los tipos</option>
                        {availableFilters.available_document_types.map(type => (
                            <option key={type} value={type}>
                                {type}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Botón para limpiar filtros */}
            <div className="mt-4">
                <button
                    onClick={() => {
                        const emptyFilters = {
                            company_name: '',
                            ticker: '',
                            year: '',
                            document_type: ''
                        };
                        setFilters(emptyFilters);
                        onFiltersChange(emptyFilters);
                    }}
                    className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                    Limpiar Filtros
                </button>
            </div>
        </div>
    );
};

export default FiltersPanel;