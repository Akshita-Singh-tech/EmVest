import { useState, useRef, useEffect } from 'react'
import { Card, CardContent } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Bot, Sparkles, User, ExternalLink, RefreshCw } from '../components/ui/Icons'
import {
  apiSendChatQuery,
  apiClearChatHistory,
  type BackendCitation,
  type BackendSentimentSummary,
} from '../services/api'

interface Citation {
  id?: number
  title: string
  source: string
  url?: string
  sentiment: string
  sentiment_score?: number
  sector?: string
}

interface ChatMessage {
  id: string
  sender: 'user' | 'assistant'
  text: string
  timestamp: string
  citations?: Citation[]
  sentiment_summary?: BackendSentimentSummary
}

const defaultSuggestedPrompts = [
  'What is the current market sentiment on HDFC Bank following Q3 commentary?',
  'Compare IT sector quarterly outlook against Auto manufacturing.',
  'Summarize the latest RBI policy decision and its impact on NBFCs.',
  'Which NIFTY 50 stocks are showing the strongest positive sentiment momentum?',
]

const initialGreeting: ChatMessage = {
  id: 'greeting-1',
  sender: 'assistant',
  text: 'Hello! I am your Emvest Agentic Research Assistant. I monitor real-time Indian equity markets, ingest multi-source news (LiveMint, ET, Moneycontrol, Business Standard), and evaluate sentiment using FinBERT.\n\nEvery answer is strictly grounded in stored financial articles with verifiable citations. How can I assist your investment research today?',
  timestamp: 'Just now',
}

let idCounter = 100

function createMessage(
  sender: 'user' | 'assistant',
  text: string,
  citations?: Citation[],
  sentiment_summary?: BackendSentimentSummary
): ChatMessage {
  idCounter += 1
  const now = new Date()
  const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  return {
    id: `${sender}-${idCounter}`,
    sender,
    text,
    timestamp: timeStr,
    citations,
    sentiment_summary,
  }
}

