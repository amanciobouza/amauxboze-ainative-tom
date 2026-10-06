import { useCallback, useEffect, useState, type ReactNode } from "react";
import { api, identity, useResource } from "./api";
import {
  ApprovalCard,
  ArtifactView,
  Avatar,
  Badge,
  Empty,
  ErrorBox,
  Icon,
  JsonView,
  Loading,
  RunTable,
  date,
  labels,
} from "./components";
import Launcher from "./Launcher";
import Office from "./Office";
import type {
  Agent,
  Approval,
  DashboardData,
  Health,
  Models,
  Organization,
  Page,
  Process,
  Retrospective,
  Run,
  Settings,
  Skill,
} from "./types";
import "./style.css";

const nav = [
  ["dashboard", "Überblick", "dashboard"],
  ["office", "Office", "office"],
  ["organization", "Organisation", "people"],
  ["departments", "Abteilungen", "process"],
  ["processes", "Prozesse", "process"],
  ["runs", "Prozessläufe", "clock"],
  ["approvals", "Freigaben", "approvals"],
  ["retrospectives", "Retrospektiven", "retro"],
  ["agents", "Agenten", "people"],
  ["skills", "Skills", "skills"],
  ["knowledge", "Wissen", "knowledge"],
  ["models", "Modelle", "models"],
  ["settings", "Einstellungen", "settings"],
];
function useRoute() {
  const [route, setRoute] = useState(location.hash.slice(2) || "dashboard");
  useEffect(() => {
    const handler = () => setRoute(location.hash.slice(2) || "dashboard");
    window.addEventListener("hashchange", handler);
    return () => window.removeEventListener("hashchange", handler);
  }, []);
  return route;
}
function Head({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {action}
    </div>
  );
}
function Panel({
  title,
  subtitle,
  action,
  children,
  className = "",
}: {
  title?: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`panel ${className}`}>
      {title && (
        <div className="panel-heading">
          <div>
            <h2>{title}</h2>
            {subtitle && <p>{subtitle}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
function ResourceState({
  loading,
  error,
  retry,
}: {
  loading: boolean;
  error: string | null;
  retry: () => void;
}) {
  return error ? (
    <ErrorBox message={error} retry={retry} />
  ) : loading ? (
    <Loading />
  ) : null;
}

function Dashboard({
  launch,
  agents,
}: {
  launch: () => void;
  agents: Agent[];
}) {
  const [mode, setMode] = useState("live"),
    [days, setDays] = useState(7);
  const resource = useResource<DashboardData>(
      `/dashboard?mode=${mode}&days=${days}`,
    ),
    health = useResource<Health>("/health");
  const data = resource.data;
  return (
    <>
      <Head
        eyebrow="DEIN UNTERNEHMEN. EIN SYSTEM."
        title="Klarheit. Dann Umsetzung."
        description="Prioritäten, Menschen und Entscheidungen an einem Ort."
        action={
          <button className="button primary" onClick={launch}>
            <Icon name="plus" />
            Prozess starten
          </button>
        }
      />
      <div className="dashboard-intro">
        <div>
          <span className="eyebrow">AMAUX BOZÉ / OPERATING SYSTEM</span>
          <h2>
            Gute Arbeit braucht
            <br />
            eine klare Richtung.
          </h2>
          <p>
            Acht Verantwortlichkeiten. Ein gemeinsamer Takt.
            <br />
            Du entscheidest. Das System koordiniert.
          </p>
          <a className="text-button" href="#/office">
            Ins Office <Icon name="arrow" />
          </a>
        </div>
        <Office agents={agents} onLaunch={launch} compact />
      </div>
      <div className="section-line">
        <div>
          <h2>Company Pulse</h2>
          <p>Nachvollziehbare Zahlen aus deinem Betrieb.</p>
        </div>
        <div className="row">
          <select
            aria-label="Dashboard-Modus"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
          >
            <option value="live">Live-Betrieb</option>
            <option value="simulation">Simulation</option>
          </select>
          <select
            aria-label="KPI-Zeitraum"
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
          >
            <option value={7}>Letzte 7 Tage</option>
            <option value={30}>Letzte 30 Tage</option>
            <option value={90}>Letzte 90 Tage</option>
          </select>
        </div>
      </div>
      <ResourceState {...resource} retry={resource.reload} />
      {data && (
        <>
          <div className="kpi-grid">
            {data.kpis.slice(0, 4).map((k) => (
              <article className="kpi-card" key={k.id}>
                <div className="row between">
                  <span>{k.name}</span>
                  <Icon
                    name={
                      k.id === "approvals"
                        ? "approvals"
                        : k.id === "success"
                          ? "check"
                          : "process"
                    }
                    size={16}
                  />
                </div>
                <strong>
                  {k.value === null
                    ? "—"
                    : new Intl.NumberFormat("de-CH").format(k.value)}
                  <small>{k.id === "success" ? "%" : ""}</small>
                </strong>
                <a
                  href={
                    k.id === "approvals"
                      ? "#/approvals"
                      : `#/runs${k.filter_status ? `?status=${k.filter_status}` : ""}`
                  }
                >
                  {k.unavailable_reason || `${k.unit} · ${days} Tage`}
                  <Icon name="arrow" size={13} />
                </a>
                <details>
                  <summary>Quelle & Berechnung</summary>
                  <p>{k.formula}</p>
                  <p>
                    {k.source} · {k.coverage}
                  </p>
                  <small>{date(k.observed_at)}</small>
                </details>
              </article>
            ))}
          </div>
          <div className="two-columns">
            <Panel
              title="Aktuelle Prozesse"
              subtitle="Was gerade passiert — und was als Nächstes ansteht."
              action={
                <a href="#/runs" className="text-button">
                  Alle Läufe <Icon name="arrow" size={16} />
                </a>
              }
            >
              <RunTable runs={data.recent_runs} />
            </Panel>
            <Panel
              title="Deine Entscheidungen"
              subtitle="Konsequenzielle Schritte bleiben bei dir."
            >
              <div className="decision-summary">
                <span className="decision-count">
                  {data.pending_approvals.length}
                </span>
                <div>
                  <h3>
                    {data.pending_approvals.length
                      ? "Entscheidungen warten"
                      : "Alles entschieden"}
                  </h3>
                  <p>
                    {data.pending_approvals.length
                      ? "Prüfe Ergebnisse, bevor der nächste Schritt beginnt."
                      : "Neue Freigaben erscheinen hier, sobald ein Prozess sie braucht."}
                  </p>
                </div>
              </div>
              <a className="button secondary wide" href="#/approvals">
                Freigaben öffnen <Icon name="arrow" />
              </a>
              {data.blocked_runs.length > 0 && (
                <a className="notice" href="#/runs?status=failed">
                  {data.blocked_runs.length} blockierte Läufe prüfen ↗
                </a>
              )}
            </Panel>
          </div>
          <div className="two-columns equal">
            <Panel
              title="Lernen aus der Arbeit"
              action={
                <a href="#/retrospectives" className="text-button">
                  Retrospektiven ↗
                </a>
              }
            >
              {data.learnings.length ? (
                <div className="list">
                  {data.learnings.map((l, i) => (
                    <a key={i} href={`#/runs/${l.run_id}`}>
                      <span className="list-icon">
                        <Icon name="knowledge" />
                      </span>
                      <div>
                        <strong>{l.title}</strong>
                        <small>{l.type.replaceAll("_", " ")}</small>
                      </div>
                      <Icon name="arrow" size={16} />
                    </a>
                  ))}
                </div>
              ) : (
                <Empty title="Erfahrung wird zu Wissen">
                  Abgeschlossene Prozesse liefern Learnings. In Retrospektiven
                  prüfst du konkrete Verbesserungen.
                </Empty>
              )}
            </Panel>
            <Panel title="Verbindungen & weitere Kennzahlen">
              <div className="connection-line">
                <span>
                  <i className="status-dot" />
                  Lokale Runtime
                </span>
                <Badge value={health.error ? "unknown" : "running"} />
              </div>
              <div className="connection-line">
                <span>Obsidian</span>
                <span className="muted">
                  {health.data?.knowledge_available
                    ? "Verbunden"
                    : "Pfad prüfen"}
                </span>
              </div>
              <div className="compact-metrics">
                {data.kpis.slice(4).map((k) => (
                  <details key={k.id}>
                    <summary>
                      <span>{k.name}</span>
                      <strong>
                        {k.value === null
                          ? "Nicht verfügbar"
                          : `${k.value} ${k.unit}`}
                      </strong>
                    </summary>
                    <p>{k.unavailable_reason || k.formula}</p>
                    <small>
                      {k.source} · {k.coverage}
                    </small>
                  </details>
                ))}
              </div>
              <a href="#/models" className="text-button">
                Modelle & Integrationen prüfen <Icon name="arrow" size={16} />
              </a>
            </Panel>
          </div>
        </>
      )}
    </>
  );
}

function Processes({
  launch,
  filter = "",
  department,
}: {
  launch: (p: Process) => void;
  filter?: string;
  department?: string;
}) {
  const resource = useResource<Process[]>("/processes", 0);
  const values = resource.data?.filter(
    (p) =>
      (!department ||
        p.owner_department_id === department ||
        p.participant_department_ids.includes(department)) &&
      `${p.name} ${p.description}`.toLowerCase().includes(filter.toLowerCase()),
  );
  return (
    <>
      <Head
        eyebrow="VON ABSICHT ZU ERGEBNIS"
        title={department ? "Prozesse der Abteilung" : "Geschäftsprozesse"}
        description="Fünf gemeinsame Abläufe. Klare Eingaben, belegte Ergebnisse und explizite Freigaben."
      />
      <ResourceState {...resource} retry={resource.reload} />
      <div className="process-grid">
        {values?.map((p, i) => (
          <article key={p.id} className="process-card">
            <div className="row between">
              <span className="process-number">0{i + 1}</span>
              <span className="tag">{p.owner_department_id.toUpperCase()}</span>
            </div>
            <span className="process-symbol">
              <Icon
                name={
                  p.id === "customer-feedback"
                    ? "people"
                    : p.id === "market-intelligence"
                      ? "knowledge"
                      : p.id === "content-campaign"
                        ? "skills"
                        : "process"
                }
                size={30}
              />
            </span>
            <h2>{p.name}</h2>
            <p>{p.description}</p>
            <div className="process-bottom">
              <p>
                <Icon name="approvals" size={15} />
                {p.approval_summary}
              </p>
              {p.live_limitation && (
                <small className="muted">{p.live_limitation}</small>
              )}
              <button
                className="button secondary wide"
                onClick={() => launch(p)}
              >
                Prozess vorbereiten <Icon name="arrow" />
              </button>
            </div>
          </article>
        ))}
      </div>
      {values?.length === 0 && <Empty title="Kein passender Prozess" />}
    </>
  );
}

function OrganizationPage({
  department = false,
  launch,
}: {
  department?: boolean;
  launch: (p: Process) => void;
}) {
  const org = useResource<Organization>("/organization", 0),
    processes = useResource<Process[]>("/processes", 0),
    [filter, setFilter] = useState("");
  return (
    <>
      <Head
        eyebrow="VERANTWORTUNG IST SICHTBAR"
        title={
          department ? "Abteilungen" : "Eine Firma. Acht Verantwortlichkeiten."
        }
        description="Amancio setzt die Richtung. Elena koordiniert. Jeder Bereich trägt seine fachliche Verantwortung."
      />
      <ResourceState {...org} retry={org.reload} />
      {org.data && (
        <>
          {!department && (
            <div className="org-founder">
              <Avatar id="amancio" large />
              <div>
                <span className="eyebrow">FOUNDER / HUMAN</span>
                <h2>Amancio</h2>
                <p>Finale strategische und konsequenzielle Entscheidungen</p>
              </div>
              <span className="tag">Alle Agenten berichten an Amancio</span>
            </div>
          )}
          <div className="section-line">
            <h2>{department ? "Fachbereiche" : "Verantwortungsstruktur"}</h2>
            <select
              aria-label="Abteilung filtern"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="">Alle Abteilungen</option>
              {org.data.departments.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </div>
          <div className="department-grid">
            {org.data.departments
              .filter((d) => !filter || d.id === filter)
              .map((d) => (
                <Panel key={d.id} className="department-card">
                  <div className="row between">
                    <span className="department-icon">
                      <Icon
                        name={
                          d.id === "technology"
                            ? "models"
                            : d.id === "intelligence"
                              ? "knowledge"
                              : "process"
                        }
                      />
                    </span>
                    <span className="tag">
                      {d.member_ids.length}{" "}
                      {d.member_ids.length === 1 ? "AGENT" : "AGENTEN"}
                    </span>
                  </div>
                  <h2>{d.name}</h2>
                  <p>{d.mission}</p>
                  <div className="department-members">
                    {d.member_ids.map((id) => {
                      const n = org.data!.nodes.find((n) => n.id === id);
                      return (
                        <a href={`#/agents/${id}`} key={id}>
                          <Avatar id={id} />
                          <div>
                            <strong>{n?.display_name}</strong>
                            <small>{n?.role}</small>
                          </div>
                          <Icon name="arrow" size={16} />
                        </a>
                      );
                    })}
                  </div>
                  <div className="department-processes">
                    {processes.data
                      ?.filter(
                        (p) =>
                          p.owner_department_id === d.id ||
                          p.participant_department_ids.includes(d.id),
                      )
                      .map((p) => (
                        <button key={p.id} onClick={() => launch(p)}>
                          <span>{p.name}</span>
                          <small>
                            {p.owner_department_id === d.id
                              ? "Owner"
                              : "Beteiligt"}
                          </small>
                          <Icon name="plus" size={14} />
                        </button>
                      ))}
                    {!processes.data?.some(
                      (p) =>
                        p.owner_department_id === d.id ||
                        p.participant_department_ids.includes(d.id),
                    ) && (
                      <p className="muted">
                        Unterstützt die Plattform. Keine separat startbaren
                        Business-Prozesse.
                      </p>
                    )}
                  </div>
                </Panel>
              ))}
          </div>
          <p className="footnote">
            Elena koordiniert über Abteilungsgrenzen hinweg. Organigramm und UI
            verändern keine Berechtigungen.
          </p>
        </>
      )}
    </>
  );
}

function Agents({ filter = "" }: { filter?: string }) {
  const resource = useResource<Agent[]>("/agents");
  return (
    <>
      <Head
        eyebrow="DIE MENSCHEN HINTER DEN ROLLEN"
        title="Dein Agententeam"
        description="Profile, Fähigkeiten und aktuelle Arbeit — aus Registry und Runtime, nicht aus Animationen."
      />
      <ResourceState {...resource} retry={resource.reload} />
      <div className="agent-grid">
        {resource.data
          ?.filter((a) =>
            `${a.name} ${a.role}`.toLowerCase().includes(filter.toLowerCase()),
          )
          .map((a) => (
            <a className="agent-card" href={`#/agents/${a.id}`} key={a.id}>
              <div className="row between">
                <Avatar id={a.id} large />
                <Badge value={resource.error ? "unknown" : a.activity.state} />
              </div>
              <h2>{a.name}</h2>
              <span className="agent-role">{a.role}</span>
              <p>{a.mission}</p>
              <div className="row between">
                <span>{a.skills.length} Skills</span>
                <Icon name="arrow" />
              </div>
            </a>
          ))}
      </div>
    </>
  );
}

function AgentDetail({ id }: { id: string }) {
  const [offset, setOffset] = useState(0),
    [status, setStatus] = useState("");
  const resource = useResource<Agent>(
    `/agents/${id}?offset=${offset}${status ? `&status=${status}` : ""}`,
  );
  const a = resource.data;
  return (
    <>
      <a href="#/agents" className="back-link">
        ← Agententeam
      </a>
      <ResourceState {...resource} retry={resource.reload} />
      {a && (
        <>
          <div className="agent-detail-head">
            <Avatar id={id} large />
            <div>
              <span className="eyebrow">AGENT / {id.toUpperCase()}</span>
              <h1>{a.name}</h1>
              <p>{a.role}</p>
            </div>
            <Badge value={resource.error ? "unknown" : a.activity.state} />
          </div>
          <div className="two-columns">
            <div>
              <Panel title="Verantwortung & Haltung">
                <p className="mission">{a.mission}</p>
                {a.communication_instructions.length > 0 && (
                  <div className="instructions">
                    <h3>So arbeitet {a.name.split(" ")[0]}</h3>
                    <ul>
                      {a.communication_instructions.map((t, i) => (
                        <li key={i}>{t}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <details className="profile-bio">
                  <summary>Hintergrund und Rollenbeschreibung</summary>
                  {a.biography ? (
                    <>
                      <p className="footnote">Quelle: {a.biography_source}</p>
                      <pre>{a.biography}</pre>
                    </>
                  ) : (
                    <p className="muted">Biografie nicht verfügbar.</p>
                  )}
                </details>
              </Panel>
              <Panel
                title="Fähigkeiten"
                subtitle="Versionierte Skills und ihre Verträge."
              >
                <div className="skill-links">
                  {a.skill_details?.map((s) => (
                    <a href={`#/skills/${s.id}`} key={s.id}>
                      <Icon name="skills" size={17} />
                      <span>{s.id}</span>
                      <small>v{s.version}</small>
                      <Icon name="arrow" size={14} />
                    </a>
                  ))}
                </div>
                {!!a.unavailable_skills?.length && (
                  <details className="profile-bio">
                    <summary>
                      Deklarierte Fähigkeiten ohne ausführbares Manifest
                    </summary>
                    <p className="footnote">
                      Diese bestehenden Rollenzuordnungen sind noch nicht als
                      Runtime-Skills implementiert.
                    </p>
                    <div className="tags">
                      {a.unavailable_skills.map((skill) => (
                        <span className="tag" key={skill}>
                          {skill} · nicht verfügbar
                        </span>
                      ))}
                    </div>
                  </details>
                )}
              </Panel>
            </div>
            <div>
              <Panel
                title="Aktuelle Arbeit"
                subtitle={`Snapshot ${date(a.activity.observed_at)}`}
              >
                <div className="list">
                  {[
                    ...a.activity.active_assignments,
                    ...a.activity.waiting_assignments,
                  ].map((x, i) => (
                    <a key={i} href={`#/runs/${x.run_id}`}>
                      <div>
                        <strong>{x.title}</strong>
                        <small>{x.stage}</small>
                      </div>
                      <Badge value={x.status || "running"} />
                    </a>
                  ))}
                </div>
                {!a.activity.active_assignments.length &&
                  !a.activity.waiting_assignments.length && (
                    <Empty title="Bereit für den nächsten Auftrag">
                      Keine aktive Prozesszuordnung im aktuellen Snapshot.
                    </Empty>
                  )}
              </Panel>
              <Panel title="Rechte & Grenzen">
                <h3>Tools</h3>
                {Object.entries(a.tools).map(([kind, tools]) => (
                  <div className="permission-line" key={kind}>
                    <span>{kind}</span>
                    <span>{tools.join(", ") || "Keine"}</span>
                  </div>
                ))}
                <h3>Freigabepflichtig</h3>
                <div className="tags">
                  {a.approval_boundaries.map((b) => (
                    <span key={b} className="tag">
                      {b.replaceAll("_", " ")}
                    </span>
                  ))}
                </div>
              </Panel>
            </div>
          </div>
          <Panel
            title="Ausführungshistorie"
            action={
              <select
                aria-label="Agentenhistorie filtern"
                value={status}
                onChange={(e) => {
                  setStatus(e.target.value);
                  setOffset(0);
                }}
              >
                <option value="">Alle Ergebnisse</option>
                <option value="completed">Abgeschlossen</option>
                <option value="failed">Fehlgeschlagen</option>
              </select>
            }
          >
            {a.history?.length ? (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Skill</th>
                      <th>Ergebnis</th>
                      <th>Versuch</th>
                      <th>Modell</th>
                      <th>Zeitpunkt</th>
                    </tr>
                  </thead>
                  <tbody>
                    {a.history.map((h) => (
                      <tr key={h.id}>
                        <td>
                          <a href={`#/runs/${h.run_id}`}>{h.skill_id}</a>
                          <small>Trace {h.trace_id.slice(0, 8)}</small>
                        </td>
                        <td>
                          <Badge value={h.status} />
                        </td>
                        <td>{h.attempt_number}</td>
                        <td>{h.model || h.provider || "—"}</td>
                        <td>{date(h.started_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <Empty title="Noch keine ausgeführten Stufen" />
            )}
            <div className="pagination">
              <button
                disabled={!offset}
                onClick={() => setOffset(Math.max(0, offset - 30))}
              >
                ← Zurück
              </button>
              <span>{a.history_total || 0} Einträge</span>
              <button
                disabled={offset + 30 >= (a.history_total || 0)}
                onClick={() => setOffset(offset + 30)}
              >
                Weiter →
              </button>
            </div>
          </Panel>
        </>
      )}
    </>
  );
}

function Skills({ id, filter = "" }: { id?: string; filter?: string }) {
  const resource = useResource<Skill[]>("/skills", 0),
    [selected, setSelected] = useState(id || "");
  useEffect(() => setSelected(id || ""), [id]);
  const skill = resource.data?.find((s) => s.id === selected);
  return (
    <>
      <Head
        eyebrow="FÄHIGKEITEN MIT VERTRAG"
        title="Skill Registry"
        description="Zweck, Version, Eingaben, Ausgaben und Modellanforderungen bleiben explizit."
      />
      <ResourceState {...resource} retry={resource.reload} />
      <div className="registry-layout">
        <Panel>
          <div className="registry-list">
            {resource.data
              ?.filter((s) =>
                `${s.id} ${s.purpose}`
                  .toLowerCase()
                  .includes(filter.toLowerCase()),
              )
              .map((s) => (
                <button
                  className={selected === s.id ? "selected" : ""}
                  onClick={() => setSelected(s.id)}
                  key={s.id}
                >
                  <Icon name="skills" />
                  <span>{s.id}</span>
                  <small>v{s.version}</small>
                </button>
              ))}
          </div>
        </Panel>
        <Panel>
          {skill ? (
            <>
              <span className="tag">VERSION {skill.version}</span>
              <h2 className="detail-title">{skill.id}</h2>
              <p>{skill.purpose}</p>
              <h3>Eingabevertrag</h3>
              <JsonView value={skill.inputs} />
              <h3>Ausgabevertrag</h3>
              <JsonView value={skill.outputs} />
              <h3>Modellanforderungen</h3>
              <ArtifactView value={skill.model} />
              <h3>Kontext & Tools</h3>
              <p>
                {skill.context.join(", ") ||
                  "Kein zusätzlicher Knowledge-Kontext"}
              </p>
              <p>{skill.allowed_tools.join(", ") || "Keine Tools"}</p>
            </>
          ) : (
            <Empty title="Fähigkeit auswählen">
              Wähle einen Skill, um seinen Vertrag zu prüfen.
            </Empty>
          )}
        </Panel>
      </div>
    </>
  );
}

function Runs({ search = "" }: { search?: string }) {
  const query = location.hash.split("?")[1] || "",
    initial = new URLSearchParams(query).get("status") || "";
  const [status, setStatus] = useState(initial),
    [mode, setMode] = useState(""),
    [offset, setOffset] = useState(0);
  const resource = useResource<Page<Run>>(
    `/runs?offset=${offset}${status ? `&status=${status}` : ""}${mode ? `&mode=${mode}` : ""}`,
  );
  return (
    <>
      <Head
        eyebrow="DER VERLAUF DEINER FIRMA"
        title="Prozessläufe"
        description="Aktuelle Arbeit, Ergebnisse, Freigaben und Wiederaufnahme — dauerhaft gespeichert."
      />
      <div className="filter-bar">
        <select
          aria-label="Prozessstatus"
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            setOffset(0);
          }}
        >
          <option value="">Alle Zustände</option>
          {[
            "active",
            "queued",
            "running",
            "waiting_approval",
            "held",
            "failed",
            "completed",
            "rejected",
            "cancelled",
          ].map((s) => (
            <option key={s} value={s}>
              {labels[s] || "Aktive Prozesse"}
            </option>
          ))}
        </select>
        <select
          aria-label="Ausführungsmodus"
          value={mode}
          onChange={(e) => {
            setMode(e.target.value);
            setOffset(0);
          }}
        >
          <option value="">Live & Simulation</option>
          <option value="live">Live</option>
          <option value="simulation">Simulation</option>
        </select>
        <span className="muted">{resource.data?.total || 0} Läufe</span>
      </div>
      <ResourceState {...resource} retry={resource.reload} />
      {resource.data && (
        <Panel>
          <RunTable
            runs={resource.data.items.filter((r) =>
              `${r.title} ${r.id}`.toLowerCase().includes(search.toLowerCase()),
            )}
          />
          <div className="pagination">
            <button
              disabled={!offset}
              onClick={() => setOffset(Math.max(0, offset - 50))}
            >
              ← Zurück
            </button>
            <span>
              {offset + 1}–{Math.min(offset + 50, resource.data.total)} /{" "}
              {resource.data.total}
            </span>
            <button
              disabled={offset + 50 >= resource.data.total}
              onClick={() => setOffset(offset + 50)}
            >
              Weiter →
            </button>
          </div>
        </Panel>
      )}
    </>
  );
}

function RunDetail({ id }: { id: string }) {
  const resource = useResource<Run>(`/runs/${id}`, 2000),
    [error, setError] = useState<string | null>(null),
    [busy, setBusy] = useState(false);
  const run = resource.data;
  async function command(action: string) {
    if (!run) return;
    setBusy(true);
    setError(null);
    try {
      await api(`/runs/${id}/${action}`, "POST", {
        revision: run.revision,
        idempotency_key: identity(),
      });
      resource.reload();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <a href="#/runs" className="back-link">
        ← Prozessläufe
      </a>
      <ResourceState {...resource} retry={resource.reload} />
      {run && (
        <>
          <Head
            eyebrow={`PROZESS / ${run.id.slice(0, 8)}`}
            title={run.title}
            description={`${run.process_id} · Gestartet ${date(run.created_at)}`}
            action={
              <div className="row">
                <Badge value={run.mode} />
                <Badge value={run.status} />
              </div>
            }
          />
          {run.mode === "simulation" && (
            <div className="notice simulation">
              Dieser Lauf verwendet Demonstrationsdaten. Es wurden keine
              externen Aktionen ausgeführt.
            </div>
          )}
          {run.error && <ErrorBox message={run.error} />}
          <div className="run-overview">
            <div>
              <span>Aktuelle Stufe</span>
              <strong>{run.current_stage.replaceAll("_", " ")}</strong>
            </div>
            <div>
              <span>Verantwortlich</span>
              <strong>
                {run.active_agent_ids.join(", ") || "Founder / Runtime"}
              </strong>
            </div>
            <div>
              <span>Revision</span>
              <strong>{run.revision}</strong>
            </div>
            <div>
              <span>Aktualisiert</span>
              <strong>{date(run.updated_at)}</strong>
            </div>
          </div>
          {error && <ErrorBox message={error} />}
          <div className="row wrap">
            {!run.approval &&
              run.allowed_commands.map((c) => (
                <button
                  key={c}
                  className="button secondary"
                  disabled={busy}
                  onClick={() => void command(c)}
                >
                  {labels[c] || c}
                </button>
              ))}
          </div>
          {run.approval && (
            <ApprovalCard approval={run.approval} onDone={resource.reload} />
          )}
          <div className="two-columns">
            <Panel
              title="Ergebnisse & Artefakte"
              subtitle="Jede ausgeführte Stufe bleibt ihrem Agenten und Versuch zugeordnet."
            >
              {run.attempts?.length ? (
                <div className="artifacts">
                  {run.attempts
                    .slice()
                    .reverse()
                    .map((a) => (
                      <details
                        key={a.id}
                        className="artifact"
                        open={
                          a.agent_id === "elena" && a.status === "completed"
                        }
                      >
                        <summary>
                          <Avatar id={a.agent_id} />
                          <div>
                            <strong>{a.skill_id}</strong>
                            <small>
                              {a.agent_id} · Versuch {a.attempt_number} ·{" "}
                              {a.model || a.provider || "Modell unbekannt"}
                            </small>
                          </div>
                          <Badge value={a.status} />
                        </summary>
                        <div className="artifact-body">
                          {a.error ? (
                            <ErrorBox message={a.error} />
                          ) : (
                            <ArtifactView value={a.artifact} />
                          )}
                          <p className="footnote">
                            Trace {a.trace_id} · {date(a.started_at)}
                          </p>
                          {Object.keys(a.usage).length > 0 && (
                            <details>
                              <summary>Modellnutzung</summary>
                              <ArtifactView value={a.usage} />
                            </details>
                          )}
                        </div>
                      </details>
                    ))}
                </div>
              ) : (
                <Empty title="Noch keine Ergebnisse">
                  Der Prozess wird vorbereitet.
                </Empty>
              )}
            </Panel>
            <div>
              <Panel title="Timeline">
                <ol className="timeline">
                  {run.events
                    ?.slice()
                    .reverse()
                    .map((e) => (
                      <li key={e.id}>
                        <span className="timeline-dot" />
                        <small>{date(e.timestamp)}</small>
                        <strong>
                          {(
                            {
                              run_created: "Prozess gestartet",
                              stage_started: "Arbeit begonnen",
                              stage_completed: "Ergebnis geliefert",
                              decision_recorded: "Entscheidung erfasst",
                              run_updated: "Prozess aktualisiert",
                              run_failed: "Ausführung blockiert",
                            } as Record<string, string>
                          )[e.type] || e.type.replaceAll("_", " ")}
                        </strong>
                        <p>
                          {String(
                            e.payload.skill_id ||
                              e.payload.current_state ||
                              e.payload.status ||
                              e.payload.decision ||
                              "",
                          )}
                        </p>
                      </li>
                    ))}
                </ol>
              </Panel>
              <Panel title="Eingaben">
                <ArtifactView value={run.input} />
              </Panel>
            </div>
          </div>
          {run.status === "completed" && (
            <Panel title="Was lernen wir daraus?">
              <div className="row between">
                <p>
                  Prüfe Ergebnisse mit Elena und deinem Team in einer
                  evidenzbasierten Retrospektive.
                </p>
                <a
                  href={`#/retrospectives?run=${run.id}`}
                  className="button secondary"
                >
                  Retrospektive vorbereiten <Icon name="retro" />
                </a>
              </div>
            </Panel>
          )}
        </>
      )}
    </>
  );
}

function Approvals() {
  const resource = useResource<Approval[]>("/approvals", 3000);
  return (
    <>
      <Head
        eyebrow="DU BEHÄLTST DIE ENTSCHEIDUNG"
        title="Freigaben & Recovery"
        description="Prüfe den Kontext. Entscheide bewusst. Die erlaubten Schritte kommen aus dem aktiven Workflow."
      />
      <ResourceState {...resource} retry={resource.reload} />
      {resource.data?.length
        ? resource.data.map((a) => (
            <ApprovalCard key={a.id} approval={a} onDone={resource.reload} />
          ))
        : !resource.loading && (
            <Panel>
              <Empty title="Keine offenen Entscheidungen">
                Sobald ein Prozess deine Freigabe braucht, erscheint er hier.
              </Empty>
            </Panel>
          )}
    </>
  );
}

function Knowledge() {
  const [query, setQuery] = useState(""),
    [submitted, setSubmitted] = useState(""),
    [scope, setScope] = useState(""),
    [path, setPath] = useState("");
  const resource = useResource<{
    items: { path: string; title: string; size: number }[];
    source: string;
  }>(
    `/knowledge?q=${encodeURIComponent(submitted)}&scope=${encodeURIComponent(scope)}`,
    0,
  );
  const [note, setNote] = useState<{
      content: string;
      path: string;
      truncated: boolean;
    } | null>(null),
    [error, setError] = useState<string | null>(null),
    [busy, setBusy] = useState(false);
  async function open(p: string) {
    setPath(p);
    setBusy(true);
    setError(null);
    setNote(null);
    try {
      setNote(await api(`/knowledge/note?path=${encodeURIComponent(p)}`));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <Head
        eyebrow="ORGANISATORISCHES GEDÄCHTNIS"
        title="Wissen, das bleibt."
        description="Notizen, Entscheidungen und Learnings aus deinem konfigurierten Obsidian-Vault."
      />
      <form
        className="knowledge-search"
        onSubmit={(e) => {
          e.preventDefault();
          setSubmitted(query);
        }}
      >
        <Icon name="search" />
        <input
          aria-label="Wissen durchsuchen"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Notizen und Inhalte durchsuchen …"
        />
        <input
          aria-label="Wissensordner"
          value={scope}
          onChange={(e) => setScope(e.target.value)}
          placeholder="Ordner (optional)"
        />
        <button className="button secondary">Suchen</button>
      </form>
      <ResourceState {...resource} retry={resource.reload} />
      {resource.error && (
        <p className="notice">
          Prüfe den Vault-Pfad unter <a href="#/settings">Einstellungen</a>.
          Fehlendes Wissen wird nicht durch erfundene Notizen ersetzt.
        </p>
      )}
      <div className="registry-layout">
        <Panel>
          <div className="note-list">
            {resource.data?.items.map((n) => (
              <button
                key={n.path}
                onClick={() => void open(n.path)}
                className={path === n.path ? "selected" : ""}
              >
                <Icon name="knowledge" />
                <div>
                  <strong>{n.title}</strong>
                  <small>{n.path}</small>
                </div>
              </button>
            ))}
          </div>
          {resource.data?.items.length === 0 && (
            <Empty title="Keine Notizen gefunden" />
          )}
        </Panel>
        <Panel>
          {busy ? (
            <Loading />
          ) : error ? (
            <ErrorBox message={error} />
          ) : note ? (
            <>
              <span className="eyebrow">OBSIDIAN / QUELLE</span>
              <h2 className="detail-title">
                {note.path.split("/").at(-1)?.replace(".md", "")}
              </h2>
              <p className="footnote">{note.path}</p>
              {note.truncated && (
                <p className="notice">Vorschau auf 24.000 Zeichen begrenzt.</p>
              )}
              <pre className="note-content">{note.content}</pre>
            </>
          ) : (
            <Empty title="Wissen öffnen">
              Wähle eine Notiz. Der Browser erhält ausschließlich kontrollierte
              Markdown-Inhalte.
            </Empty>
          )}
        </Panel>
      </div>
    </>
  );
}

function ModelsPage() {
  const resource = useResource<Models>("/models", 10000);
  return (
    <>
      <Head
        eyebrow="INTELLIGENZ HINTER EINER GRENZE"
        title="Modelle & Routing"
        description="Lokale Modelle zuerst. Cloud-Anbieter nur mit bewusster Auswahl. Keine stille Ausweichroute."
        action={
          <a href="#/settings" className="button secondary">
            Routing konfigurieren <Icon name="settings" />
          </a>
        }
      />
      <ResourceState {...resource} retry={resource.reload} />
      {resource.data && (
        <>
          <div className="model-grid">
            <Panel>
              <div className="row between">
                <span className="model-symbol">
                  <Icon name="models" size={28} />
                </span>
                <Badge
                  value={
                    resource.data.lm_studio.available ? "running" : "unknown"
                  }
                />
              </div>
              <h2>LM Studio</h2>
              <p>Lokale Intelligenz auf deinem Rechner.</p>
              <p className="mono">{resource.data.routing.lm_studio_url}</p>
              {resource.data.lm_studio.reason && (
                <p className="notice">{resource.data.lm_studio.reason}</p>
              )}
              <div className="list">
                {resource.data.lm_studio.models.map((m) => (
                  <div key={m} className="model-name">
                    <i className="status-dot" />
                    {m}
                  </div>
                ))}
              </div>
            </Panel>
            {(["openai", "anthropic"] as const).map((p) => (
              <Panel key={p}>
                <div className="row between">
                  <span className="model-symbol">
                    <Icon name="skills" size={28} />
                  </span>
                  <span className="tag">
                    {resource.data![p].configured
                      ? "KEY KONFIGURIERT"
                      : "NICHT KONFIGURIERT"}
                  </span>
                </div>
                <h2>{p === "openai" ? "OpenAI" : "Anthropic"}</h2>
                <p>Optionaler externer Anbieter.</p>
                <p className="muted">
                  Zugangsschlüssel bleiben auf dem Server. Modell und
                  Standard-Privacy müssen explizit eingestellt werden.
                </p>
              </Panel>
            ))}
          </div>
          <Panel title="Aktuelles Routing">
            <div className="settings-summary">
              <div>
                <span>Ausgewählter Anbieter</span>
                <strong>{resource.data.routing.provider}</strong>
              </div>
              <div>
                <span>Modell</span>
                <strong>
                  {resource.data.routing.model ||
                    "Erstes geladenes lokales Modell"}
                </strong>
              </div>
              <div>
                <span>Privacy</span>
                <strong>{resource.data.routing.privacy}</strong>
              </div>
              <div>
                <span>Cloud-Fallback</span>
                <strong>Deaktiviert</strong>
              </div>
            </div>
          </Panel>
          <Panel title="Integrationen">
            <div className="connection-line">
              <span>Social Publishing</span>
              <span className="muted">Adapter nicht konfiguriert</span>
            </div>
            <div className="connection-line">
              <span>Shopify / Commerce-Kennzahlen</span>
              <span className="muted">Nicht verbunden</span>
            </div>
            <div className="connection-line">
              <span>Community Publishing</span>
              <span className="muted">Adapter nicht konfiguriert</span>
            </div>
            <p className="footnote">
              Planung und Reviews laufen unabhängig. Die App behauptet keine
              Veröffentlichung ohne erfolgreiches Tool-Ergebnis.
            </p>
          </Panel>
        </>
      )}
    </>
  );
}

function SettingsPage() {
  const resource = useResource<Settings>("/settings", 0),
    [value, setValue] = useState<Settings | null>(null),
    [busy, setBusy] = useState(false),
    [message, setMessage] = useState(""),
    [error, setError] = useState<string | null>(null);
  useEffect(() => {
    if (resource.data) setValue(resource.data);
  }, [resource.data]);
  async function save(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setMessage("");
    try {
      setValue(await api("/settings", "PUT", value));
      setMessage(
        "Einstellungen gespeichert. Sie gelten für neue Ausführungsabschnitte.",
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <Head
        eyebrow="DEIN LOKALER BETRIEB"
        title="Einstellungen"
        description="Wissensquelle, Modell und Kontext kontrolliert konfigurieren."
      />
      <ResourceState {...resource} retry={resource.reload} />
      {value && (
        <div className="two-columns equal">
          <Panel title="Runtime konfigurieren">
            <form onSubmit={(e) => void save(e)}>
              <label>
                Sprache der Agenten
                <select
                  value={value.agent_language}
                  onChange={(e) =>
                    setValue({
                      ...value,
                      agent_language: e.target
                        .value as Settings["agent_language"],
                    })
                  }
                >
                  <option value="de">Deutsch</option>
                  <option value="en">English</option>
                </select>
              </label>
              <p className="muted">
                Gilt f?r neue Live-Ausf?hrungsabschnitte aller Agenten und
                Retrospektiven. Bestehende Ergebnisse bleiben erhalten;
                Simulationsbeispiele werden nicht ?bersetzt.
              </p>
              <label>
                Obsidian-Vault
                <input
                  value={value.vault_path}
                  required
                  onChange={(e) =>
                    setValue({ ...value, vault_path: e.target.value })
                  }
                />
              </label>
              <label>
                LM Studio Server
                <input
                  value={value.lm_studio_url}
                  required
                  onChange={(e) =>
                    setValue({ ...value, lm_studio_url: e.target.value })
                  }
                />
              </label>
              <label>
                Modellanbieter
                <select
                  value={value.provider}
                  onChange={(e) =>
                    setValue({
                      ...value,
                      provider: e.target.value as Settings["provider"],
                      privacy:
                        e.target.value === "lm_studio"
                          ? "local_only"
                          : "standard",
                      model: "",
                    })
                  }
                >
                  <option value="lm_studio">LM Studio · lokal</option>
                  <option value="openai">OpenAI · Cloud</option>
                  <option value="anthropic">Anthropic · Cloud</option>
                </select>
              </label>
              <label>
                Modell-ID
                <input
                  value={value.model}
                  onChange={(e) =>
                    setValue({ ...value, model: e.target.value })
                  }
                  placeholder={
                    value.provider === "lm_studio"
                      ? "Leer = erstes geladenes Modell"
                      : "Exakte Modell-ID eintragen"
                  }
                  required={value.provider !== "lm_studio"}
                />
              </label>
              <label>
                Privacy
                <select
                  value={value.privacy}
                  onChange={(e) =>
                    setValue({
                      ...value,
                      privacy: e.target.value as Settings["privacy"],
                    })
                  }
                >
                  <option value="local_only">Nur lokal · Cloud verboten</option>
                  <option value="standard">
                    Standard · explizit gewählter Anbieter
                  </option>
                </select>
              </label>
              <label>
                Maximale Ausgabetokens
                <input
                  type="number"
                  min={256}
                  max={16384}
                  value={value.max_output_tokens}
                  onChange={(e) =>
                    setValue({
                      ...value,
                      max_output_tokens: Number(e.target.value),
                    })
                  }
                />
              </label>
              {value.provider === "lm_studio" && (
                <label>
                  Lokaler Reasoning-Aufwand
                  <select
                    value={value.local_reasoning_effort}
                    onChange={(e) =>
                      setValue({
                        ...value,
                        local_reasoning_effort: e.target
                          .value as Settings["local_reasoning_effort"],
                      })
                    }
                  >
                    <option value="auto">Modellstandard</option>
                    <option value="none">
                      Keine erweiterte Reasoning-Phase
                    </option>
                    <option value="low">Niedrig</option>
                    <option value="medium">Mittel</option>
                    <option value="high">Hoch</option>
                  </select>
                  <small>
                    Nur verwenden, wenn das geladene Modell diese Option
                    unterstuetzt.
                  </small>
                </label>
              )}
              <label>
                Kontextbudget (Zeichen)
                <input
                  type="number"
                  min={2000}
                  max={24000}
                  value={value.context_chars}
                  onChange={(e) =>
                    setValue({
                      ...value,
                      context_chars: Number(e.target.value),
                    })
                  }
                />
              </label>
              {error && <ErrorBox message={error} />}
              <button className="button primary" disabled={busy}>
                {busy ? "Speichert …" : "Einstellungen speichern"}
                <Icon name="check" />
              </button>
              {message && (
                <p className="success-message" role="status">
                  {message}
                </p>
              )}
            </form>
          </Panel>
          <div>
            <Panel title="Klare Grenzen">
              <div className="principle">
                <Icon name="approvals" />
                <div>
                  <h3>Du entscheidest</h3>
                  <p>
                    Marke, Produkt, Preise und Produktion bleiben
                    freigabepflichtig.
                  </p>
                </div>
              </div>
              <div className="principle">
                <Icon name="knowledge" />
                <div>
                  <h3>Wissen bleibt erhalten</h3>
                  <p>
                    Obsidian ist dein organisatorisches Gedächtnis.
                    Prozesszustand liegt getrennt in der lokalen Runtime.
                  </p>
                </div>
              </div>
              <div className="principle">
                <Icon name="models" />
                <div>
                  <h3>Keine stille Cloud-Nutzung</h3>
                  <p>
                    Lokale Aufgaben scheitern sichtbar, wenn LM Studio fehlt.
                    Cloud-Nutzung verlangt einen ausgewählten Anbieter.
                  </p>
                </div>
              </div>
            </Panel>
            <Panel title="Zugangsschlüssel">
              <p>
                Optionale Schlüssel über <code>OPENAI_API_KEY</code> und{" "}
                <code>ANTHROPIC_API_KEY</code> in der lokalen <code>.env</code>{" "}
                konfigurieren. Die App zeigt oder speichert keine Schlüssel im
                Browser.
              </p>
              <p className="notice">
                Retrospektiven sind aktuell lokal-only. Cloud-Auswahl hebt ihre
                Skill-Privacy nicht auf.
              </p>
            </Panel>
          </div>
        </div>
      )}
    </>
  );
}

function Retrospectives({ id }: { id?: string }) {
  const list = useResource<Retrospective[]>("/retrospectives", 4000),
    runs = useResource<Page<Run>>("/runs?status=completed"),
    agents = useResource<Agent[]>("/agents", 0);
  const detail = useResource<Retrospective>(
    id ? `/retrospectives/${id}` : null,
    id ? 2500 : 0,
  );
  const [title, setTitle] = useState(
      "Was verbessern wir im nächsten Durchlauf?",
    ),
    [runIds, setRunIds] = useState<string[]>(
      new URLSearchParams(location.hash.split("?")[1] || "").get("run")
        ? [new URLSearchParams(location.hash.split("?")[1] || "").get("run")!]
        : [],
    ),
    [participants, setParticipants] = useState(["elena", "nora"]),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<string | null>(null),
    [rationale, setRationale] = useState(""),
    [result, setResult] = useState<
      Record<string, { evidence: string; rationale: string; outcome: string }>
    >({});
  async function create(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const r = await api<Retrospective>("/retrospectives", "POST", {
        title,
        run_ids: runIds,
        participant_ids: participants,
        idempotency_key: identity(),
      });
      location.hash = `/retrospectives/${r.id}`;
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  async function action(path: string, body: unknown) {
    setBusy(true);
    setError(null);
    try {
      await api(path, "POST", body);
      detail.reload();
      list.reload();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  const retro = detail.data;
  if (id)
    return (
      <>
        <a href="#/retrospectives" className="back-link">
          ← Retrospektiven
        </a>
        <ResourceState {...detail} retry={detail.reload} />
        {retro && (
          <>
            <Head
              eyebrow="EVIDENZ → ERKENNTNIS → EXPERIMENT"
              title={retro.title}
              description={`Moderation: Elena · ${retro.participant_ids.join(", ")} · ${date(retro.created_at)}`}
              action={
                <div className="row">
                  <Badge value={retro.mode} />
                  <Badge value={retro.status} />
                </div>
              }
            />
            {retro.error && <ErrorBox message={retro.error} />}
            <div className="notice">
              Verbesserungen sind Vorschläge. Freigabe erlaubt dokumentierte
              Sandbox-Experimente; produktive Softwareänderungen benötigen ein
              eigenes OpenSpec-Change.
            </div>
            <div className="row wrap">
              {retro.run_ids.map((r) => (
                <a className="tag" href={`#/runs/${r}`} key={r}>
                  Prozess {r.slice(0, 8)} ↗
                </a>
              ))}
            </div>
            <div className="contribution-grid">
              {retro.contributions.map((c) => (
                <Panel key={c.author_id}>
                  <div className="row">
                    <Avatar id={c.author_id} />
                    <h2>{c.author_id}</h2>
                  </div>
                  <h3>Beobachtung</h3>
                  <p>{c.observation}</p>
                  <h3>Interpretation</h3>
                  <p>{c.interpretation}</p>
                  <h3>Vorschlag</h3>
                  <p>{c.proposal}</p>
                  <p className="notice">
                    Evidenzlücke:{" "}
                    {c.evidence_gap ||
                      "Keine angegebene Lücke; Quellen trotzdem prüfen."}
                  </p>
                  <div className="tags">
                    {c.evidence_refs.map((r) => (
                      <a key={r} href={`#/runs/${r}`} className="tag">
                        Quelle {r.slice(0, 8)}
                      </a>
                    ))}
                  </div>
                </Panel>
              ))}
            </div>
            {retro.improvements.length > 0 && (
              <Panel title="Verbesserungsvorschläge">
                {retro.improvements.map((i, index) => (
                  <div className="improvement" key={index}>
                    <h3>{i.hypothesis}</h3>
                    <ArtifactView
                      value={{
                        Verantwortlich: i.owner_id,
                        Baseline: i.baseline,
                        Messgröße: i.metric,
                        Ziel: i.target,
                        Risiko: i.risk,
                        OpenSpec:
                          i.openspec_ref ||
                          "Separates Change erforderlich für Softwareumsetzung",
                      }}
                    />
                  </div>
                ))}
              </Panel>
            )}
            {error && <ErrorBox message={error} />}
            <Panel title="Review & nächste Schritte">
              {["awaiting_review", "held", "failed"].includes(retro.status) && (
                <>
                  <label>
                    Begründung
                    <textarea
                      value={rationale}
                      onChange={(e) => setRationale(e.target.value)}
                      rows={2}
                    />
                  </label>
                  <div className="row">
                    {(retro.status === "awaiting_review"
                      ? ["approve", "hold", "reject"]
                      : retro.status === "held"
                        ? ["resume", "reject"]
                        : ["retry", "reject"]
                    ).map((d) => (
                      <button
                        key={d}
                        disabled={busy}
                        className={
                          d === "approve"
                            ? "button primary"
                            : "button secondary"
                        }
                        onClick={() =>
                          void action(`/retrospectives/${id}/review`, {
                            decision: d,
                            revision: retro.revision,
                            rationale,
                            idempotency_key: identity(),
                          })
                        }
                      >
                        {labels[d]}
                      </button>
                    ))}
                  </div>
                </>
              )}
              {["collecting", "synthesizing", "draft"].includes(
                retro.status,
              ) && <Loading />}
              {retro.experiments.map((ex) => {
                const v = result[ex.id] || {
                  evidence: "",
                  rationale: "",
                  outcome: "inconclusive",
                };
                return (
                  <div className="experiment" key={ex.id}>
                    <div className="row between">
                      <h3>{ex.improvement.metric}</h3>
                      <Badge value={ex.status} />
                    </div>
                    <p>{ex.improvement.hypothesis}</p>
                    <p className="muted">
                      Baseline: {ex.improvement.baseline}
                      <br />
                      Ziel: {ex.improvement.target}
                    </p>
                    {ex.status === "proposed" && (
                      <button
                        disabled={busy}
                        className="button secondary"
                        onClick={() =>
                          void action(
                            `/retrospectives/${id}/experiments/${ex.id}/start`,
                            {
                              revision: retro.revision,
                              idempotency_key: identity(),
                            },
                          )
                        }
                      >
                        Manuelles Sandbox-Experiment starten
                      </button>
                    )}
                    {ex.status === "experimenting" && (
                      <form
                        onSubmit={(e) => {
                          e.preventDefault();
                          void action(
                            `/retrospectives/${id}/experiments/${ex.id}/result`,
                            {
                              ...v,
                              revision: retro.revision,
                              idempotency_key: identity(),
                            },
                          );
                        }}
                      >
                        <label>
                          Ergebnis
                          <select
                            value={v.outcome}
                            onChange={(e) =>
                              setResult({
                                ...result,
                                [ex.id]: { ...v, outcome: e.target.value },
                              })
                            }
                          >
                            <option value="inconclusive">
                              Nicht eindeutig
                            </option>
                            <option value="improved">Verbessert</option>
                            <option value="no_improvement">
                              Keine Verbesserung
                            </option>
                          </select>
                        </label>
                        <label>
                          Ergebnisbelege
                          <textarea
                            required
                            minLength={5}
                            value={v.evidence}
                            onChange={(e) =>
                              setResult({
                                ...result,
                                [ex.id]: { ...v, evidence: e.target.value },
                              })
                            }
                          />
                        </label>
                        <label>
                          Begründung im Vergleich zur Baseline
                          <textarea
                            required
                            minLength={5}
                            value={v.rationale}
                            onChange={(e) =>
                              setResult({
                                ...result,
                                [ex.id]: { ...v, rationale: e.target.value },
                              })
                            }
                          />
                        </label>
                        <button disabled={busy} className="button primary">
                          Ergebnis dokumentieren
                        </button>
                      </form>
                    )}
                    {ex.status === "closed" && (
                      <>
                        <Badge value={ex.outcome || "inconclusive"} />
                        <p>{ex.evidence}</p>
                        <p>{ex.rationale}</p>
                      </>
                    )}
                  </div>
                );
              })}
              {retro.status === "closed" && (
                <div className="notice">
                  {retro.mode === "simulation" ? (
                    "Simulation bleibt in der Runtime. Kein Vault-Export."
                  ) : retro.exported_path ? (
                    <span>In Obsidian gespeichert: {retro.exported_path}</span>
                  ) : (
                    <button
                      className="button secondary"
                      disabled={busy}
                      onClick={() =>
                        void action(`/retrospectives/${id}/export`, {
                          revision: retro.revision,
                          idempotency_key: identity(),
                        })
                      }
                    >
                      Freigegebenes Learning in Obsidian speichern
                    </button>
                  )}
                </div>
              )}
            </Panel>
          </>
        )}
      </>
    );
  return (
    <>
      <Head
        eyebrow="BESSER WERDEN, MIT BELEGEN"
        title="Retrospektiven-Räume"
        description="Elena moderiert. Dein Team reflektiert echte Ergebnisse. Du entscheidest über messbare Verbesserungen."
      />
      <div className="two-columns equal">
        <Panel title="Neue Retrospektive">
          <form onSubmit={(e) => void create(e)}>
            <label>
              Fragestellung
              <input
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </label>
            <label>Abgeschlossene Prozesse (max. 5, gleicher Modus)</label>
            <div className="checklist">
              {runs.data?.items.map((r) => (
                <label key={r.id}>
                  <input
                    type="checkbox"
                    checked={runIds.includes(r.id)}
                    onChange={(e) =>
                      setRunIds(
                        e.target.checked
                          ? [...runIds, r.id]
                          : runIds.filter((x) => x !== r.id),
                      )
                    }
                  />
                  <span>{r.title}</span>
                  <Badge value={r.mode} />
                </label>
              ))}
            </div>
            {!runs.data?.items.length && (
              <p className="notice">
                Zuerst einen Business-Prozess abschließen.
              </p>
            )}
            <label>Teilnehmende (max. 4)</label>
            <div className="participant-select">
              {agents.data?.map((a) => (
                <label key={a.id}>
                  <input
                    type="checkbox"
                    checked={participants.includes(a.id)}
                    onChange={(e) =>
                      setParticipants(
                        e.target.checked
                          ? [...participants, a.id]
                          : participants.filter((x) => x !== a.id),
                      )
                    }
                  />
                  <Avatar id={a.id} />
                  {a.name.split(" ")[0]}
                </label>
              ))}
            </div>
            {error && <ErrorBox message={error} />}
            <button
              className="button primary"
              disabled={
                busy ||
                !runIds.length ||
                participants.length > 4 ||
                runIds.length > 5 ||
                !participants.length
              }
            >
              Retrospektive starten <Icon name="retro" />
            </button>
          </form>
        </Panel>
        <Panel title="Deine Räume">
          <ResourceState {...list} retry={list.reload} />
          {list.data?.length ? (
            <div className="list">
              {list.data.map((r) => (
                <a href={`#/retrospectives/${r.id}`} key={r.id}>
                  <span className="list-icon">
                    <Icon name="retro" />
                  </span>
                  <div>
                    <strong>{r.title}</strong>
                    <small>
                      {date(r.created_at)} · {r.mode}
                    </small>
                  </div>
                  <Badge value={r.status} />
                </a>
              ))}
            </div>
          ) : (
            <Empty title="Noch kein Retrospektiven-Raum">
              Ein abgeschlossener Prozess ist der Ausgangspunkt für den nächsten
              Lernzyklus.
            </Empty>
          )}
        </Panel>
      </div>
    </>
  );
}

export default function App() {
  const route = useRoute(),
    [search, setSearch] = useState(""),
    [launch, setLaunch] = useState<Process | null>(null),
    [menu, setMenu] = useState(false),
    [connected, setConnected] = useState(true);
  const rootRoute = route.split("/")[0].split("?")[0],
    id = route.split("/")[1]?.split("?")[0];
  const agents = useResource<Agent[]>("/agents"),
    processes = useResource<Process[]>("/processes", 0),
    approvals = useResource<Approval[]>("/approvals", 4000);
  useEffect(() => {
    const events = new EventSource("/api/events/stream");
    events.onopen = () => setConnected(true);
    events.onerror = () => setConnected(false);
    return () => events.close();
  }, []);
  useEffect(() => {
    setMenu(false);
    setSearch("");
    window.scrollTo(0, 0);
  }, [route]);
  const close = useCallback(() => setLaunch(null), []);
  function launchFirst() {
    location.hash = "/processes";
  }
  const title = nav.find((n) => n[0] === rootRoute)?.[1] || "Workspace";
  let page: ReactNode;
  switch (rootRoute) {
    case "office":
      page = (
        <>
          <Head
            eyebrow="DIE FIRMA ALS GEMEINSAMER ORT"
            title="Willkommen im Office."
            description="Arbeitsplätze für Verantwortung. Raum für Ideen. Wähle einen Agenten oder starte mit Amancio einen Prozess."
            action={
              <button className="button primary" onClick={launchFirst}>
                <Icon name="plus" />
                Prozess starten
              </button>
            }
          />
          <ResourceState {...agents} retry={agents.reload} />
          <Panel>
            <Office
              agents={agents.data || []}
              onLaunch={launchFirst}
              stale={!connected || !!agents.error}
            />
          </Panel>
        </>
      );
      break;
    case "organization":
      page = <OrganizationPage launch={setLaunch} />;
      break;
    case "departments":
      page = <OrganizationPage department launch={setLaunch} />;
      break;
    case "processes":
      page = <Processes launch={setLaunch} filter={search} />;
      break;
    case "agents":
      page = id ? <AgentDetail id={id} /> : <Agents filter={search} />;
      break;
    case "skills":
      page = <Skills id={id} filter={search} />;
      break;
    case "runs":
      page = id ? <RunDetail id={id} /> : <Runs search={search} />;
      break;
    case "approvals":
      page = <Approvals />;
      break;
    case "knowledge":
      page = <Knowledge />;
      break;
    case "models":
      page = <ModelsPage />;
      break;
    case "settings":
      page = <SettingsPage />;
      break;
    case "retrospectives":
      page = <Retrospectives id={id} />;
      break;
    default:
      page = <Dashboard launch={launchFirst} agents={agents.data || []} />;
  }
  return (
    <div className="app">
      <aside className={`sidebar ${menu ? "open" : ""}`}>
        <a className="brand" href="#/dashboard">
          <span className="brand-mark">
            AB<span>✦</span>
          </span>
          <div>
            AMAUX BOZÉ<small>COMPANY OS</small>
          </div>
        </a>
        <div className="workspace-label">
          WORKSPACE <span>LOCAL V1</span>
        </div>
        <nav aria-label="Hauptnavigation">
          {nav.map(([key, label, icon], i) => (
            <a
              href={`#/${key}`}
              key={key}
              className={`${rootRoute === key ? "active" : ""} ${i === 8 ? "nav-separator" : ""}`}
              aria-current={rootRoute === key ? "page" : undefined}
            >
              <Icon name={icon} />
              <span>{label}</span>
              {key === "approvals" && !!approvals.data?.length && (
                <b>{approvals.data.length}</b>
              )}
            </a>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="local-status">
            <i className={`status-dot ${connected ? "" : "warning"}`} />
            <span>
              {connected ? "Lokaler Workspace" : "Verbindung unterbrochen"}
              <small>
                {connected
                  ? "Ereignisstream verbunden"
                  : "Aktivität bitte aktualisieren"}
              </small>
            </span>
          </div>
          <div className="founder-profile">
            <Avatar id="amancio" />
            <div>
              <strong>Amancio</strong>
              <small>Founder & Owner</small>
            </div>
            <span>⌄</span>
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="row">
            <button
              className="mobile-menu icon-button"
              aria-label="Navigation öffnen"
              onClick={() => setMenu(!menu)}
            >
              ☰
            </button>
            <span className="breadcrumb">
              Workspace <span>/</span> <strong>{title}</strong>
            </span>
          </div>
          <div className="row">
            <div className="top-search">
              <Icon name="search" size={16} />
              <input
                aria-label="Aktuelle Ansicht durchsuchen"
                placeholder="In dieser Ansicht suchen …"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                disabled={
                  !["agents", "skills", "runs", "processes"].includes(rootRoute)
                }
              />
            </div>
            <span className="local-pill">
              <i className="status-dot" />
              LOCAL
            </span>
            <a
              className="top-approval"
              href="#/approvals"
              aria-label="Freigaben öffnen"
            >
              <Icon name="approvals" />
              {!!approvals.data?.length && <i />}
            </a>
          </div>
        </header>
        <main key={route}>{page}</main>
        <footer className="app-footer">
          <span>
            AMAUX BOZÉ <span>·</span> Purpose in every decision.
          </span>
          <span>
            AI Native TOM/OS <span>·</span> Local-first
          </span>
        </footer>
      </div>
      {launch && (
        <Launcher
          process={launch}
          onClose={close}
          onStarted={(run) => {
            setLaunch(null);
            location.hash = `/runs/${run.id}`;
          }}
        />
      )}
      {processes.error && (
        <div className="global-error" role="alert">
          API nicht erreichbar. {processes.error}
        </div>
      )}
    </div>
  );
}
