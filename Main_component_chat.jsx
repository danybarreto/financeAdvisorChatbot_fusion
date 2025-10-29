import { useState } from 'react';
import FiltersPanel from './FiltersPanel';

const EnhancedChat = () => {
    const [query, setQuery] = useState('');
    const [filters, setFilters] = useState({});
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const handleSendMessage = async () => {
        if (!query.trim()) return;

        setIsLoading(true);
        const userMessage = { role: 'user', content: query };
        setMessages(prev => [...prev, userMessage]);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    filters: Object.keys(filters).some(key => filters[key]) ? filters : null,
                    max_results: 5
                }),
            });

            const data = await response.json();
            
            const assistantMessage = {
                role: 'assistant',
                content: data.response,
                sources: data.source_documents,
                market_data: data.market_data,
                filters_applied: data.filters_applied
            };

            setMessages(prev => [...prev, assistantMessage]);
            setQuery('');
        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                role: 'assistant',
                content: 'Lo siento, hubo un error procesando tu mensaje.',
                isError: true
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen max-w-4xl mx-auto">
            <h1 className="text-2xl font-bold p-4 border-b">
                Financial Advisor Chatbot
            </h1>

            {/* Panel de Filtros */}
            <FiltersPanel onFiltersChange={setFilters} />

            {/* Área de Mensajes */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`p-4 rounded-lg ${
                            message.role === 'user' 
                                ? 'bg-blue-100 ml-8' 
                                : 'bg-gray-100 mr-8'
                        } ${message.isError ? 'border border-red-300' : ''}`}
                    >
                        <div className="font-semibold mb-2">
                            {message.role === 'user' ? 'Tú' : 'Asistente'}
                        </div>
                        <div className="whitespace-pre-wrap">{message.content}</div>
                        
                        {/* Mostrar información adicional para respuestas del asistente */}
                        {message.role === 'assistant' && message.market_data && (
                            <div className="mt-3 p-3 bg-yellow-50 rounded border">
                                <strong>Información de Mercado:</strong>
                                <div className="whitespace-pre-wrap text-sm mt-1">
                                    {message.market_data}
                                </div>
                            </div>
                        )}
                        
                        {message.role === 'assistant' && message.sources && (
                            <div className="mt-3">
                                <strong>Fuentes:</strong>
                                <div className="text-sm mt-1 space-y-1">
                                    {message.sources.map((source, idx) => (
                                        <div key={idx} className="text-gray-600">
                                            • {source.filename} ({source.company_name} - {source.year})
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                ))}
                
                {isLoading && (
                    <div className="text-center text-gray-500">
                        Procesando...
                    </div>
                )}
            </div>

            {/* Input de Mensaje */}
            <div className="p-4 border-t">
                <div className="flex space-x-2">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                        placeholder="Escribe tu pregunta sobre reportes financieros..."
                        className="flex-1 p-2 border border-gray-300 rounded-md"
                        disabled={isLoading}
                    />
                    <button
                        onClick={handleSendMessage}
                        disabled={isLoading || !query.trim()}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                        Enviar
                    </button>
                </div>
            </div>
        </div>
    );
};

export default EnhancedChat;