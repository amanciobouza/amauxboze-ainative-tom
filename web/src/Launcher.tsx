import { useEffect, useRef, useState } from "react";
import { api, identity, useResource } from "./api";
import { Badge, ErrorBox, Icon, Loading } from "./components";
import type { Mode, Page, Process, Run } from "./types";

export default function Launcher({
  process,
  onClose,
  onStarted,
}: {
  process: Process | null;
  onClose: () => void;
  onStarted: (run: Run) => void;
}) {
  const [mode, setMode] = useState<Mode>("live"),
    [input, setInput] = useState<Record<string, string>>({}),
    [busy, setBusy] = useState(false),
    [error, setError] = useState<string | null>(null);
  const key = useRef(identity()),
    dialog = useRef<HTMLDivElement>(null);
  const approved = useResource<Page<Run>>(
    `/runs?process_id=watch-development&status=completed&mode=${mode}`,
  );
  useEffect(() => {
    if (process) {
      setInput(
        Object.fromEntries(
          Object.entries(process.input_schema.properties || {}).map(
            ([k, v]) => [
              k,
              v.type === "object"
                ? JSON.stringify(v.default || {})
                : Array.isArray(v.default)
                  ? v.default.join("\n")
                  : String(v.default || ""),
            ],
          ),
        ),
      );
      key.current = identity();
    }
  }, [process]);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement;
    const timer = setTimeout(
      () =>
        dialog.current
          ?.querySelector<HTMLElement>("select, input, textarea, button")
          ?.focus(),
      0,
    );
    function keyboard(e: KeyboardEvent) {
      if (e.key === "Escape" && !busy) onClose();
      if (e.key === "Tab") {
        const elements = dialog.current?.querySelectorAll<HTMLElement>(
          "button:not(:disabled),a,select,input,textarea",
        );
        if (!elements?.length) return;
        const first = elements[0],
          last = elements[elements.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }
    document.addEventListener("keydown", keyboard);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("keydown", keyboard);
      previous?.focus();
    };
  }, [onClose, busy]);
  if (!process) return null;
  async function start(e: React.FormEvent) {
    e.preventDefault();
    if (!process) return;
    setBusy(true);
    setError(null);
    try {
      const payload = Object.fromEntries(
        Object.entries(process.input_schema.properties || {}).map(([k, s]) => [
          k,
          s.type === "array"
            ? (input[k] || "")
                .split("\n")
                .map((v) => v.trim())
                .filter(Boolean)
            : s.type === "object"
              ? JSON.parse(input[k] || "{}")
              : input[k] || "",
        ]),
      );
      const run = await api<Run>("/runs", "POST", {
        process_id: process.id,
        version: process.version,
        mode,
        input: payload,
        idempotency_key: key.current,
      });
      onStarted(run);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div
      className="modal-backdrop"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget && !busy) onClose();
      }}
    >
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="launch-title"
        ref={dialog}
      >
        <div className="row between">
          <span className="eyebrow">NEUER PROZESS · V{process.version}</span>
          <button
            className="icon-button"
            aria-label="Schließen"
            disabled={busy}
            onClick={onClose}
          >
            <Icon name="close" />
          </button>
        </div>
        <h2 id="launch-title">{process.name}</h2>
        <p className="muted">{process.description}</p>
        <form onSubmit={(e) => void start(e)}>
          <label>
            Ausführung
            <select
              value={mode}
              onChange={(e) => {
                setMode(e.target.value as Mode);
                key.current = identity();
              }}
            >
              <option value="live">Live · echtes konfiguriertes Modell</option>
              <option value="simulation">
                Simulation · keine externen Aktionen
              </option>
            </select>
          </label>
          <div
            className={`notice ${mode === "simulation" ? "simulation" : ""}`}
          >
            <Badge value={mode} />
            <span>
              {mode === "simulation"
                ? "Demonstrationsdaten. Keine belegten Ergebnisse, keine Veröffentlichung und keine Vault-Schreibzugriffe."
                : "Aufgaben laufen über das ausgewählte Modell. Lokale Aufgaben wechseln niemals automatisch in die Cloud."}
            </span>
          </div>
          {process.live_limitation && mode === "live" && (
            <p className="notice">{process.live_limitation}</p>
          )}
          {Object.entries(process.input_schema.properties || {}).map(
            ([k, s]) => (
              <label key={k}>
                {s.title || k}
                {process.input_schema.required?.includes(k) && (
                  <span className="required"> *</span>
                )}
                {k === "approved_run_id" ? (
                  <select
                    required
                    value={input[k] || ""}
                    onChange={(e) => {
                      setInput({ ...input, [k]: e.target.value });
                      key.current = identity();
                    }}
                  >
                    <option value="">Freigegebenes Produkt wählen …</option>
                    {approved.data?.items
                      .filter((r) => r.state.production_decision === "approve")
                      .map((r) => (
                        <option key={r.id} value={r.id}>
                          {r.title} · {r.id.slice(0, 8)}
                        </option>
                      ))}
                  </select>
                ) : [
                    "product_working_title",
                    "product_id",
                    "source",
                    "geography",
                    "audience",
                  ].includes(k) ? (
                  <input
                    required={process.input_schema.required?.includes(k)}
                    value={input[k] || ""}
                    onChange={(e) => {
                      setInput({ ...input, [k]: e.target.value });
                      key.current = identity();
                    }}
                  />
                ) : (
                  <textarea
                    rows={s.type === "object" ? 3 : 3}
                    required={process.input_schema.required?.includes(k)}
                    value={input[k] || ""}
                    onChange={(e) => {
                      setInput({ ...input, [k]: e.target.value });
                      key.current = identity();
                    }}
                  />
                )}
              </label>
            ),
          )}
          {process.id === "product-launch" && approved.loading && <Loading />}
          {process.id === "product-launch" &&
            approved.data?.items.length === 0 && (
              <p className="notice">
                Zuerst eine Produktentwicklung inklusive Produktionsfreigabe im
                selben Modus abschließen.
              </p>
            )}
          <p className="approval-note">
            <Icon name="approvals" />
            {process.approval_summary}
          </p>
          {error && <ErrorBox message={error} />}
          <div className="row end">
            <button
              type="button"
              className="button secondary"
              disabled={busy}
              onClick={onClose}
            >
              Schließen
            </button>
            <button className="button primary" disabled={busy}>
              {busy ? "Wird gestartet …" : "Prozess starten"}
              <Icon name="arrow" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
