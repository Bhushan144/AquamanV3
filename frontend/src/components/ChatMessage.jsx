// src/components/ChatMessage.jsx
import React from 'react';
import { Copy } from 'lucide-react';

const ChatMessage = ({ message, onCopy }) => {
  const { role, content } = message;
  const isUser = role === 'user';
  const isAssistant = role === 'assistant';

  const handleCopy = async () => {
    if (!isAssistant || !content || content === 'Thinking...') return;
    try {
      await navigator.clipboard.writeText(content);
      if (onCopy) onCopy();
    } catch (e) {
      console.error('Copy failed', e);
    }
  };

  return (
    <div className={`flex my-2 ${isUser ? 'justify-end' : 'justify-start'} items-center gap-2`}>
      {/* User bubble (right aligned) */}
      {isUser && (
        <div className={`px-4 py-2 rounded-2xl max-w-[85%] ${isUser ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-200'}`}>
          {content === 'Thinking...' ? (
            <div className="mt-1 text-base flex items-center gap-2">
              <span>Thinking</span>
              <span className="inline-flex">
                <span className="w-2 h-2 bg-gray-200 rounded-full animate-bounce" style={{ animationDelay: '-0.3s' }}></span>
                <span className="w-2 h-2 bg-gray-200 rounded-full animate-bounce mx-1" style={{ animationDelay: '-0.15s' }}></span>
                <span className="w-2 h-2 bg-gray-200 rounded-full animate-bounce"></span>
              </span>
            </div>
          ) : (
            <div className="mt-1 text-base whitespace-pre-wrap">{content}</div>
          )}
        </div>
      )}

      {/* Assistant bubble (left) with trailing copy button */}
      {isAssistant && (
        <>
          <div className={`px-4 py-2 rounded-2xl max-w-[85%] ${isAssistant ? 'bg-gray-700 text-gray-200' : 'bg-blue-600 text-white'}`}>
            {content === 'Thinking...' ? (
              <div className="mt-1 text-base flex items-center gap-2">
                <span>Thinking</span>
                <span className="inline-flex">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '-0.3s' }}></span>
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce mx-1" style={{ animationDelay: '-0.15s' }}></span>
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                </span>
              </div>
            ) : (
              <div className="mt-1 text-base whitespace-pre-wrap">{content}</div>
            )}
          </div>
          {content && content !== 'Thinking...' && (
            <button
              onClick={handleCopy}
              title="Copy"
              aria-label="Copy response"
              className="shrink-0 p-2 rounded-md border border-gray-600 text-gray-200 hover:bg-gray-700 transition-colors"
            >
              <Copy size={16} />
            </button>
          )}
        </>
      )}
    </div>
  );
};

export default ChatMessage;