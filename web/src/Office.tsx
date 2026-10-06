import { useRef, useState } from "react";
import { Avatar, Badge, Icon, colors, labels } from "./components";
import type { Agent } from "./types";

const slots: Record<string, [number, number]> = {
  elena: [325, 245],
  lucien: [490, 325],
  elodie: [645, 245],
  nora: [165, 325],
  marc: [325, 405],
  maya: [645, 405],
  sophie: [490, 165],
  kai: [805, 325],
};
const coffee: Record<string, [number, number]> = {
  elena: [430, 430],
  lucien: [500, 465],
  elodie: [570, 500],
  nora: [640, 465],
  marc: [500, 405],
  maya: [570, 440],
  sophie: [640, 405],
  kai: [710, 440],
};
function Desk({ x, y, color }: { x: number; y: number; color: string }) {
  return (
    <g transform={`translate(${x},${y})`} shapeRendering="crispEdges">
      <path
        d="m-54 0 54-27 54 27-54 27z"
        fill="#c7ad85"
        stroke="#ac946f"
        strokeWidth="2"
      />
      <path d="M-54 0v8L0 35V27z" fill="#aa8a61" />
      <path d="M0 27v8L54 8V0z" fill="#b89a72" />
      <path d="M-42 12v30l5 3V15M39 13v30l5-3V10" fill="#8c775b" />
      <path d="m-19-12 23-12 19 10-23 12z" fill="#6b7770" />
      <path d="M-19-12v-25l23-12v25z" fill="#303e37" />
      <path d="m-15-15 15-8v-18l-15 8z" fill={color} />
      <path d="m0 9 15-8 10 5-15 8z" fill="#e9dfce" />
      <path d="m26-2 7-4 5 3-7 4z" fill="#f6eee0" />
      <path d="M31-4v-8l6-3v9z" fill="#e8ded0" />
    </g>
  );
}
function Actor({
  x,
  y,
  color,
  name,
  state,
  onSelect,
}: {
  x: number;
  y: number;
  color: string;
  name: string;
  state: string;
  onSelect: () => void;
}) {
  return (
    <g
      className="office-actor"
      role="button"
      tabIndex={0}
      aria-label={`${name} · ${state}`}
      onClick={onSelect}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect();
        }
      }}
      transform={`translate(${x},${y})`}
    >
      <title>{name}</title>
      <ellipse cx="0" cy="6" rx="14" ry="7" fill="#39453a" opacity=".13" />
      <g className="actor-sprite" shapeRendering="crispEdges">
        <path d="M-8-9h6V5h-6zm10 0h6V5H2z" fill="#36443d" />
        <path
          d="M-12-27h24v18h-24zM-15-25h4v15h-4zm26 0h4v15h-4z"
          fill={color}
        />
        <path d="M-7-44H7v5h4v13h-22v-13h4z" fill="#3c332d" />
        <path d="M-7-37H7v13H-7z" fill="#e6be96" />
        <path d="M-5-34h2v3h-2zm8 0h2v3H3z" fill="#343630" />
        <path d="M-3-24h6v4h-6z" fill="#ead6b7" />
      </g>
      <circle
        cx="14"
        cy="-41"
        r="4"
        fill={
          state === "working"
            ? "#668570"
            : state === "idle"
              ? "#afa384"
              : state === "unknown"
                ? "#90958e"
                : "#bf9550"
        }
        stroke="#fff9eb"
        strokeWidth="2"
      />
      <rect
        x="-38"
        y="11"
        width="76"
        height="21"
        rx="4"
        fill="#fffaf0"
        opacity=".96"
      />
      <text
        x="0"
        y="25"
        textAnchor="middle"
        fill="#465249"
        fontSize="11"
        fontFamily="sans-serif"
      >
        {name}
      </text>
    </g>
  );
}
export default function Office({
  agents,
  onLaunch,
  compact = false,
  stale = false,
}: {
  agents: Agent[];
  onLaunch: () => void;
  compact?: boolean;
  stale?: boolean;
}) {
  const [zoom, setZoom] = useState(1),
    [pan, setPan] = useState([0, 0]);
  const drag = useRef<{ x: number; y: number; pan: number[] } | null>(null);
  return (
    <div className={`office-container ${compact ? "compact" : ""}`}>
      <div className="office-toolbar">
        <span>
          <i className={`status-dot ${stale ? "warning" : ""}`} />
          {stale
            ? "Aktivität unbekannt · Verbindung prüfen"
            : "Lokales Office"}{" "}
          <span className="muted">/ 8 Agenten</span>
        </span>
        <div className="row">
          <button
            aria-label="Office verkleinern"
            onClick={() => setZoom(Math.max(0.65, zoom - 0.15))}
          >
            −
          </button>
          <span>{Math.round(zoom * 100)}%</span>
          <button
            aria-label="Office vergrößern"
            onClick={() => setZoom(Math.min(1.8, zoom + 0.15))}
          >
            +
          </button>
          <button
            aria-label="Office Ansicht zurücksetzen"
            onClick={() => {
              setZoom(1);
              setPan([0, 0]);
            }}
          >
            ↺
          </button>
        </div>
      </div>
      <svg
        className="office-scene"
        viewBox="0 0 1000 590"
        role="img"
        aria-label="Isometrisches Büro mit acht Arbeitsplätzen, Kaffeezone und Founder"
        onPointerDown={(e) => {
          if ((e.target as Element).closest(".office-actor")) return;
          drag.current = { x: e.clientX, y: e.clientY, pan };
          e.currentTarget.setPointerCapture(e.pointerId);
        }}
        onPointerMove={(e) => {
          if (drag.current)
            setPan([
              drag.current.pan[0] + (e.clientX - drag.current.x),
              drag.current.pan[1] + (e.clientY - drag.current.y),
            ]);
        }}
        onPointerUp={() => {
          drag.current = null;
        }}
      >
        <defs>
          <pattern
            id="floor"
            width="48"
            height="24"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M0 12 24 0 48 12 24 24Z"
              fill="none"
              stroke="#d6ceba"
              strokeWidth=".6"
            />
          </pattern>
          <linearGradient id="roomShade" x2="0" y2="1">
            <stop stopColor="#f0ead8" />
            <stop offset="1" stopColor="#e4dbc4" />
          </linearGradient>
        </defs>
        <g
          transform={`translate(${pan[0]},${pan[1]}) translate(500,295) scale(${zoom}) translate(-500,-295)`}
        >
          <ellipse
            cx="500"
            cy="480"
            rx="355"
            ry="54"
            fill="#bec2b3"
            opacity=".18"
          />
          <path d="m90 315 410-205 410 205-410 205z" fill="#b8ac92" />
          <path d="m90 305 410-205 410 205-410 205z" fill="url(#roomShade)" />
          <path d="m90 305 410-205 410 205-410 205z" fill="url(#floor)" />
          <path d="M90 305v-105L500-5v105z" fill="#e7e4d6" />
          <path d="M500 100V-5l410 205v105z" fill="#d9daca" />
          <path
            d="m95 209 400-200M505 9l400 200"
            stroke="#bdc0b0"
            strokeWidth="4"
          />
          <path
            d="M90 295 500 90l410 205"
            fill="none"
            stroke="#bdc0ae"
            strokeWidth="6"
          />
          <g fill="#b3c6b8" stroke="#9eafa3" strokeWidth="3">
            <path d="M170 199v-48l98-49v48z" />
            <path d="M294 137V89l98-49v48z" />
          </g>
          <path d="M218 126v48M342 64v48" stroke="#edf0e6" strokeWidth="4" />
          <path
            d="m578 90 125 62v40l-125-62z"
            fill="#fff9e7"
            stroke="#bdbea9"
            strokeWidth="3"
          />
          <text
            x="584"
            y="117"
            transform="rotate(27 584 117)"
            fontSize="15"
            fontFamily="Georgia"
            fill="#5c6657"
          >
            AMAUX BOZÉ
          </text>
          <text
            x="745"
            y="206"
            transform="rotate(27 745 206)"
            fontSize="11"
            letterSpacing="2"
            fill="#6d7662"
          >
            COMPANY OS
          </text>
          <g transform="translate(140 265)" shapeRendering="crispEdges">
            <path d="m-16 0 16-8 16 8v16l-16 8-16-8z" fill="#ac9679" />
            <path d="M-4-1v-45H4V0z" fill="#778765" />
            <path
              d="M-22-28h18v-18h-10v-15H0v28h15v-18h12v25H4v14h-26z"
              fill="#829574"
            />
          </g>
          <g transform="translate(865 280)" shapeRendering="crispEdges">
            <path d="m-12 0 12-6 12 6v14l-12 6-12-6z" fill="#aa9274" />
            <path d="M-3-1v-42h6V0z" fill="#697b5f" />
            <path
              d="M-20-20h16v-21H5v10h15v-18H8v-8H-4v-3h-11v25h-5z"
              fill="#859d79"
            />
          </g>
          {Object.entries(slots).map(([id, [x, y]]) => (
            <Desk key={id} x={x} y={y} color={colors[id]} />
          ))}
          <g transform="translate(590 445)">
            <path
              d="m-105 0 105-53 105 53-105 53z"
              fill="#9aa58a"
              opacity=".25"
            />
            <path d="m-45-3 45-23 45 23-45 23z" fill="#bea17b" />
            <path
              d="M0 20v24M-38 0v20M38 0v20"
              stroke="#967a59"
              strokeWidth="5"
            />
            <path d="m-10-5 10-5 10 5-10 5z" fill="#efede1" />
            <text
              x="0"
              y="72"
              textAnchor="middle"
              fill="#839078"
              fontSize="10"
              letterSpacing="2"
            >
              COFFEE & IDEAS
            </text>
          </g>
          {agents.map((a) => {
            const actual = stale ? "unknown" : a.activity.state;
            const [x, y] =
              actual === "idle"
                ? coffee[a.id] || [500, 400]
                : slots[a.id] || [500, 300];
            return (
              <Actor
                key={a.id}
                x={x}
                y={y - 18}
                color={colors[a.id]}
                name={a.name.split(" ")[0]}
                state={actual}
                onSelect={() => {
                  window.location.hash = `/agents/${a.id}`;
                }}
              />
            );
          })}
          <Actor
            x={775}
            y={214}
            color={colors.amancio}
            name="Amancio ↗"
            state="idle"
            onSelect={onLaunch}
          />
          <path d="m755 243 20-10 20 10-20 10z" fill="#b8a176" opacity=".2" />
          <text x="775" y="258" fontSize="9" textAnchor="middle" fill="#7c806d">
            FOUNDER
          </text>
        </g>
      </svg>
      <div className="office-footer">
        <span>
          <i className="legend-dot working" />
          In Arbeit <i className="legend-dot idle" />
          Bereit <i className="legend-dot waiting" />
          Wartet
        </span>
        <span>
          {compact
            ? "Agent auswählen, um Arbeit und Profil zu öffnen."
            : "Ziehen zum Verschieben · + / − für Zoom · Founder öffnet Prozesse"}
        </span>
      </div>
      {!compact && (
        <div className="office-agent-list" aria-label="Agenten im Office">
          {agents.map((a) => (
            <a key={a.id} href={`#/agents/${a.id}`}>
              <Avatar id={a.id} />
              <span>{a.name.split(" ")[0]}</span>
              <Badge value={stale ? "unknown" : a.activity.state} />
            </a>
          ))}
          <button className="button secondary" onClick={onLaunch}>
            <Icon name="plus" />
            Prozess mit Amancio starten
          </button>
        </div>
      )}
    </div>
  );
}
