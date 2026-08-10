"use server";

import { revalidatePath } from "next/cache";
import { createClient } from "@/utils/supabase/server";

export async function createNote(formData: FormData): Promise<void> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw new Error("Unauthorized");

  const note = String(formData.get("note") ?? "").trim();
  if (!note) return;

  const body = String(formData.get("body") ?? "").trim() || null;
  const courseId = String(formData.get("courseId") ?? "") || null;

  await supabase.from("notes").insert({ user_id: user.id, note, body, course_id: courseId });
  revalidatePath("/notes");
}

export async function deleteNote(id: string): Promise<void> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw new Error("Unauthorized");

  await supabase.from("notes").delete().eq("id", id).eq("user_id", user.id);
  revalidatePath("/notes");
}
