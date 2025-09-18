// src/components/InitialScreen.jsx
import React from 'react';
import ChatInput from './ChatInput';

const InitialScreen = ({ onSendMessage, isLoading }) => {
  const examplePrompts = [
    "List all profiles and their locations",
    "What are the 5 warmest temperature readings?",
    "Show me salinity profiles near the equator",
    "Map the location of the deepest measurement",
  ];

  return (
    <div className="flex flex-col h-screen w-screen bg-gray-900 text-white">
      {/* Logo in top left corner */}
      <div className="absolute top-6 left-6">
        <h1 className="text-2xl font-bold text-blue-400">🌊 FloatChat AI</h1>
      </div>
      
      {/* Main content centered */}
      <div className="flex-grow flex flex-col items-center justify-center text-center px-6 pt-24">
        <h1 className="text-5xl font-bold mb-6">
          <div className="text-white">Conversational AI for Intelligent</div>
          <div className="text-blue-500">Ocean Data Discovery</div>
        </h1>
        <p className="text-lg text-gray-400 mb-16 max-w-4xl leading-relaxed mt-2">
          Explore vast and complex ARGO ocean data through a simple conversation. Our AI-powered assistant, FloatChat, translates your questions into powerful data visualizations and insights, making oceanography accessible to everyone.
        </p>
        
        <div className="grid grid-cols-2 gap-4 mb-12 mt-12">
          {examplePrompts.map((prompt) => (
            <button
              key={prompt}
              onClick={() => onSendMessage(prompt)}
              disabled={isLoading}
              className="p-4 bg-gray-800 border border-gray-700 rounded-lg hover:bg-gray-700 transition-colors text-left"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>
      
      {/* Input at bottom */}
      <div className="w-full max-w-3xl p-4 mx-auto">
        <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};

export default InitialScreen;