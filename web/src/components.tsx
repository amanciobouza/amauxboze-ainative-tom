import { useState, type ReactNode } from "react";
import { api, identity } from "./api";
import type { Approval, Run } from "./types";

export const labels: Record<string, string> = {
  live: "Live",
  simulation: "Simulation",
  queued: "In Warteschlange",
  running: "In Arbeit",
  waiting_approval: "Entscheidung offen",
  held: "Pausiert",
  failed: "Blockiert",
  completed: "Abgeschlossen",
  rejected: "Abgelehnt",
  cancelled: "Abgebrochen",
  working: "In Arbeit",
  idle: "Bereit",
  blocked: "Blockiert",
  unknown: "Unbekannt",
  awaiting_review: "Review offen",
  approved: "Freigegeben",
  collecting: "Beiträge sammeln",
  synthesizing: "Zusammenführen",
  draft: "Entwurf",
  experimenting: "Experiment läuft",
  evaluating: "Auswertung",
  closed: "Abgeschlossen",
  proposed: "Vorgeschlagen",
  improved: "Verbessert",
  no_improvement: "Keine Verbesserung",
  inconclusive: "Nicht eindeutig",
  approve: "Freigeben",
  reject: "Ablehnen",
  revise: "Überarbeiten",
  hold: "Pausieren",
  cancel: "Abbrechen",
  retry: "Erneut versuchen",
  resume: "Wieder aufnehmen",
  recover: "Checkpoint wieder aufnehmen",
  act: "Handeln",
  investigate_further: "Weiter untersuchen",
  monitor: "Beobachten",
  archive: "Archivieren",
};
export const colors: Record<string, string> = {
  elena: "#ac694d",
  lucien: "#78836b",
  elodie: "#a57784",
  nora: "#7b86a5",
  marc: "#a48653",
  maya: "#7b9a94",
  sophie: "#ac8c79",
  kai: "#788eae",
  amancio: "#36473e",
};
export function Icon({ name, size = 19 }: { name: string; size?: number }) {
  const paths: Record<string, ReactNode> = {
    dashboard: (
      <>
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
      </>
    ),
    office: (
      <>
        <path d="m3 9 9-5 9 5-9 5zM3 9v8l9 5 9-5V9M12 14v8" />
      </>
    ),
    people: (
      <>
        <circle cx="9" cy="7" r="3" />
        <path d="M3 21v-3a6 6 0 0 1 12 0v3M16 4a3 3 0 0 1 0 6M18 14a5 5 0 0 1 3 4v3" />
      </>
    ),
    process: (
      <>
        <circle cx="5" cy="5" r="2" />
        <circle cx="19" cy="12" r="2" />
        <circle cx="5" cy="19" r="2" />
        <path d="M7 5h4v7h6M11 12v7H7" />
      </>
    ),
    check: <path d="m5 12 4 4L19 6" />,
    approvals: (
      <>
        <path d="M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h9" />
        <path d="m10 10 3 3 8-8" />
      </>
    ),
    skills: (
      <>
        <path d="m12 3 3 6 6 3-6 3-3 6-3-6-6-3 6-3z" />
      </>
    ),
    knowledge: (
      <>
        <path d="M12 5c-4-3-8-2-9-1v15c3-2 6-2 9 0 3-2 6-2 9 0V4c-3-2-6-2-9 1v14" />
      </>
    ),
    models: (
      <>
        <rect x="6" y="6" width="12" height="12" rx="2" />
        <path d="M9 2v4m6-4v4M9 18v4m6-4v4M2 9h4m-4 6h4m12-6h4m-4 6h4" />
        <rect x="10" y="10" width="4" height="4" />
      </>
    ),
    settings: (
      <>
        <path d="M4 7h16M4 17h16" />
        <circle cx="9" cy="7" r="3" />
        <circle cx="15" cy="17" r="3" />
      </>
    ),
    retro: (
      <>
        <path d="M20 7v5h-5M4 17v-5h5" />
        <path d="M6 7a7 7 0 0 1 12-1l2 2M4 16l2 2a7 7 0 0 0 12-1" />
      </>
    ),
    arrow: <path d="M4 12h16m-6-6 6 6-6 6" />,
    plus: <path d="M12 4v16M4 12h16" />,
    search: (
      <>
        <circle cx="10" cy="10" r="6" />
        <path d="m15 15 6 6" />
      </>
    ),
    close: <path d="m6 6 12 12M6 18 18 6" />,
    clock: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7v5l3 2" />
      </>
    ),
    link: (
      <>
        <path d="m10 14 4-4M8 16l-1 1a4 4 0 0 1-6-6l5-5a4 4 0 0 1 6 0M16 8l1-1a4 4 0 0 1 6 6l-5 5a4 4 0 0 1-6 0" />
      </>
    ),
  };
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name] || paths.process}
    </svg>
  );
}
export function Badge({ value }: { value: string }) {
  return (
    <span className={`badge ${value}`}>
      <i />
      {labels[value] || value}
    </span>
  );
}
export function Avatar({ id, large = false }: { id: string; large?: boolean }) {
  return (
    <span
      className={`avatar ${large ? "large" : ""}`}
      style={{ background: colors[id] || "#89938a" }}
    >
      <svg
        width={large ? 44 : 25}
        height={large ? 44 : 25}
        viewBox="0 0 24 28"
        shapeRendering="crispEdges"
        aria-hidden="true"
      >
        <path fill="#312c28" d="M6 3h12v3h3v9H3V6h3z" />
        <path fill="#edc7a1" d="M6 7h12v10H6z" />
        <path fill="#272b29" d="M8 10h2v2H8zm6 0h2v2h-2z" />
        <path fill="#f8f3e8" d="M8 17h8v3h5v8H3v-8h5z" />
        <path fill="#343c35" d="M10 19h4v9h-4z" />
      </svg>
    </span>
  );
}
export function Empty({
  title,
  children,
  action,
}: {
  title: string;
  children?: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="empty">
      <span className="empty-icon">
        <Icon name="process" size={27} />
      </span>
      <h3>{title}</h3>
      {children && <p>{children}</p>}
      {action}
    </div>
  );
}
export function ErrorBox({
  message,
  retry,
}: {
  message: string;
  retry?: () => void;
}) {
  return (
    <div className="error-box" role="alert">
      {message}
      {retry && (
        <button className="text-button" onClick={retry}>
          Erneut laden
        </button>
      )}
    </div>
  );
}
export function Loading() {
  return (
    <div className="loading" role="status">
      <span />
      Workspace wird geladen …
    </div>
  );
}
export function JsonView({ value }: { value: unknown }) {
  return <pre className="json-view">{JSON.stringify(value, null, 2)}</pre>;
}
export function ArtifactView({ value }: { value: unknown }) {
  if (value === null || value === undefined)
    return <span className="muted">Nicht verfügbar</span>;
  if (typeof value !== "object")
    return (
      <span>
        {typeof value === "boolean" ? (value ? "Ja" : "Nein") : String(value)}
      </span>
    );
  if (Array.isArray(value))
    return value.length ? (
      <ul className="artifact-list">
        {value.map((v, i) => (
          <li key={i}>
            <ArtifactView value={v} />
          </li>
        ))}
      </ul>
    ) : (
      <span className="muted">Keine Einträge</span>
    );
  return (
    <dl className="artifact-fields">
      {Object.entries(value).map(([k, v]) => (
        <div key={k}>
          <dt>{k.replaceAll("_", " ")}</dt>
          <dd>
            <ArtifactView value={v} />
          </dd>
        </div>
      ))}
    </dl>
  );
}
export function date(value: string) {
  return new Intl.DateTimeFormat("de-CH", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
export function RunTable({ runs }: { runs: Run[] }) {
  return runs.length ? (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Prozess</th>
            <th>Status</th>
            <th>Modus</th>
            <th>Aktualisiert</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {runs.map((r) => (
            <tr key={r.id}>
              <td>
                <a href={`#/runs/${r.id}`} className="run-name">
                  {r.title}
                </a>
                <small>{r.current_stage.replaceAll("_", " ")}</small>
              </td>
              <td>
                <Badge value={r.status} />
              </td>
              <td>
                <Badge value={r.mode} />
              </td>
              <td className="muted">{date(r.updated_at)}</td>
              <td>
                <a href={`#/runs/${r.id}`} aria-label={`${r.title} öffnen`}>
                  <Icon name="arrow" />
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  ) : (
    <Empty title="Noch keine Prozessläufe">
      Starte einen Prozess. Verlauf und Entscheidungen erscheinen hier.
    </Empty>
  );
}
export function ApprovalCard({
  approval,
  onDone,
}: {
  approval: Approval;
  onDone: () => void;
}) {
  const [rationale, setRationale] = useState(""),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<string | null>(null);
  async function decide(decision: string) {
    setBusy(true);
    setError(null);
    try {
      await api(`/approvals/${approval.id}/decision`, "POST", {
        decision,
        revision: approval.revision,
        rationale,
        idempotency_key: identity(),
      });
      onDone();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <article className="approval-card">
      <div className="row between">
        <div className="row">
          <span className="approval-icon">
            <Icon name={approval.kind === "recovery" ? "retro" : "approvals"} />
          </span>
          <div>
            <h3>{approval.action.replaceAll("_", " ")}</h3>
            <a href={`#/runs/${approval.run_id}`}>
              Prozess öffnen <span aria-hidden>↗</span>
            </a>
          </div>
        </div>
        <Badge
          value={approval.kind === "recovery" ? "failed" : "waiting_approval"}
        />
      </div>
      <div className="approval-context">
        <ArtifactView value={approval.context} />
      </div>
      <label>
        Begründung / Feedback
        <textarea
          value={rationale}
          onChange={(e) => setRationale(e.target.value)}
          placeholder="Was ist für deine Entscheidung relevant?"
          rows={2}
        />
      </label>
      {error && <ErrorBox message={error} />}
      <div className="row wrap">
        {approval.allowed_decisions.map((d) => (
          <button
            disabled={busy}
            className={
              ["approve", "act", "retry"].includes(d)
                ? "button primary"
                : "button secondary"
            }
            key={d}
            onClick={() => void decide(d)}
          >
            {labels[d] || d}
          </button>
        ))}
      </div>
    </article>
  );
}
