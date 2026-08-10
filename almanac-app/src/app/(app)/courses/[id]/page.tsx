import Link from "next/link";
import { notFound } from "next/navigation";
import { createClient } from "@/utils/supabase/server";
import { updateCourse, deleteCourse } from "../actions";

interface CourseRow {
  id: string;
  course_code: string;
  course_name: string;
  semester: string | null;
  credits: number | null;
  grade: string | null;
  theory_faculty: string | null;
  theory_room: string | null;
  lab_faculty: string | null;
  lab_room: string | null;
}

interface TaskRow {
  id: string;
  task: string;
  due_date: string | null;
  status: string;
}

interface NoteRow {
  id: string;
  note: string;
  body: string | null;
}

export default async function CourseDetailPage(props: PageProps<"/courses/[id]">) {
  const { id } = await props.params;
  const supabase = await createClient();

  const [{ data: course }, { data: tasks }, { data: notes }] = await Promise.all([
    supabase.from("courses").select("*").eq("id", id).maybeSingle<CourseRow>(),
    supabase.from("tasks").select("id, task, due_date, status").eq("course_id", id).returns<TaskRow[]>(),
    supabase.from("notes").select("id, note, body").eq("course_id", id).returns<NoteRow[]>(),
  ]);

  if (!course) {
    notFound();
  }

  return (
    <div>
      <Link href="/courses" className="text-sm opacity-70">
        ← Courses
      </Link>

      <div className="flex items-start justify-between gap-3 mt-3 mb-1">
        <div>
          <div className="text-xs uppercase tracking-wide" style={{ color: "var(--color-accent)" }}>
            {course.course_code}
          </div>
          <h1 className="text-2xl">{course.course_name}</h1>
        </div>
        {course.grade && (
          <span className="text-xs rounded-full px-2.5 py-1 flex-none" style={{ border: "1px solid var(--color-accent)", color: "var(--color-accent)" }}>
            {course.grade}
          </span>
        )}
      </div>
      <p className="text-sm opacity-65 mb-6">
        {course.theory_faculty ?? "—"} · Rm {course.theory_room ?? "—"}
        {course.lab_faculty && (
          <>
            {" "}
            &nbsp;·&nbsp; Lab: {course.lab_faculty} · Rm {course.lab_room ?? "—"}
          </>
        )}
      </p>

      <details className="card mb-6">
        <summary className="cursor-pointer text-sm font-semibold">Edit course</summary>
        <form action={updateCourse.bind(null, course.id)} className="flex flex-col gap-3 mt-3">
          <div className="flex gap-3">
            <input className="input" name="courseCode" defaultValue={course.course_code} required />
            <input className="input" name="semester" defaultValue={course.semester ?? ""} placeholder="Semester" />
          </div>
          <input className="input" name="courseName" defaultValue={course.course_name} required />
          <div className="flex gap-3">
            <input className="input" name="credits" type="number" defaultValue={course.credits ?? ""} placeholder="Credits" />
            <input className="input" name="grade" defaultValue={course.grade ?? ""} placeholder="Grade" />
          </div>
          <div className="flex gap-3">
            <input className="input" name="theoryFaculty" defaultValue={course.theory_faculty ?? ""} placeholder="Theory faculty" />
            <input className="input" name="theoryRoom" defaultValue={course.theory_room ?? ""} placeholder="Theory room" />
          </div>
          <div className="flex gap-3">
            <input className="input" name="labFaculty" defaultValue={course.lab_faculty ?? ""} placeholder="Lab faculty" />
            <input className="input" name="labRoom" defaultValue={course.lab_room ?? ""} placeholder="Lab room" />
          </div>
          <div className="flex gap-3">
            <button type="submit" className="btn btn-primary">
              Save
            </button>
            <button type="submit" formAction={deleteCourse.bind(null, course.id)} className="btn btn-secondary" style={{ color: "var(--color-accent-700)" }}>
              Delete course
            </button>
          </div>
        </form>
      </details>

      <div className="text-sm font-semibold mb-2">Tasks linked to this course</div>
      <div className="flex flex-col gap-2 mb-6">
        {(tasks ?? []).length === 0 && <div className="text-sm opacity-55">None yet.</div>}
        {(tasks ?? []).map((t) => (
          <div key={t.id} className="card flex flex-row items-center justify-between gap-3">
            <span className="text-sm">{t.task}</span>
            <span className="text-xs opacity-60">{t.status}</span>
          </div>
        ))}
        <Link href="/tasks" className="text-xs opacity-60 underline">
          Manage in Tasks →
        </Link>
      </div>

      <div className="text-sm font-semibold mb-2">Notes linked to this course</div>
      <div className="flex flex-col gap-2">
        {(notes ?? []).length === 0 && <div className="text-sm opacity-55">None yet.</div>}
        {(notes ?? []).map((n) => (
          <div key={n.id} className="card">
            <div className="text-sm font-semibold">{n.note}</div>
            {n.body && <p className="text-xs opacity-70 mt-1">{n.body}</p>}
          </div>
        ))}
        <Link href="/notes" className="text-xs opacity-60 underline">
          Manage in Notes →
        </Link>
      </div>
    </div>
  );
}
