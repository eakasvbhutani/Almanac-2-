import { createClient } from "@/utils/supabase/server";
import { createOfficeTask, cycleOfficeTaskStatus, deleteOfficeTask } from "./actions";

interface OfficeTaskRow {
  id: string;
  task: string;
  due_date: string | null;
  status: string;
}

const STATUS_STYLE: Record<string, { bg: string; color: string }> = {
  "To do": { bg: "color-mix(in srgb, var(--color-text) 8%, transparent)", color: "var(--color-text)" },
  Doing: { bg: "var(--color-accent-100)", color: "var(--color-accent-700)" },
  Done: { bg: "var(--color-accent-2-100)", color: "var(--color-accent-2-700)" },
};

export default async function OfficeWorkPage() {
  const supabase = await createClient();
  const { data: tasks } = await supabase
    .from("office_tasks")
    .select("*")
    .order("created_at", { ascending: false })
    .returns<OfficeTaskRow[]>();

  return (
    <div>
      <h1 className="text-2xl mb-1">Office Work</h1>
      <p className="text-sm opacity-55 mb-4">A plain task list — not linked to courses.</p>

      <details className="card mb-4">
        <summary className="cursor-pointer text-sm font-semibold">+ Add task</summary>
        <form action={createOfficeTask} className="flex flex-col gap-3 mt-3">
          <input className="input" name="task" placeholder="Task" required />
          <div className="flex gap-3">
            <input className="input" name="dueDate" placeholder="Due date, e.g. Aug 20" />
            <select className="input" name="status" defaultValue="To do">
              <option>To do</option>
              <option>Doing</option>
              <option>Done</option>
            </select>
          </div>
          <button type="submit" className="btn btn-primary">
            Add
          </button>
        </form>
      </details>

      <div className="flex flex-col gap-2">
        {(tasks ?? []).length === 0 && <div className="card text-center opacity-60 py-8 text-sm">Nothing here yet.</div>}
        {(tasks ?? []).map((t) => {
          const style = STATUS_STYLE[t.status] ?? STATUS_STYLE["To do"];
          return (
            <div key={t.id} className="card flex flex-row items-center gap-3">
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold">{t.task}</div>
                {t.due_date && <div className="text-xs opacity-60 mt-1">{t.due_date}</div>}
              </div>
              <form action={cycleOfficeTaskStatus.bind(null, t.id, t.status)}>
                <button
                  type="submit"
                  className="text-xs rounded-full px-3 py-1.5 flex-none"
                  style={{ background: style.bg, color: style.color }}
                >
                  {t.status}
                </button>
              </form>
              <form action={deleteOfficeTask.bind(null, t.id)}>
                <button type="submit" className="btn btn-secondary" style={{ padding: "6px 12px", fontSize: 12 }}>
                  Delete
                </button>
              </form>
            </div>
          );
        })}
      </div>
    </div>
  );
}