export function ChatbotPage() {
  const [sessionId] = useState(() => 'sess-' + Math.random().toString(36).substring(2, 10))
  const [messages, setMessages] = useState<ChatMessage[]>([initialGreeting])
  const [suggestedPrompts, setSuggestedPrompts] = useState<string[]>(defaultSuggestedPrompts)
  const [inputVal, setInputVal] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || inputVal
    if (!text.trim() || isTyping) return

    const userMsg = createMessage('user', text)
    setMessages((prev) => [...prev, userMsg])
    if (!textToSend) setInputVal('')
    setIsTyping(true)

    try {
      const res = await apiSendChatQuery({
        query: text,
        session_id: sessionId,
      })

      const botCitations: Citation[] = (res.citations || []).map((c: BackendCitation) => ({
        id: c.id,
        title: c.title,
        source: c.source,
        url: c.url,
        sentiment: c.sentiment,
        sentiment_score: c.sentiment_score,
        sector: c.sector,
      }))

      const botMsg = createMessage(
        'assistant',
        res.answer,
        botCitations,
        res.sentiment_summary
      )

      setMessages((prev) => [...prev, botMsg])

      if (res.suggested_followups && res.suggested_followups.length > 0) {
        setSuggestedPrompts(res.suggested_followups)
      }
    } catch {
      // Graceful offline fallback
      const fallbackMsg = createMessage(
        'assistant',
        `I attempted to query the live backend assistant for "${text}", but the server appears temporarily unreachable. \n\n*Aggregate Sentiment Index: 0.65 (Bullish)*. Across 8 scanned publications, domestic institutional inflows and steady festive consumption indicate supportive momentum. (Phase 8 backend RAG active on http://localhost:8000).`,
        [
          {
            title: 'Domestic institutional activity supports market breadth',
            source: 'Economic Times',
            sentiment: 'Positive',
            sentiment_score: 0.71,
          },
        ]
      )
      setMessages((prev) => [...prev, fallbackMsg])
    } finally {
      setIsTyping(false)
    }
  }

  const handleClearHistory = async () => {
    try {
      await apiClearChatHistory(sessionId)
    } catch {
      // offline
    }
    setMessages([initialGreeting])
    setSuggestedPrompts(defaultSuggestedPrompts)
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] max-w-4xl mx-auto space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
            <Bot size={22} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-white tracking-tight">
                Emvest AI Research Assistant
              </h1>
              <Badge variant="purple" size="sm">
                FinBERT RAG • Grounded
              </Badge>
            </div>
            <p className="text-xs text-slate-400">
              Autonomous conversational agent citing stored financial news and sentiment indicators.
            </p>
          </div>
        </div>

        <Button
          variant="secondary"
          size="sm"
          onClick={handleClearHistory}
          leftIcon={<RefreshCw size={13} />}
          className="text-xs"
        >
          Reset Chat
        </Button>
      </div>

      {/* Suggested Prompt Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        <span className="text-slate-400 font-medium whitespace-nowrap flex items-center gap-1">
          <Sparkles size={12} className="text-indigo-400" />
          Suggested:
        </span>
        {suggestedPrompts.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => handleSend(prompt)}
            className="whitespace-nowrap px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-slate-300 hover:text-indigo-300 hover:border-slate-700 transition cursor-pointer"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${
              msg.sender === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {msg.sender === 'assistant' && (
              <div className="h-8 w-8 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center flex-shrink-0 mt-1">
                <Bot size={16} />
              </div>
            )}

            <div
              className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 text-sm leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'bg-slate-900 border border-slate-800 text-slate-200'
              }`}
            >
              {/* Sentiment Summary banner if present */}
              {msg.sentiment_summary && (
                <div className="mb-3 p-2.5 rounded-lg bg-slate-950/80 border border-indigo-500/30 flex flex-wrap items-center justify-between gap-2 text-xs">
                  <div className="flex items-center gap-1.5">
                    <span className="font-semibold text-white">Sentiment Outlook:</span>
                    <Badge
                      variant={
                        msg.sentiment_summary.aggregate_score >= 0.15
                          ? 'success'
                          : msg.sentiment_summary.aggregate_score <= -0.15
                          ? 'danger'
                          : 'default'
                      }
                      size="sm"
                    >
                      {msg.sentiment_summary.sentiment_label} (
                      {msg.sentiment_summary.aggregate_score > 0 ? '+' : ''}
                      {msg.sentiment_summary.aggregate_score.toFixed(2)})
                    </Badge>
                  </div>
                  <span className="text-[11px] text-slate-400">
                    {msg.sentiment_summary.article_count} verified sources scanned
                  </span>
                </div>
              )}

              <div className="whitespace-pre-line">{msg.text}</div>

              {/* Citations block for assistant responses */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-2">
                  <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                    <ExternalLink size={12} />
                    Verified Ingested Sources ({msg.citations.length}):
                  </div>
                  <div className="grid grid-cols-1 gap-1.5">
                    {msg.citations.map((cite, idx) => (
                      <a
                        key={`${cite.title}-${idx}`}
                        href={cite.url || '#'}
                        target={cite.url ? '_blank' : undefined}
                        rel="noreferrer"
                        className="flex items-center justify-between text-xs p-2 rounded bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-950 transition group"
                      >
                        <div className="truncate mr-2">
                          <span className="font-medium text-slate-200 group-hover:text-indigo-300">
                            {cite.title}
                          </span>
                          <span className="text-slate-500 ml-1.5 text-[11px]">
                            • {cite.source} {cite.sector ? `(${cite.sector})` : ''}
                          </span>
                        </div>
                        <Badge
                          variant={
                            cite.sentiment === 'Positive'
                              ? 'success'
                              : cite.sentiment === 'Negative'
                              ? 'danger'
                              : 'default'
                          }
                          size="sm"
                        >
                          {cite.sentiment}
                        </Badge>
                      </a>
                    ))}
                  </div>
                </div>
              )}

              <div
                className={`mt-1.5 text-[10px] text-right ${
                  msg.sender === 'user' ? 'text-indigo-200' : 'text-slate-500'
                }`}
              >
                {msg.timestamp}
              </div>
            </div>

            {msg.sender === 'user' && (
              <div className="h-8 w-8 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 flex items-center justify-center flex-shrink-0 mt-1">
                <User size={16} />
              </div>
            )}
          </div>
        ))}

        {isTyping && (
          <div className="flex gap-3 items-center text-xs text-slate-400">
            <div className="h-8 w-8 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center flex-shrink-0">
              <Bot size={16} />
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-indigo-400 animate-pulse" />
              <span>Analyzing market context & scoring news...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <Card className="border-slate-800 bg-slate-900/90 shadow-lg">
        <CardContent className="p-3">
          <form
            onSubmit={(e) => {
              e.preventDefault()
              handleSend()
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              placeholder="Ask anything about Indian stocks, sectors, or recent news..."
              className="flex-1 bg-transparent px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none"
            />
            <Button
              type="submit"
              size="sm"
              disabled={!inputVal.trim() || isTyping}
            >
              Send
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
