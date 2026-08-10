import Link from "next/link";
import { createClient } from "@/utils/supabase/server";
import { createCourse } from "./actions";

interface CourseRow {
  id: string;
  course_code: string;
  course_name: string;
  semester: string | null;
  credits: number | null;
  grade: string | null;
  theory_room: string | null;
  lab_room: string | null;
}

export default async function CoursesPage() {
  const supabase = await createClient();
  const { data: courses } = await supabase.from("courses").select("*").order("course_code").returns<CourseRow[]>();

  return (
    <div>
      <h1 className="text-2xl mb-4">Courses</h1>

      <details className="card mb-4">
        <summary className="cursor-pointer text-sm font-semibold">+ Add course</summary>
        <form action={createCourse} className="flex flex-col gap-3 mt-3">
          <div className="flex gap-3">
            <input className="input" name="courseCode" placeholder="Course code, e.g. ECE-201" required />
            <input className="input" name="semester" placeholder="Semester" />
          </div>
          <input className="input" name="courseName" placeholder="Course name" required />
          <div className="flex gap-3">
            <input className="input" name="credits" type="number" placeholder="Credits" />
            <input className="input" name="grade" placeholder="Grade" />
          </div>
          <div className="flex gap-3">
            <input className="input" name="theoryFaculty" placeholder="Theory faculty" />
            <input className="input" name="theoryRoom" placeholder="Theory room" />
          </div>
          <div className="flex gap-3">
            <input className="input" name="labFaculty" placeholder="Lab faculty" />
            <input className="input" name="labRoom" placeholder="Lab room" />
          </div>
          <button type="submit" className="btn btn-primary">
            Add
          </button>
        </form>
      </details>

      <div className="flex flex-col gap-2">
        {(courses ?? []).length === 0 && <div className="card text-center opacity-60 py-8 text-sm">No courses yet.</div>}
        {(courses ?? []).map((c) => (
          <Link key={c.id} href={`/courses/${c.id}`} className="card flex flex-row items-center gap-3 no-underline text-inherit">
            <div className="text-xs opacity-55 flex-none w-20">{c.course_code}</div>
            <div className="flex-1 min-w-0 text-sm font-semibold">{c.course_name}</div>
            {c.grade && (
              <span
                className="text-xs rounded-full px-2.5 py-1 flex-none"
                style={{ border: "1px solid var(--color-accent)", color: "var(--color-accent)" }}
              >
                {c.grade}
              </span>
            )}
          </Link>
        ))}
      </div>
    </div>
  );
}
