// AgentPanel.jsx — Real-time agent panel with clickable tool results
import { useState } from "react";

const STATUS_COLORS = {
  idle:    { border: "#2A2A3A", text: "#5A5A72", bg: "transparent" },
  working: { border: "#7EE8A2", text: "#7EE8A2", bg: "rgba(126,232,162,0.05)" },
  done:    { border: "#F7C59F", text: "#F7C59F", bg: "rgba(247,197,159,0.05)" },
};

const STATUS_LABELS = {
  idle:    "En espera",
  working: "Trabajando...",
  done:    "Listo",
};

const AGENT_ICONS = {
  search: ">>",
  price: "$",
  reviews: "*",
  budget: "#",
};

function formatCLP(n) {
  return "$" + Number(n).toLocaleString("es-CL");
}

function ToolResultDetail({ toolName, data, onClose }) {
  if (!data) return null;
  const output = data.output;
  const input = data.input;

  return (
    <div style={{
      position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
      background: "rgba(0,0,0,0.85)", zIndex: 1000,
      display: "flex", justifyContent: "center", alignItems: "center",
      padding: "2rem",
    }} onClick={onClose}>
      <div style={{
        background: "#16161C", border: "1px solid #2A2A3A",
        borderRadius: 8, maxWidth: 700, width: "100%", maxHeight: "80vh",
        overflow: "auto", padding: "1.5rem",
      }} onClick={e => e.stopPropagation()}>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "1rem" }}>
          <span style={{ fontSize: "0.9rem", fontWeight: 700, color: "#F7C59F" }}>
            MCP Tool: {toolName}
          </span>
          <button onClick={onClose} style={{
            background: "none", border: "none", color: "#5A5A72",
            cursor: "pointer", fontSize: "1.2rem",
          }}>X</button>
        </div>

        {input && (
          <div style={{ marginBottom: "1rem" }}>
            <div style={{ fontSize: "0.65rem", color: "#5A5A72", marginBottom: "0.3rem" }}>INPUT</div>
            <div style={{ fontSize: "0.7rem", color: "#9B8BFF", background: "#0E0E12", padding: "0.5rem", borderRadius: 4 }}>
              {Object.entries(input).map(([k, v]) => (
                <div key={k}>{k}: {JSON.stringify(v)}</div>
              ))}
            </div>
          </div>
        )}

        <div style={{ fontSize: "0.65rem", color: "#5A5A72", marginBottom: "0.3rem" }}>OUTPUT</div>

        {/* Render products as cards if it's an array */}
        {Array.isArray(output) ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
            {output.map((item, i) => (
              <div key={i} style={{
                background: "#0E0E12", border: "1px solid #2A2A3A",
                borderRadius: 4, padding: "0.8rem",
              }}>
                <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "#C5F0D3", marginBottom: "0.3rem" }}>
                  {item.title || item.product || `Item ${i + 1}`}
                </div>
                {item.brand && (
                  <div style={{ fontSize: "0.65rem", color: "#9B8BFF" }}>{item.brand}</div>
                )}
                <div style={{ display: "flex", gap: "1rem", marginTop: "0.3rem", flexWrap: "wrap" }}>
                  {item.price_clp && (
                    <span style={{ fontSize: "0.7rem", color: "#7EE8A2", fontWeight: 700 }}>
                      {formatCLP(item.price_clp)}
                    </span>
                  )}
                  {item.price_usd && (
                    <span style={{ fontSize: "0.65rem", color: "#5A5A72" }}>
                      USD ${item.price_usd}
                    </span>
                  )}
                  {item.rating && (
                    <span style={{ fontSize: "0.65rem", color: "#F7C59F" }}>
                      Rating: {item.rating}
                    </span>
                  )}
                  {item.review_count && (
                    <span style={{ fontSize: "0.65rem", color: "#5A5A72" }}>
                      ({item.review_count} reviews)
                    </span>
                  )}
                </div>
                {item.url && (
                  <a href={item.url} target="_blank" rel="noopener noreferrer" style={{
                    fontSize: "0.6rem", color: "#7EE8A2", textDecoration: "none",
                    display: "block", marginTop: "0.3rem",
                  }}>
                    {"Ver en MercadoLibre >"}
                  </a>
                )}
                {item.features && (
                  <div style={{ fontSize: "0.6rem", color: "#5A5A72", marginTop: "0.3rem" }}>
                    {item.features.join(" | ")}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : typeof output === "object" ? (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
            {output.pros && (
              <div>
                <div style={{ fontSize: "0.65rem", color: "#7EE8A2", marginBottom: "0.2rem" }}>Pros:</div>
                {output.pros.map((p, i) => (
                  <div key={i} style={{ fontSize: "0.65rem", color: "#C5F0D3", paddingLeft: "0.5rem" }}>+ {p}</div>
                ))}
              </div>
            )}
            {output.cons && (
              <div style={{ marginTop: "0.3rem" }}>
                <div style={{ fontSize: "0.65rem", color: "#F7C59F", marginBottom: "0.2rem" }}>Cons:</div>
                {output.cons.map((c, i) => (
                  <div key={i} style={{ fontSize: "0.65rem", color: "#E8E8F0", paddingLeft: "0.5rem" }}>- {c}</div>
                ))}
              </div>
            )}
            {!output.pros && !output.cons && (
              <pre style={{ fontSize: "0.6rem", color: "#E8E8F0", whiteSpace: "pre-wrap" }}>
                {JSON.stringify(output, null, 2)}
              </pre>
            )}
          </div>
        ) : (
          <pre style={{ fontSize: "0.6rem", color: "#E8E8F0", whiteSpace: "pre-wrap" }}>
            {JSON.stringify(output, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}

function AgentCard({ agentKey, agent, onClick }) {
  const colors = STATUS_COLORS[agent.status];
  const isWorking = agent.status === "working";
  const isDone = agent.status === "done";
  const hasResult = isDone && agent.result;
  const icon = AGENT_ICONS[agentKey] || ">";

  const resultCount = hasResult && Array.isArray(agent.result.output)
    ? agent.result.output.length + " resultados"
    : null;

  return (
    <div
      onClick={() => hasResult && onClick()}
      style={{
        border: `1px solid ${colors.border}`,
        background: colors.bg,
        padding: "1rem",
        transition: "all 0.3s ease",
        position: "relative",
        overflow: "hidden",
        cursor: hasResult ? "pointer" : "default",
      }}
    >
      {isWorking && (
        <div style={{
          position: "absolute", top: 0, left: 0, right: 0, height: 2,
          background: colors.border, animation: "scan 1.5s infinite",
          opacity: 0.8,
        }} />
      )}

      <div style={{ fontSize: "0.75rem", fontWeight: 600, color: colors.text, marginBottom: "0.4rem" }}>
        {icon} {agent.label}
      </div>

      <div style={{ fontSize: "0.6rem", color: "#5A5A72", marginBottom: "0.5rem" }}>
        MCP Tool: <span style={{ color: "#9B8BFF" }}>{agent.tool}</span>
      </div>

      <div style={{
        fontSize: "0.65rem",
        color: colors.text,
        opacity: agent.status === "idle" ? 0.4 : 1,
        fontStyle: isWorking ? "italic" : "normal",
        minHeight: "1rem",
      }}>
        {isWorking ? (
          <span>{STATUS_LABELS.working} <span style={{ animation: "blink 1s infinite" }}>|</span></span>
        ) : isDone ? (
          <span>
            {STATUS_LABELS.done}
            {resultCount && <span style={{ color: "#7EE8A2", marginLeft: "0.5rem" }}>{resultCount}</span>}
            {hasResult && <span style={{ color: "#5A5A72", marginLeft: "0.5rem" }}>(click para ver)</span>}
          </span>
        ) : (
          STATUS_LABELS[agent.status]
        )}
      </div>
    </div>
  );
}

export default function AgentPanel({ agents }) {
  const [selectedAgent, setSelectedAgent] = useState(null);
  const anyActive = Object.values(agents).some(a => a.status !== "idle");

  return (
    <div style={{
      width: 300,
      background: "#0E0E12",
      borderLeft: "1px solid #222",
      display: "flex",
      flexDirection: "column",
      flexShrink: 0,
    }}>
      <div style={{
        padding: "0.8rem 1rem",
        borderBottom: "1px solid #222",
        display: "flex",
        alignItems: "center",
        gap: "0.5rem",
      }}>
        <span style={{ fontSize: "0.6rem", color: "#5A5A72", letterSpacing: "0.1em", textTransform: "uppercase" }}>
          Agentes en vivo
        </span>
        {anyActive && (
          <span style={{
            width: 6, height: 6, borderRadius: "50%",
            background: "#7EE8A2", marginLeft: "auto",
            animation: "pulse 1.5s infinite",
          }} />
        )}
      </div>

      <div style={{ padding: "0.8rem", display: "flex", flexDirection: "column", gap: "0.6rem" }}>
        {Object.entries(agents).map(([key, agent]) => (
          <AgentCard
            key={key}
            agentKey={key}
            agent={agent}
            onClick={() => setSelectedAgent({ key, tool: agent.tool, data: agent.result })}
          />
        ))}
      </div>

      <div style={{
        margin: "0 0.8rem",
        padding: "0.8rem",
        border: "1px solid #222",
        fontSize: "0.6rem",
        color: "#5A5A72",
        lineHeight: 1.6,
      }}>
        Los agentes usan <span style={{ color: "#7EE8A2" }}>MCP tools</span> reales.
        Click en un agente completado para ver los datos que retorno.
      </div>

      <div style={{
        marginTop: "auto",
        padding: "0.8rem 1rem",
        borderTop: "1px solid #222",
        fontSize: "0.55rem",
        color: "#2A2A3A",
        lineHeight: 1.6,
      }}>
        Amazon Bedrock AgentCore<br/>
        Strands Agents + FastMCP<br/>
        Datos reales de MercadoLibre Chile
      </div>

      {selectedAgent && (
        <ToolResultDetail
          toolName={selectedAgent.tool}
          data={selectedAgent.data}
          onClose={() => setSelectedAgent(null)}
        />
      )}

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(0.85)} }
        @keyframes scan  { 0%{opacity:0.8} 50%{opacity:0.2} 100%{opacity:0.8} }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
      `}</style>
    </div>
  );
}
