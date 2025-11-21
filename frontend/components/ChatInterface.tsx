'use client'

import { useState, useRef, useEffect } from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  toolCalls?: Array<{
    tool: string
    arguments: Record<string, any>
    result: string
  }>
  metadata?: Record<string, any>
}

const EXAMPLE_QUERIES = [
  "What is Apple's current stock price?",
  "What is Apple's revenue from their latest SEC filing?",
  "What is Tesla's stock price and summarize their risk factors?",
  "Compare Microsoft and Apple's market cap",
]

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage],
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to get response')
      }

      const assistantMessage = await response.json()
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error: any) {
      console.error('Chat error:', error)
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'assistant',
          content: `Error: ${error.message}. Please try again.`,
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleExampleClick = (query: string) => {
    setInput(query)
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-4 py-4 shadow-sm">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-slate-900">Stock Research Assistant</h1>
          <p className="text-sm text-slate-600 mt-1">
            AI-powered stock analysis with live data and SEC filings
          </p>
        </div>
      </header>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-slate-700 mb-2">
                Welcome! Ask me anything about stocks
              </h2>
              <p className="text-slate-500 mb-6">
                I can analyze SEC filings, get live stock prices, and answer complex financial questions.
              </p>

              {/* Example Queries */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
                {EXAMPLE_QUERIES.map((query, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleExampleClick(query)}
                    className="text-left p-4 bg-white border border-slate-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all text-sm text-slate-700"
                  >
                    <span className="text-blue-600 font-medium">→</span> {query}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-slate-200 text-slate-900'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>

                {/* Tool Calls Display */}
                {message.toolCalls && message.toolCalls.length > 0 && (
                  <details className="mt-3 text-sm">
                    <summary className="cursor-pointer text-slate-600 hover:text-slate-800 font-medium">
                      🔧 Tools used ({message.toolCalls.length})
                    </summary>
                    <div className="mt-2 space-y-2 border-t border-slate-200 pt-2">
                      {message.toolCalls.map((tool, idx) => (
                        <div key={idx} className="bg-slate-50 p-2 rounded text-xs">
                          <div className="font-semibold text-slate-700">{tool.tool}</div>
                          <div className="text-slate-500 mt-1">
                            Args: {JSON.stringify(tool.arguments)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </details>
                )}

                {/* Metadata */}
                {message.metadata && (
                  <div className="mt-2 text-xs text-slate-500">
                    Model: {message.metadata.model} • Iterations: {message.metadata.iterations}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-slate-200 rounded-lg px-4 py-3">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce delay-100" />
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce delay-200" />
                  <span className="text-sm text-slate-600 ml-2">Thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Form */}
      <div className="border-t border-slate-200 bg-white px-4 py-4 shadow-lg">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex space-x-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about stocks, SEC filings, or company financials..."
              className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-900 placeholder-slate-400"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
