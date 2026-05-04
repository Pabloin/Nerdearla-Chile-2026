// App.jsx — ShopMind frontend
import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import AgentPanel from "./AgentPanel";

const GATEWAY_URL = import.meta.env.VITE_AGENT_URL || "http://localhost:8000";

const TOOL_TO_AGENT = {
  web_search: "search",
  price_compare: "price",
  fetch_reviews: "reviews",
  user_memory: "budget",
};

const INITIAL_AGENTS = {
  search:  { label: "Search Agent",  tool: "web_search",    status: "idle", result: null },
  price:   { label: "Price Agent",   tool: "price_compare", status: "idle", result: null },
  reviews: { label: "Review Agent",  tool: "fetch_reviews", status: "idle", result: null },
  budget:  { label: "Budget Agent",  tool: "user_memory",   status: "idle", result: null },
};

export default function App() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hola! Soy ShopMind\nCuentame que producto estas buscando y tu presupuesto, y mis agentes encontraran la mejor opcion para ti." }
  ]);
  const [input, setInput]     = useState("");
  const [loading, setLoading] = useState(false);
  const [agents, setAgents]   = useState(INITIAL_AGENTS);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const activateAgents = () => {
    const keys = Object.keys(INITIAL_AGENTS);
    keys.forEach((key, i) => {
      setTimeout(() => {
        setAgents(prev => ({
          ...prev,
          [key]: { ...prev[key], status: "working" }
        }));
      }, i * 300);
    });
  };

  const completeAgentsWithResults = (toolResults) => {
    setAgents(prev => {
      const next = { ...prev };
      // Mark agents that were actually called as "done" with their results
      Object.entries(toolResults || {}).forEach(([toolName, data]) => {
        const agentKey = TOOL_TO_AGENT[toolName];
        if (agentKey && next[agentKey]) {
          next[agentKey] = { ...next[agentKey], status: "done", result: data };
        }
      });
      // Mark agents that weren't called as idle
      Object.keys(next).forEach(k => {
        if (next[k].status === "working") {
          next[k] = { ...next[k], status: "idle" };
        }
      });
      return next;
    });
  };

  const resetAgents = () => setAgents(INITIAL_AGENTS);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput("");
    setLoading(true);
    resetAgents();

    setMessages(prev => [...prev, { role: "user", text: userMsg }]);
    activateAgents();
    setMessages(prev => [...prev, { role: "assistant", text: "", streaming: true }]);

    try {
      const res = await fetch(`${GATEWAY_URL}/invoke`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg, user_id: "nerdearla-demo" }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      const assistantText = data.text || data.error || "Sin respuesta.";

      completeAgentsWithResults(data.tool_results || {});
      setMessages(prev => {
        const next = [...prev];
        next[next.length - 1] = { role: "assistant", text: assistantText, streaming: false };
        return next;
      });

    } catch (err) {
      setMessages(prev => {
        const next = [...prev];
        next[next.length - 1] = {
          role: "assistant",
          text: "Error conectando con los agentes. Verifica que el backend este corriendo.",
          streaming: false,
        };
        return next;
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={{ position: "relative", width: "100%", background: "#0a0a10" }}>
        <img src="/shopmind_header_wider.png" alt="ShopMind" style={{ width: "100%", display: "block" }} />
        <div style={{
          position: "absolute", left: 24, top: "50%", transform: "translateY(-50%)",
          display: "flex", alignItems: "center", gap: 10,
        }}>
          <a href="https://www.awsnerds.dev/" target="_blank" rel="noopener noreferrer" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none", border: "none", outline: "none" }}>
            <img src="/aws_logo.png" alt="AWS" style={{ height: 32 }} />
            <span style={{ color: "#FF9900", fontWeight: "bold", fontSize: 18 }}>x</span>
            <img src="/nerdearla_logo.png" alt="Nerdearla" style={{ height: 32 }} />
          </a>
        </div>
      </div>

      <div style={styles.main}>
        <div style={styles.chatCol}>
          <div style={styles.messages}>
            {messages.map((msg, i) => (
              <div key={i} style={msg.role === "user" ? styles.userMsg : styles.assistantMsg}>
                <div style={msg.role === "user" ? styles.userBubble : styles.assistantBubble}>
                  {msg.role === "assistant" && msg.text ? (
                    <ReactMarkdown
                      components={{
                        a: ({ href, children }) => (
                          <a href={href} target="_blank" rel="noopener noreferrer" style={{
                            color: "#0E0E12", background: "#7EE8A2", padding: "3px 10px",
                            borderRadius: 3, textDecoration: "none", fontSize: "0.7rem",
                            fontWeight: 600, display: "inline-block", marginTop: 4,
                          }}>
                            {children}
                          </a>
                        ),
                        strong: ({ children }) => (
                          <strong style={{ color: "#F7C59F" }}>{children}</strong>
                        ),
                        li: ({ children }) => (
                          <li style={{ marginBottom: "0.5rem", listStyle: "none" }}>{children}</li>
                        ),
                        ul: ({ children }) => (
                          <ul style={{ paddingLeft: "0.5rem", margin: "0.3rem 0" }}>{children}</ul>
                        ),
                        ol: ({ children }) => (
                          <ol style={{ paddingLeft: "1rem", margin: "0.3rem 0" }}>{children}</ol>
                        ),
                        p: ({ children }) => (
                          <p style={{ margin: "0.3rem 0" }}>{children}</p>
                        ),
                        h1: ({ children }) => <div style={{ fontSize: "0.9rem", fontWeight: 700, margin: "0.5rem 0 0.3rem" }}>{children}</div>,
                        h2: ({ children }) => <div style={{ fontSize: "0.85rem", fontWeight: 700, margin: "0.5rem 0 0.3rem" }}>{children}</div>,
                        h3: ({ children }) => <div style={{ fontSize: "0.8rem", fontWeight: 700, margin: "0.4rem 0 0.2rem" }}>{children}</div>,
                      }}
                    >
                      {msg.text}
                    </ReactMarkdown>
                  ) : (
                    msg.text || (msg.streaming ? "..." : "")
                  )}
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          <div style={styles.inputRow}>
            <input
              style={styles.input}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && sendMessage()}
              placeholder="Ej: Quiero auriculares, presupuesto $80, para estudiar..."
              disabled={loading}
            />
            <button style={styles.btn} onClick={sendMessage} disabled={loading}>
              {loading ? "..." : ">"}
            </button>
          </div>
        </div>

        <AgentPanel agents={agents} />
      </div>
    </div>
  );
}

const styles = {
  container: { fontFamily: "'DM Mono', monospace", background: "#0E0E12", color: "#E8E8F0", minHeight: "100vh", display: "flex", flexDirection: "column" },
  header:    { background: "#16161C", borderBottom: "1px solid #222", padding: "0.8rem 2rem", display: "flex", alignItems: "center", gap: "1.2rem" },
  logo:      { fontWeight: 700, fontSize: "1.1rem" },
  powered:   { fontSize: "0.65rem", color: "#5A5A72" },
  liveDot:   { width: 8, height: 8, borderRadius: "50%", background: "#7EE8A2", marginLeft: "auto", animation: "pulse 1.5s infinite" },
  main:      { display: "flex", flex: 1, overflow: "hidden", gap: 0 },
  chatCol:   { flex: 1, display: "flex", flexDirection: "column", borderRight: "1px solid #222" },
  messages:  { flex: 1, overflowY: "auto", padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1rem" },
  userMsg:       { display: "flex", justifyContent: "flex-end", gap: "0.6rem", alignItems: "flex-start" },
  assistantMsg:  { display: "flex", gap: "0.6rem", alignItems: "flex-start" },
  userBubble:      { background: "#1E1E26", border: "1px solid #2A2A3A", padding: "0.7rem 1rem", borderRadius: 4, maxWidth: "70%", fontSize: "0.8rem", lineHeight: 1.6, whiteSpace: "pre-wrap" },
  assistantBubble: { background: "rgba(126,232,162,0.06)", border: "1px solid rgba(126,232,162,0.15)", padding: "0.7rem 1rem", borderRadius: 4, maxWidth: "75%", fontSize: "0.8rem", lineHeight: 1.5, color: "#C5F0D3" },
  inputRow:  { padding: "1rem", borderTop: "1px solid #222", display: "flex", gap: "0.5rem" },
  input:     { flex: 1, background: "#16161C", border: "1px solid #2A2A3A", color: "#E8E8F0", padding: "0.7rem 1rem", fontSize: "0.8rem", outline: "none", fontFamily: "inherit", borderRadius: 4 },
  btn:       { background: "#7EE8A2", color: "#000", border: "none", padding: "0.7rem 1.2rem", cursor: "pointer", fontWeight: 700, fontSize: "1rem", borderRadius: 4 },
};
