import Link from "next/link";
import { redirect } from "next/navigation";
import { createClient } from "@/utils/supabase/server";
import { WeekAgenda, type AgendaSlot } from "@/components/WeekAgenda";

interface CourseRow {
  id: string;
  course_code: string;
  course_name: string;
  theory_room: string | null;
  theory_faculty: string | null;
  lab_room: string | null;
  lab_faculty: string | null;
}

interface SlotRow {
  id: string;
  day: string;
  start_time: string;
  end_time: string;
  slot_type: AgendaSlot["slot_type"];
  course_id: string | null;
  label: string | null;
  room: string | null;
}

export default async function Home() {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  // The layout above already redirects unauthenticated requests, but a
  // Server Component must not assume that holds — verify again here.
  if (!user) {
    redirect("/login");
  }

  const [{ data: courses }, { data: slots }] = await Promise.all([
    supabase.from("courses").select("*").returns<CourseRow[]>(),
    supabase.from("timetable_slots").select("*").returns<SlotRow[]>(),
  ]);

  const courseById = new Map((courses ?? []).map((c) => [c.id, c]));

  const agendaSlots: AgendaSlot[] = (slots ?? []).map((slot) => {
    const course = slot.course_id ? courseById.get(slot.course_id) : undefined;
    const isLab = slot.slot_type === "lab";
    const title = course ? course.course_name : (slot.label ?? "Untitled");
    const room = course ? (isLab ? course.lab_room : course.theory_room) : slot.room;
    const faculty = course ? (isLab ? course.lab_faculty : course.theory_faculty) : null;
    const meta =
      slot.slot_type === "break"
        ? ""
        : slot.slot_type === "activity"
          ? (slot.room ?? "")
          : [room ? `Rm ${room}` : null, faculty].filter(Boolean).join(" · ");

    return { id: slot.id, day: slot.day, start_time: slot.start_time, end_time: slot.end_time, slot_type: slot.slot_type, title, meta };
  });

  const hasTimetable = agendaSlots.length > 0;

  if (!hasTimetable) {
    return (
      <div className="card text-center py-10">
        <p className="text-sm opacity-70 mb-4">You haven&apos;t uploaded a timetable yet.</p>
        <Link href="/onboarding" className="btn btn-primary">
          Upload your timetable
        </Link>
      </div>
    );
  }

  return (
    <>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl">Your week</h1>
        <Link href="/onboarding" className="btn btn-secondary">
          + Add another
        </Link>
      </div>
      <WeekAgenda slots={agendaSlots} />
    </>
  );
}
