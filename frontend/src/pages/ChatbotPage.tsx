import { useState } from 'react'
import { Card, CardContent } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Bot, Sparkles, User, ExternalLink } from '../components/ui/Icons'

interface ChatMessage {
  id: string
  sender: 'user' | 'assistant'
  text: string
  timestamp: string
  citations?: Array<{ title: string; source: string; sentiment: string }>
}

const suggestedPrompts = [
  'What is the current market sentiment on HDFC Bank following Q3 commentary?',
  'Compare IT sector quarterly outlook against Auto manufacturing.',
  'Summarize the latest RBI policy decision and its impact on NBFCs.',
  'Which NIFTY 50 stocks are showing the strongest positive sentiment momentum?',
]

const initialMessages: ChatMessage[] = [
  {
    id: 'msg-1',
    sender: 'assistant',
    text: 'Hello! I am your Emvest Agentic Research Assistant. I monitor real-time Indian equity markets, ingest multi-source news, and evaluate sentiment using FinBERT. How can I assist your market research today?',
    timestamp: 'Just now',
  },
  {
    id: 'msg-2',
    sender: 'user',
    text: 'What is the outlook for Reliance Industries based on the recent retail and energy news?',
    timestamp: 'Just now',
  },
  {
    id: 'msg-3',
    sender: 'assistant',
    text: 'Based on our latest ingestion of 14 articles across LiveMint, Economic Times, and Reuters, Reliance Industries (RELIANCE) exhibits a **Moderately Bullish (+0.72)** sentiment score.\n\n**Key Takeaways:**\n- **Retail Omnichannel Push:** Reliance Retail added 120 stores with expanding operating EBITDA margins.\n- **Energy Refining Spread:** Volatility in Brent crude has been partially hedged with delayed voluntary OPEC+ production unwinding.\n- **Institutional Consensus:** Target valuations maintain an overweight bias with key triggers around upcoming digital retail monetization milestones.',
    timestamp: 'Just now',
    citations: [
      { title: 'Reliance Retail expands store network by 120 outlets', source: 'Business Standard', sentiment: '+0.69' },
      { title: 'Brent crude near $74/bbl amidst OPEC+ voluntary curbs', source: 'Reuters', sentiment: '0.04' },
    ],
  },
]

let idCounter = 100

function createMessage(
  sender: 'user' | 'assistant',
  text: string,
  citations?: Array<{ title: string; source: string; sentiment: string }>
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
  }
}

export function ChatbotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages)
  const [inputVal, setInputVal] = useState('')
  const [isTyping, setIsTyping] = useState(false)

  const handleSend = (textToSend?: string) => {
    const text = textToSend || inputVal
    if (!text.trim()) return

    const userMsg = createMessage('user', text)

    setMessages((prev) => [...prev, userMsg])
    if (!textToSend) setInputVal('')
    setIsTyping(true)

    // Simulate Agent response (until Phase 8 backend LLM service is connected)
    setTimeout(() => {
      const botMsg = createMessage(
        'assistant',
        `I have analyzed the recent news feed regarding "${text}". \n\n*Aggregate Sentiment Index: 0.65 (Bullish)*. Across 8 scanned publications, domestic institutional inflows and steady festive consumption indicate supportive momentum. (Note: Full LLM RAG engine activates in Phase 8).`,
        [
          { title: 'Domestic institutional activity supports market breadth', source: 'Economic Times', sentiment: '+0.71' },
        ]
      )
      setMessages((prev) => [...prev, botMsg])
      setIsTyping(false)
    }, 700)
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
                FinBERT RAG
              </Badge>
            </div>
            <p className="text-xs text-slate-400">
              Autonomous conversational agent citing stored financial news and sentiment indicators.
            </p>
          </div>
        </div>
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
              <div className="whitespace-pre-line">{msg.text}</div>

              {/* Citations block for assistant responses */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-800/80 space-y-1.5">
                  <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                    <ExternalLink size={12} />
                    Verified Ingested Sources:
                  </div>
                  {msg.citations.map((cite) => (
                    <div
                      key={cite.title}
                      className="flex items-center justify-between text-xs p-2 rounded bg-slate-950/60 border border-slate-800"
                    >
                      <span className="text-slate-300 truncate mr-2">
                        {cite.title} ({cite.source})
                      </span>
                      <Badge variant="success" size="sm">
                        {cite.sentiment}
                      </Badge>
                    </div>
                  ))}
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
