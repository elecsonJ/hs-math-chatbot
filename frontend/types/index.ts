export interface Evidence {
    subject: string;
    chapter: string;
    concept: string;
    desc?: string;
}

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    evidence?: Evidence[];
}
