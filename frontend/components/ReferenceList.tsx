"use client";
import { useState } from 'react';
import { Evidence } from '../types';

export default function ReferenceList({ evidence }: { evidence: Evidence[] }) {
    const [isOpen, setIsOpen] = useState(false);

    if (!evidence || evidence.length === 0) return null;

    return (
        <div className="mt-4">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="text-sm text-blue-500 hover:text-blue-700 underline flex items-center gap-1 focus:outline-none transition-colors"
            >
                <span className="text-xs">{isOpen ? '▼' : '▶'}</span>
                <span>근거 개념 확인하기 ({evidence.length})</span>
            </button>

            {isOpen && (
                <div className="mt-2 pl-4 border-l-2 border-indigo-100 text-sm">
                    <ul className="space-y-2">
                        {evidence.map((item, idx) => (
                            <li key={idx} className="bg-white border border-gray-100 p-3 rounded-lg shadow-sm">
                                <div className="flex items-center gap-2 mb-1">
                                    <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-50 text-indigo-600">
                                        {item.subject}
                                    </span>
                                    <span className="text-xs text-gray-400">&gt;</span>
                                    <span className="text-xs text-gray-500">{item.chapter}</span>
                                </div>
                                <div className="text-gray-800 font-medium ml-1">
                                    {item.concept}
                                </div>
                                {item.desc && <div className="text-xs text-gray-500 mt-1 ml-1">{item.desc}</div>}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}
