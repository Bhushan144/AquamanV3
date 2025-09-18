// src/components/ChatColumn.jsx
import React, { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import { useState } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ChatInput from './ChatInput';

const ChatColumn = ({ messages, isLoading, onSendMessage }) => {
  const chatHistoryRef = useRef(null);
  const [copied, setCopied] = useState(false);

  // Auto-scroll to the bottom of the chat
  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  return (
    <div className="flex flex-col h-full bg-gray-800 p-4">
      <div className="flex-grow overflow-y-auto pr-2
        [&::-webkit-scrollbar]:w-2
        [&::-webkit-scrollbar-track]:bg-gray-100
        [&::-webkit-scrollbar-thumb]:bg-gray-300
        dark:[&::-webkit-scrollbar-track]:bg-neutral-700
        dark:[&::-webkit-scrollbar-thumb]:bg-neutral-500" ref={chatHistoryRef}>
        {messages.map((msg, index) => (
          <ChatMessage
            key={index}
            message={msg}
            onCopy={() => {
              toast.success('Copied to clipboard', {
                position: 'bottom-right',
                autoClose: 1500,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                theme: 'dark',
              });
            }}
          />
        ))}
        {isLoading && <ChatMessage message={{ role: 'assistant', content: 'Thinking...' }} />}
      </div>
      <ToastContainer />
      <div className="mt-4">
        <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};

export default ChatColumn;