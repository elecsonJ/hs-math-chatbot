import { Message } from '../types';
import ReferenceList from './ReferenceList';

export default function MessageBubble({ message }: { message: Message }) {
    const isUser = message.role === 'user';

    return (
        <div className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div
                className={`max-w-[85%] md:max-w-[70%] px-5 py-4 rounded-2xl shadow-sm text-[15px] leading-relaxed
        ${isUser
                        ? 'bg-indigo-600 text-white rounded-br-none'
                        : 'bg-white text-gray-800 border border-gray-100 rounded-bl-none'
                    }`}
            >
                <div className="whitespace-pre-wrap">{message.content}</div>

                {!isUser && message.evidence && (
                    <ReferenceList evidence={message.evidence} />
                )}
            </div>
        </div>
    );
}
