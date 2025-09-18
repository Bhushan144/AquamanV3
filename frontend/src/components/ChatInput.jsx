// src/components/ChatInput.jsx
import React, { useState } from 'react';
import { Send } from 'lucide-react';

const ChatInput = ({ onSendMessage, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything..."
          disabled={isLoading}
          className="w-full p-4 pr-12 text-white bg-gray-700 border border-gray-600 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="absolute inset-y-0 right-2 top-1 flex items-center justify-center w-12 h-12 text-white bg-blue-600 rounded-full disabled:bg-gray-500 hover:bg-blue-700"
        >
          <Send size={20} />
        </button>
      </div>
    </form>
  );
};

export default ChatInput;