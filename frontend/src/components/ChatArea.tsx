import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Facebook, Instagram, Video, Loader2, Linkedin, MessageCircle, Check } from 'lucide-react';
import { cn } from '../lib/utils';
import type { Message } from '../App';

interface ChatAreaProps {
    messages: Message[];
    onSendMessage: (content: string) => void;
    isLoading: boolean;
    selectedNetworks: string[];
    setSelectedNetworks: (networks: string[]) => void;
}

export default function ChatArea({
    messages,
    onSendMessage,
    isLoading,
    selectedNetworks,
    setSelectedNetworks
}: ChatAreaProps) {
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleSend = () => {
        if (!input.trim() || isLoading) return;
        onSendMessage(input);
        setInput('');
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const toggleNetwork = (network: string) => {
        if (selectedNetworks.includes(network)) {
            setSelectedNetworks(selectedNetworks.filter(n => n !== network));
        } else {
            setSelectedNetworks([...selectedNetworks, network]);
        }
    };

    const NetworkButton = ({ id, icon: Icon, label, colorClass }: { id: string, icon: any, label: string, colorClass: string }) => {
        const isSelected = selectedNetworks.includes(id);
        return (
            <button
                onClick={() => toggleNetwork(id)}
                className={cn(
                    "flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all border",
                    isSelected
                        ? cn("bg-opacity-20 border-opacity-50 ring-1 ring-opacity-50", colorClass.replace('text-', 'bg-').replace('hover:', ''), colorClass.replace('text-', 'border-').replace('hover:', ''), colorClass.replace('text-', 'ring-').replace('hover:', ''), "text-white")
                        : "bg-gray-800 border-gray-700 text-gray-400 hover:bg-gray-700"
                )}
            >
                <div className="relative">
                    <Icon size={14} className={cn(isSelected ? "text-white" : colorClass)} />
                    {isSelected && (
                        <div className="absolute -top-1 -right-1 bg-white rounded-full p-[1px]">
                            <Check size={6} className="text-black" strokeWidth={4} />
                        </div>
                    )}
                </div>
                {label}
            </button>
        );
    };

    return (
        <div className="flex flex-col h-full w-full max-w-5xl mx-auto">
            {/* Network Selector Toolbar */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 p-4 border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-10">
                <span className="text-xs text-gray-500 font-medium uppercase tracking-wider mr-2 hidden sm:inline">Target Networks:</span>
                <div className="flex flex-wrap justify-center gap-2">
                    <NetworkButton id="facebook" icon={Facebook} label="Facebook" colorClass="text-blue-500" />
                    <NetworkButton id="instagram" icon={Instagram} label="Instagram" colorClass="text-pink-500" />
                    <NetworkButton id="tiktok" icon={Video} label="TikTok" colorClass="text-black dark:text-white" />
                    <NetworkButton id="linkedin" icon={Linkedin} label="LinkedIn" colorClass="text-blue-400" />
                    <NetworkButton id="whatsapp" icon={MessageCircle} label="WhatsApp" colorClass="text-green-500" />
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin scrollbar-thumb-gray-700">
                {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center p-8 opacity-50">
                        <div className="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center mb-4">
                            <Bot size={32} className="text-white" />
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">How can I help you today?</h2>
                        <p className="text-gray-400 max-w-md">
                            I can help you generate content for your social networks. Select the target platforms above and tell me what you want to post.
                        </p>
                    </div>
                ) : (
                    messages.map((msg, index) => (
                        <div
                            key={index}
                            className={cn(
                                "flex gap-4 max-w-3xl mx-auto w-full",
                                msg.role === 'user' ? "justify-end" : "justify-start"
                            )}
                        >
                            {/* Avatar Assistant */}
                            {msg.role === 'assistant' && (
                                <div className="w-8 h-8 rounded-sm bg-green-600 flex-shrink-0 flex items-center justify-center mt-1">
                                    <Bot size={18} className="text-white" />
                                </div>
                            )}

                            {/* Message Content */}
                            <div
                                className={cn(
                                    "relative px-5 py-3.5 text-sm leading-relaxed shadow-sm max-w-[85%]",
                                    msg.role === 'user'
                                        ? "bg-gray-700 text-white rounded-2xl rounded-tr-sm"
                                        : "text-gray-100 rounded-md" // Assistant messages look transparent/clean like ChatGPT
                                )}
                            >
                                <div className="whitespace-pre-wrap">{msg.content}</div>
                            </div>

                            {/* Avatar User */}
                            {msg.role === 'user' && (
                                <div className="w-8 h-8 rounded-sm bg-gray-600 flex-shrink-0 flex items-center justify-center mt-1">
                                    <User size={18} className="text-white" />
                                </div>
                            )}
                        </div>
                    ))
                )}

                {isLoading && (
                    <div className="flex gap-4 max-w-3xl mx-auto w-full">
                        <div className="w-8 h-8 rounded-sm bg-green-600 flex-shrink-0 flex items-center justify-center mt-1">
                            <Bot size={18} className="text-white" />
                        </div>
                        <div className="flex items-center mt-2">
                            <Loader2 size={16} className="animate-spin text-gray-400" />
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-gray-900 border-t border-gray-800">
                <div className="max-w-3xl mx-auto relative bg-gray-800 rounded-xl border border-gray-700 shadow-sm focus-within:border-gray-500 focus-within:ring-1 focus-within:ring-gray-500 transition-all">
                    <textarea
                        ref={textareaRef}
                        value={input}
                        onChange={(e) => {
                            setInput(e.target.value);
                            e.target.style.height = 'auto';
                            e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
                        }}
                        onKeyDown={handleKeyDown}
                        placeholder="Send a message..."
                        className="w-full bg-transparent text-white placeholder-gray-400 px-4 py-3 pr-12 rounded-xl resize-none outline-none max-h-[200px] overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600"
                        rows={1}
                        style={{ minHeight: '52px' }}
                    />
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || isLoading}
                        className={cn(
                            "absolute right-2 bottom-2 p-2 rounded-lg transition-colors",
                            input.trim() && !isLoading
                                ? "bg-white text-black hover:bg-gray-200"
                                : "bg-transparent text-gray-500 cursor-not-allowed"
                        )}
                    >
                        <Send size={18} />
                    </button>
                </div>
                <div className="text-center mt-2">
                    <p className="text-[10px] text-gray-500">
                        AI can make mistakes. Consider checking important information.
                    </p>
                </div>
            </div>
        </div>
    );
}
