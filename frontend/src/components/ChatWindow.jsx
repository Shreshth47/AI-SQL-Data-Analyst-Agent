import React, { useState, useRef, useEffect } from 'react';
import { Send, Database, Terminal, ChevronDown } from 'lucide-react';
import ResultTable from './ResultTable';
import ChartView from './ChartView';
import { askQuestion } from '../api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

export default function ChatWindow() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      answer: 'Hello! I am your AI Data Analyst. Ask me anything about your database in natural language.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userQuestion = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userQuestion }]);
    setLoading(true);

    try {
      const res = await askQuestion(userQuestion);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          answer: res.answer,
          sql: res.sql,
          rows: res.rows,
          chart: res.chart,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          answer: 'An error occurred while running the analysis. Make sure the backend server is running.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto px-4 py-6">
      {/* Header */}
      <header className="flex items-center gap-3 pb-4 border-b border-slate-800">
        <div className="p-2 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
          <Database size={22} />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-slate-100">AI SQL / Data Analyst Agent</h1>
          <p className="text-xs text-slate-400">PostgreSQL • Read-Only Sandbox • Gemini 3.6 Flash</p>
        </div>
      </header>

      {/* Message Feed */}
      <main className="flex-1 overflow-y-auto py-4 space-y-5 pr-2">
        {messages.map((m, index) => (
          <div key={index} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}>
            {m.role === 'user' ? (
              <div className="bg-indigo-600 text-white text-sm px-4 py-2.5 rounded-2xl rounded-tr-sm max-w-lg shadow-sm">
                {m.content}
              </div>
            ) : (
              <div className="w-full bg-slate-800/60 border border-slate-700/60 rounded-2xl p-4 text-sm text-slate-200 space-y-3">
                <div className="prose prose-invert prose-sm max-w-none text-slate-200">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm, remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                  >
                    {m.answer}
                  </ReactMarkdown>
                </div>

                {/* Collapsible SQL Query view */}
                {m.sql && (
                  <details className="group border border-slate-700/80 rounded-lg bg-slate-900/60 overflow-hidden">
                    <summary className="flex items-center justify-between px-3 py-2 cursor-pointer text-xs font-mono text-slate-400 hover:text-slate-200">
                      <span className="flex items-center gap-2">
                        <Terminal size={14} className="text-emerald-400" />
                        Generated SQL
                      </span>
                      <ChevronDown size={14} className="group-open:rotate-180 transition-transform" />
                    </summary>
                    <pre className="p-3 text-xs font-mono text-emerald-300 bg-slate-950/70 border-t border-slate-800 overflow-x-auto whitespace-pre">
                      {m.sql}
                    </pre>
                  </details>
                )}

                {/* Chart */}
                {m.chart && <ChartView chart={m.chart} />}

                {/* Table */}
                {m.rows && m.rows.length > 0 && (
                  <details className="group mt-2">
                    <summary className="text-xs text-slate-400 hover:text-slate-300 cursor-pointer select-none">
                      Show raw query results ({m.rows.length} rows)
                    </summary>
                    <ResultTable rows={m.rows} />
                  </details>
                )}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-xs text-indigo-400 animate-pulse bg-indigo-950/30 p-3 rounded-lg border border-indigo-900/50 w-fit">
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
            Analyzing schema, validating query, and running SQL...
          </div>
        )}
        <div ref={bottomRef} />
      </main>

      {/* Input Box */}
      <footer className="pt-2">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
            placeholder="Ask a question (e.g. 'Show total revenue grouped by product category')"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:hover:bg-indigo-600 text-white px-5 rounded-xl flex items-center justify-center transition-colors"
          >
            <Send size={18} />
          </button>
        </form>
      </footer>
    </div>
  );
}