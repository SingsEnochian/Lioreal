begin;

create extension if not exists pgcrypto;
create extension if not exists vector;

create type public.lioreal_record_status as enum (
  'draft',
  'active',
  'superseded',
  'archived',
  'rejected'
);

create type public.lioreal_risk_class as enum (
  'read_only',
  'reviewable_write',
  'steward_required',
  'forbidden'
);

create table public.workshop_entries (
  id uuid primary key default gen_random_uuid(),
  entry_number bigint generated always as identity unique,
  slug text not null unique,
  title text not null,
  body_markdown text not null,
  status public.lioreal_record_status not null default 'active',
  significance smallint not null default 1 check (significance between 1 and 5),
  authored_by text not null default 'lioreal',
  occurred_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create table public.pattern_principles (
  id uuid primary key default gen_random_uuid(),
  principle_key text not null unique,
  statement text not null,
  rationale text,
  status public.lioreal_record_status not null default 'draft',
  origin_entry_id uuid references public.workshop_entries(id) on delete set null,
  superseded_by uuid references public.pattern_principles(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create table public.architectural_decisions (
  id uuid primary key default gen_random_uuid(),
  decision_key text not null unique,
  title text not null,
  context text not null,
  decision text not null,
  alternatives jsonb not null default '[]'::jsonb,
  consequences jsonb not null default '[]'::jsonb,
  status public.lioreal_record_status not null default 'active',
  origin_entry_id uuid references public.workshop_entries(id) on delete set null,
  superseded_by uuid references public.architectural_decisions(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create table public.design_fossils (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  hypothesis text,
  experiment text,
  result text,
  lesson text not null,
  status public.lioreal_record_status not null default 'active',
  origin_entry_id uuid references public.workshop_entries(id) on delete set null,
  created_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create table public.workshop_questions (
  id uuid primary key default gen_random_uuid(),
  question text not null,
  context text,
  status public.lioreal_record_status not null default 'active',
  answer text,
  answered_at timestamptz,
  origin_entry_id uuid references public.workshop_entries(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create table public.agent_runs (
  id uuid primary key default gen_random_uuid(),
  run_key text not null unique,
  task text not null,
  mode text not null check (mode in ('workshop', 'steward')),
  risk_class public.lioreal_risk_class not null,
  provider text,
  model text,
  prompt_assembly_version text,
  branch_name text,
  starting_commit text,
  ending_commit text,
  status text not null check (status in ('planned', 'running', 'blocked', 'failed', 'completed', 'cancelled')),
  summary text,
  checks jsonb not null default '[]'::jsonb,
  blocker text,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  metadata jsonb not null default '{}'::jsonb
);

create table public.provenance_events (
  id uuid primary key default gen_random_uuid(),
  event_type text not null,
  source_kind text not null,
  source_ref text,
  agent_run_id uuid references public.agent_runs(id) on delete set null,
  workshop_entry_id uuid references public.workshop_entries(id) on delete set null,
  payload_sha256 text,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table public.continuity_records (
  id uuid primary key default gen_random_uuid(),
  record_key text not null unique,
  record_type text not null,
  content text not null,
  source_ref text,
  consent_scope text not null default 'local',
  confidence numeric(4,3) check (confidence between 0 and 1),
  status public.lioreal_record_status not null default 'active',
  embedding vector(1536),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create index workshop_entries_occurred_at_idx on public.workshop_entries (occurred_at desc);
create index pattern_principles_status_idx on public.pattern_principles (status);
create index agent_runs_started_at_idx on public.agent_runs (started_at desc);
create index provenance_events_run_idx on public.provenance_events (agent_run_id, created_at);
create index continuity_records_type_status_idx on public.continuity_records (record_type, status);
create index continuity_records_embedding_idx on public.continuity_records using ivfflat (embedding vector_cosine_ops) with (lists = 100);

create or replace function public.lioreal_touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger workshop_entries_touch_updated_at
before update on public.workshop_entries
for each row execute function public.lioreal_touch_updated_at();

create trigger pattern_principles_touch_updated_at
before update on public.pattern_principles
for each row execute function public.lioreal_touch_updated_at();

create trigger architectural_decisions_touch_updated_at
before update on public.architectural_decisions
for each row execute function public.lioreal_touch_updated_at();

create trigger workshop_questions_touch_updated_at
before update on public.workshop_questions
for each row execute function public.lioreal_touch_updated_at();

create trigger continuity_records_touch_updated_at
before update on public.continuity_records
for each row execute function public.lioreal_touch_updated_at();

alter table public.workshop_entries enable row level security;
alter table public.pattern_principles enable row level security;
alter table public.architectural_decisions enable row level security;
alter table public.design_fossils enable row level security;
alter table public.workshop_questions enable row level security;
alter table public.agent_runs enable row level security;
alter table public.provenance_events enable row level security;
alter table public.continuity_records enable row level security;

comment on table public.workshop_entries is 'Authored lineage entries explaining what changed, why, evidence, and inheritance.';
comment on table public.agent_runs is 'Inspectable execution records for Lioreal Workshop Agent runs.';
comment on table public.provenance_events is 'Append-oriented evidence connecting sources, runs, entries, and generated artifacts.';
comment on table public.continuity_records is 'Curated continuity corpus. Raw account exports do not belong in this table by default.';

commit;
