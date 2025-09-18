// src/App.jsx
import React, { useState } from 'react';
import axios from 'axios';
import { MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css';
import InitialScreen from './components/InitialScreen';
import ChatColumn from './components/ChatColumn';
import VisualizationColumn from './components/VisualizationColumn';

// Prefer env-configured backend; fallback to common defaults
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';
const API_URL = `${API_BASE}/chat`;

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  // 'initial' or 'dashboard'
  const [layoutMode, setLayoutMode] = useState('initial'); 

  const handleSendMessage = async (prompt) => {
    const userMessage = { role: 'user', content: prompt };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    // Immediately switch to dashboard layout and show thinking state
    if (layoutMode === 'initial') {
      setLayoutMode('dashboard');
    }
    setIsLoading(true);

    try {
      const response = await axios.post(API_URL, { input: prompt });
      // Support both {data:{...}} and flat {...}
      const payload = response.data?.data ?? response.data;
      const { output, table_data, geo_data, sql_query } = payload || {};
      
      const assistantMessage = {
        role: 'assistant',
        content: output || 'No response text from backend.',
        table_data: table_data || null,
        geo_data: geo_data || null,
        sql_query: sql_query || '',
      };
      
      setMessages(prevMessages => [...prevMessages, assistantMessage]);

    } catch (error) {
      console.error("Error connecting to the backend:", error);
      const errorMessage = {
        role: 'assistant',
        content: `Error: Could not connect to the backend at ${API_URL}. ${error?.message || ''}`,
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <MantineProvider>
      <div className="flex h-screen w-screen bg-gray-900 overflow-hidden">
        {/* Left: Visualizations (animate width) */}
        <div
          className="transition-all duration-700 ease-in-out border-r-2 border-gray-800 overflow-hidden"
          style={{ width: layoutMode === 'initial' ? '0%' : '60%' }}
        >
          {layoutMode === 'dashboard' && (
            <VisualizationColumn messages={messages} isLoading={isLoading} />
          )}
        </div>

        {/* Right: Chat (animate width) */}
        <div
          className="transition-all duration-700 ease-in-out"
          style={{ width: layoutMode === 'initial' ? '100%' : '40%' }}
        >
          {layoutMode === 'initial' ? (
            <InitialScreen onSendMessage={handleSendMessage} isLoading={isLoading} />
          ) : (
            <ChatColumn messages={messages} isLoading={isLoading} onSendMessage={handleSendMessage} />
          )}
        </div>
      </div>
    </MantineProvider>
  );
}

export default App;