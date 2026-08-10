"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { createClient } from "@/utils/supabase/server";

function fieldOrNull(formData: FormData, name: string): string | null {
  const value = String(formData.get(name) ?? "").trim();
  return value || null;
}

export async function createCourse(formData: FormData): Promise<void> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw new Error("Unauthorized");

  const courseCode = String(formData.get("courseCode") ?? "").trim();
  const courseName = String(formData.get("courseName") ?? "").trim();
  if (!courseCode || !courseName) return;

  const creditsRaw = String(formData.get("credits") ?? "").trim();

  await supabase.from("courses").insert({
    user_id: user.id,
    course_code: courseCode,
    course_name: courseName,
    semester: fieldOrNull(formData, "semester"),
    credits: creditsRaw ? Number(creditsRaw) : null,
    grade: fieldOrNull(formData, "grade"),
    theory_faculty: fieldOrNull(formData, "theoryFaculty"),
    theory_room: fieldOrNull(formData, "theoryRoom"),
    lab_faculty: fieldOrNull(formData, "labFaculty"),
    lab_room: fieldOrNull(formData, "labRoom"),
  });
  revalidatePath("/courses");
}

export async function updateCourse(id: string, formData: FormData): Promise<void> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw new Error("Unauthorized");

  const courseCode = String(formData.get("courseCode") ?? "").trim();
  const courseName = String(formData.get("courseName") ?? "").trim();
  if (!courseCode || !courseName) return;

  const creditsRaw = String(formData.get("credits") ?? "").trim();

  await supabase
    .from("courses")
    .update({
      course_code: courseCode,
      course_name: courseName,
      semester: fieldOrNull(formData, "semester"),
      credits: creditsRaw ? Number(creditsRaw) : null,
      grade: fieldOrNull(formData, "grade"),
      theory_faculty: fieldOrNull(formData, "theoryFaculty"),
      theory_room: fieldOrNull(formData, "theoryRoom"),
      lab_faculty: fieldOrNull(formData, "labFaculty"),
      lab_room: fieldOrNull(formData, "labRoom"),
    })
    .eq("id", id)
    .eq("user_id", user.id);
  revalidatePath("/courses");
  revalidatePath(`/courses/${id}`);
}

export async function deleteCourse(id: string): Promise<void> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw new Error("Unauthorized");

  await supabase.from("courses").delete().eq("id", id).eq("user_id", user.id);
  revalidatePath("/courses");
  redirect("/courses");
}
