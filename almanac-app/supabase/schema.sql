-- Almanac schema. Every table is scoped to auth.uid() via Row Level Security,
-- so each of your ~10 users only ever sees their own data even though
-- everyone shares the same database.

create extension if not exists "pgcrypto";

-- One row per signed-up user, created automatically by the trigger below.
create table if not exists profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  section text default '3EC-ACT123',
  created_at timestamptz not null default now()
);

create table if not exists courses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  course_code text not null,
  course_name text not null,
  semester text,
  credits int,
  grade text,
  theory_faculty text,
  theory_room text,
  lab_faculty text,
  lab_room text,
  created_at timestamptz not null default now()
);

create table if not exists timetable_slots (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  day text not null check (day in ('Mon','Tue','Wed','Thu','Fri','Sat','Sun')),
  start_time text not null,
  end_time text not null,
  slot_type text not null check (slot_type in ('theory','lab','activity','break')),
  course_id uuid references courses(id) on delete set null,
  label text,
  room text,
  created_at timestamptz not null default now()
);

create table if not exists tasks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  course_id uuid references courses(id) on delete set null,
  task text not null,
  due_date text,
  status text not null default 'To do' check (status in ('To do','Doing','Done')),
  created_at timestamptz not null default now()
);

create table if not exists office_tasks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  task text not null,
  due_date text,
  status text not null default 'To do' check (status in ('To do','Doing','Done')),
  created_at timestamptz not null default now()
);

create table if not exists notes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  course_id uuid references courses(id) on delete set null,
  note text not null,
  body text,
  updated_at timestamptz not null default now()
);

-- Raw upload record for every timetable JPG/PDF a user submits, plus what
-- the parser produced — kept around so a bad parse can be reviewed/retried.
create table if not exists timetable_uploads (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  storage_path text not null,
  status text not null default 'pending' check (status in ('pending','parsed','failed')),
  parsed_json jsonb,
  error text,
  created_at timestamptz not null default now()
);

alter table profiles enable row level security;
alter table courses enable row level security;
alter table timetable_slots enable row level security;
alter table tasks enable row level security;
alter table office_tasks enable row level security;
alter table notes enable row level security;
alter table timetable_uploads enable row level security;

create policy "own profile" on profiles for select using (auth.uid() = id);
create policy "update own profile" on profiles for update using (auth.uid() = id);

create policy "own courses" on courses for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own timetable_slots" on timetable_slots for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own tasks" on tasks for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own office_tasks" on office_tasks for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own notes" on notes for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own timetable_uploads" on timetable_uploads for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Auto-create a profile row whenever someone signs up.
-- search_path is pinned (not left mutable) and PUBLIC's implicit EXECUTE
-- grant is revoked so this can only ever run as the auth.users trigger,
-- never called directly over the REST RPC endpoint.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, full_name)
  values (new.id, new.raw_user_meta_data->>'full_name');
  return new;
end;
$$;

revoke execute on function public.handle_new_user() from public;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure handle_new_user();

-- Private storage bucket for uploaded timetable files (JPG/PNG/PDF).
insert into storage.buckets (id, name, public)
values ('timetables', 'timetables', false)
on conflict (id) do nothing;

create policy "own timetable files read" on storage.objects for select
  using (bucket_id = 'timetables' and auth.uid()::text = (storage.foldername(name))[1]);
create policy "own timetable files insert" on storage.objects for insert
  with check (bucket_id = 'timetables' and auth.uid()::text = (storage.foldername(name))[1]);
create policy "own timetable files delete" on storage.objects for delete
  using (bucket_id = 'timetables' and auth.uid()::text = (storage.foldername(name))[1]);
