import { createClient } from "@/utils/supabase/server";
import { createNote, deleteNote } from "./actions";

interface NoteRow {
  id: string;
  note: string;
  body: string | null;
  course_id: string | null;
  updated_at: string;
}

interface CourseOption {
  id: string;
  course_code: string;
}

export default async function NotesPage() {
  const supabase = await createClient();
  const [{ data: notes }, { data: courses }] = await Promise.all([
    supabase.from("notes").select("*").order("updated_at", { ascending: false }).returns<NoteRow[]>(),
    supabase.from("courses").select("id, course_code").order("course_code").returns<CourseOption[]>(),
  ]);
  const courseById = new Map((courses ?? []).map((c) => [c.id, c.course_code]));

  return (
    <div>
      <h1 className="text-2xl mb-4">Notes</h1>

      <details className="card mb-4">
        <summary className="cursor-pointer text-sm font-semibold">+ Add note</summary>
        <form action={createNote} className="flex flex-col gap-3 mt-3">
          <input className="input" name="note" placeholder="Note title" required />
          <select className="input" name="courseId" defaultValue="">
            <option value="">No course</option>
            {(courses ?? []).map((c) => (
              <option key={c.id} value={c.id}>
                {c.course_code}
              </option>
            ))}
          </select>
          <textarea className="input" name="body" placeholder="Body" style={{ minHeight: 80 }} />
          <button type="submit" className="btn btn-primary">
            Add
          </button>
        </form>
      </details>

      <div className="grid gap-3" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
        {(notes ?? []).length === 0 && <div className="card text-center opacity-60 py-8 text-sm">No notes yet.</div>}
        {(notes ?? []).map((n) => (
          <div key={n.id} className="card">
            <div className="flex items-start justify-between gap-2">
              {n.course_id && courseById.get(n.course_id) && (
                <div className="text-xs uppercase tracking-wide" style={{ color: "var(--color-accent)" }}>
                  {courseById.get(n.course_id)}
                </div>
              )}
              <form action={deleteNote.bind(null, n.id)} className="ml-auto">
                <button type="submit" className="btn btn-secondary" style={{ padding: "2px 8px", fontSize: 11 }}>
                  Delete
                </button>
              </form>
            </div>
            <div className="text-base font-semibold mt-1">{n.note}</div>
            {n.body && <p className="text-sm opacity-80 mt-1">{n.body}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
