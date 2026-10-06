export type Mode = "live" | "simulation";
export type Status =
  | "queued"
  | "running"
  | "waiting_approval"
  | "held"
  | "failed"
  | "completed"
  | "rejected"
  | "cancelled";
export interface Assignment {
  run_id: string;
  title: string;
  stage: string;
  status?: string;
  mode: Mode;
}
export interface Activity {
  state: string;
  active_assignments: Assignment[];
  waiting_assignments: Assignment[];
  observed_at: string;
  freshness: string;
}
export interface Skill {
  id: string;
  version: string;
  purpose: string;
  inputs: Schema;
  outputs: Schema;
  context: string[];
  allowed_tools: string[];
  model: Record<string, unknown>;
}
export interface Schema {
  type: string;
  required?: string[];
  properties?: Record<string, Schema>;
  title?: string;
  default?: unknown;
  items?: Schema;
}
export interface Agent {
  id: string;
  name: string;
  role: string;
  mission: string;
  skills: string[];
  communication_instructions: string[];
  tools: { read: string[]; write: string[]; actions: string[] };
  approval_boundaries: string[];
  activity: Activity;
  department_ids?: string[];
  biography?: string;
  biography_source?: string;
  skill_details?: Skill[];
  unavailable_skills?: string[];
  history?: Attempt[];
  history_total?: number;
}
export interface Department {
  id: string;
  name: string;
  mission: string;
  member_ids: string[];
}
export interface Node {
  id: string;
  kind: "human" | "agent";
  display_name: string;
  role: string;
  mission: string;
  parent_id: string | null;
  department_ids: string[];
}
export interface Organization {
  nodes: Node[];
  departments: Department[];
  coordinator_id: string;
}
export interface Process {
  id: string;
  version: string;
  name: string;
  description: string;
  owner_department_id: string;
  participant_department_ids: string[];
  input_schema: Schema;
  approval_summary: string;
  external_action: string | null;
  live_limitation: string | null;
}
export interface Approval {
  id: string;
  run_id: string;
  revision: number;
  action: string;
  kind: "approval" | "recovery";
  allowed_decisions: string[];
  context: Record<string, unknown>;
  status: string;
  created_at: string;
}
export interface Run {
  id: string;
  process_id: string;
  title: string;
  mode: Mode;
  status: Status;
  current_stage: string;
  active_agent_ids: string[];
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  revision: number;
  input: Record<string, unknown>;
  state: Record<string, unknown>;
  error: string | null;
  approval_id: string | null;
  allowed_commands: string[];
  attempts?: Attempt[];
  events?: RuntimeEvent[];
  approval?: Approval | null;
}
export interface Attempt {
  id: string;
  run_id: string;
  agent_id: string;
  skill_id: string;
  status: string;
  attempt_number: number;
  trace_id: string;
  started_at: string;
  completed_at: string | null;
  artifact: Record<string, unknown> | null;
  error: string | null;
  provider: string | null;
  model: string | null;
  usage: Record<string, unknown>;
}
export interface RuntimeEvent {
  id: number;
  run_id: string;
  type: string;
  timestamp: string;
  payload: Record<string, unknown>;
}
export interface KPI {
  id: string;
  name: string;
  value: number | null;
  unit: string;
  formula: string;
  source: string;
  coverage: string;
  observed_at: string;
  unavailable_reason: string | null;
  filter_status: string | null;
}
export interface DashboardData {
  mode: Mode;
  period_start: string;
  period_end: string;
  kpis: KPI[];
  recent_runs: Run[];
  pending_approvals: Approval[];
  blocked_runs: Run[];
  learnings: {
    run_id: string;
    title: string;
    type: string;
    content: unknown;
  }[];
}
export interface Health {
  status: string;
  timestamp: string;
  knowledge_available: boolean;
  publishing: string;
  local_only: boolean;
}
export interface Settings {
  agent_language: "de" | "en";
  vault_path: string;
  lm_studio_url: string;
  provider: "lm_studio" | "openai" | "anthropic";
  model: string;
  privacy: "local_only" | "standard";
  context_chars: number;
  max_output_tokens: number;
  local_reasoning_effort: "auto" | "none" | "low" | "medium" | "high";
}
export interface Models {
  lm_studio: { available: boolean; models: string[]; reason: string | null };
  openai: { configured: boolean };
  anthropic: { configured: boolean };
  routing: Omit<Settings, "vault_path">;
  cloud_fallback: boolean;
}
export interface Contribution {
  author_id: string;
  evidence_refs: string[];
  observation: string;
  interpretation: string;
  proposal: string;
  evidence_gap: string;
}
export interface Improvement {
  owner_id: string;
  hypothesis: string;
  baseline: string;
  metric: string;
  target: string;
  risk: string;
  openspec_ref: string | null;
}
export interface Experiment {
  id: string;
  improvement: Improvement;
  status: string;
  evidence: string;
  outcome: string | null;
  rationale: string;
}
export interface Retrospective {
  id: string;
  title: string;
  run_ids: string[];
  participant_ids: string[];
  mode: Mode;
  status: string;
  revision: number;
  created_at: string;
  updated_at: string;
  contributions: Contribution[];
  improvements: Improvement[];
  experiments: Experiment[];
  error: string | null;
  exported_path: string | null;
}
export interface Page<T> {
  items: T[];
  total: number;
  offset: number;
}
