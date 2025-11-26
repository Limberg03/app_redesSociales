import { MessageSquare, Plus, Trash2, LogOut, User } from 'lucide-react';
import { cn } from '../lib/utils';
import type { Conversation } from '../App';

interface ChatSidebarProps {
    conversations: Conversation[];
    currentConversationId: number | null;
    onSelectConversation: (id: number) => void;
    onNewChat: () => void;
    onDeleteConversation: (id: number) => void;
    onLogout: () => void;
    currentUser?: any;
}

export default function ChatSidebar({
    conversations,
    currentConversationId,
    onSelectConversation,
    onNewChat,
    onDeleteConversation,
    onLogout,
    currentUser
}: ChatSidebarProps) {
    return (
        <div className="flex flex-col h-full w-64 bg-black text-gray-100 border-r border-gray-800">
            {/* New Chat Button */}
            <div className="p-3">
                <button
                    onClick={onNewChat}
                    className="flex items-center gap-3 w-full px-3 py-3 rounded-md border border-gray-700 hover:bg-gray-900 transition-colors text-sm text-white"
                >
                    <Plus size={16} />
                    <span>New chat</span>
                </button>
            </div>

            {/* Conversation List */}
            <div className="flex-1 overflow-y-auto px-3 py-2 space-y-2 no-scrollbar">
                <div className="text-xs font-medium text-gray-500 mb-2 px-2">Recent</div>
                {conversations.map((conv) => (
                    <div
                        key={conv.id}
                        className={cn(
                            "group flex items-center gap-3 px-3 py-3 rounded-md cursor-pointer text-sm transition-colors relative",
                            currentConversationId === conv.id
                                ? "bg-gray-800 text-white"
                                : "text-gray-300 hover:bg-gray-900"
                        )}
                        onClick={() => onSelectConversation(conv.id)}
                    >
                        <MessageSquare size={16} className="text-gray-400" />
                        <span className="truncate flex-1 pr-6">{conv.title || "New Chat"}</span>

                        {/* Delete Button (visible on hover or active) */}
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                onDeleteConversation(conv.id);
                            }}
                            className={cn(
                                "absolute right-2 text-gray-400 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity",
                                currentConversationId === conv.id && "opacity-100"
                            )}
                        >
                            <Trash2 size={14} />
                        </button>
                    </div>
                ))}

                {conversations.length === 0 && (
                    <div className="text-center text-gray-600 text-xs py-4">
                        No conversations yet
                    </div>
                )}
            </div>

            {/* User Footer */}
            <div className="p-3 border-t border-gray-800">
                <div className="flex items-center gap-3 px-3 py-3 rounded-md hover:bg-gray-900 cursor-pointer transition-colors group">
                    <div className="w-8 h-8 rounded bg-green-600 flex items-center justify-center text-white font-bold text-xs">
                        {currentUser?.username?.charAt(0).toUpperCase() || <User size={16} />}
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <div className="text-sm font-medium text-white truncate">
                            {currentUser?.username || 'User'}
                        </div>
                    </div>
                    <button
                        onClick={onLogout}
                        className="text-gray-400 hover:text-white"
                        title="Logout"
                    >
                        <LogOut size={16} />
                    </button>
                </div>
            </div>
        </div>
    );
}
