import { createClient } from "@/utils/supabase/server";
import { createTask, cycleTaskStatus, deleteTask } from "./actions";

interface TaskRow {
  id: string;
  task: string;
  due_date: string | null;
  status: string;
  course_id: string | null;
}

interface CourseOption {
  id: string;
  course_code: string;
}

const STATUS_STYLE: Record<string, { bg: string; color: string }> = {
  "To do": { bg: "color-mix(in srgb, var(--color-text) 8%, transparent)", color: "var(--color-text)" },
  Doing: { bg: "var(--color-accent-100)", color: "var(--color-accent-700)" },
  Done: { bg: "var(--color-accent-2-100)", color: "var(--color-accent-2-700)" },
};

export default async function TasksPage() {
  const supabase = await createClient();
  const [{ data: tasks }, { data: courses }] = await Promise.all([
    supabase.from("tasks").select("*").order("created_at", { ascending: false }).returns<TaskRow[]>(),
    supabase.from("courses").select("id, course_code").order("course_code").returns<CourseOption[]>(),
  ]);
  const courseById = new Map((courses ?? []).map((c) => [c.id, c.course_code]));

  return (
    <div>
      <h1 className="text-2xl mb-4">Tasks</h1>

      <details className="card mb-4">
        <summary className="cursor-pointer text-sm font-semibold">+ Add task</summary>
        <form action={createTask} className="flex flex-col gap-3 mt-3">
          <input className="input" name="task" placeholder="Task" required />
          <div className="flex gap-3">
            <input className="input" name="dueDate" placeholder="Due date, e.g. Aug 20" />
            <select className="input" name="status" defaultValue="To do">
              <option>To do</option>
              <option>Doing</option>
              <option>Done</option>
            </select>
          </div>
          <select className="input" name="courseId" defaultValue="">
            <option value="">No course</option>
            {(courses ?? []).map((c) => (
              <option key={c.id} value={c.id}>
                {c.course_code}
              </option>
            ))}
          </select>
          <button type="submit" className="btn btn-primary">
            Add
          </button>
        </form>
      </details>

      <div className="flex flex-col gap-2">
        {(tasks ?? []).length === 0 && <div className="card text-center opacity-60 py-8 text-sm">No tasks yet.</div>}
        {(tasks ?? []).map((t) => {
          const style = STATUS_STYLE[t.status] ?? STATUS_STYLE["To do"];
          return (
            <div key={t.id} className="card flex flex-row items-center gap-3">
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold">{t.task}</div>
                <div className="text-xs opacity-60 mt-1 flex gap-2 items-center flex-wrap">
                  {t.due_date && <span>{t.due_date}</span>}
                  {t.course_id && courseById.get(t.course_id) && (
                    <span
                      className="rounded-full px-2 py-0.5"
                      style={{ background: "color-mix(in srgb, var(--color-text) 8%, transparent)" }}
                    >
                      {courseById.get(t.course_id)}
                    </span>
                  )}
                </div>
              </div>
              <form action={cycleTaskStatus.bind(null, t.id, t.status)}>
                <button
                  type="submit"
                  className="text-xs rounded-full px-3 py-1.5 flex-none"
                  style={{ background: style.bg, color: style.color }}
                >
                  {t.status}
                </button>
              </form>
              <form action={deleteTask.bind(null, t.id)}>
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
