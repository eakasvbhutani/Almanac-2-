"use server";

import { revalidatePath } from "next/cache";
import { createClient } from "@/utils/supabase/server";

const STATUS_ORDER = ["To do", "Doing", "Done"] as const;

export async function createOfficeTask(formData: FormData): Promise<void> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw new Error("Unauthorized");

  const task = String(formData.get("task") ?? "").trim();
  if (!task) return;

  const dueDate = String(formData.get("dueDate") ?? "").trim() || null;
  const status = String(formData.get("status") ?? "To do");

  await supabase.from("office_tasks").insert({ user_id: user.id, task, due_date: dueDate, status });
  revalidatePath("/office");
}

export async function cycleOfficeTaskStatus(id: string, currentStatus: string): Promise<void> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw new Error("Unauthorized");

  const idx = STATUS_ORDER.indexOf(currentStatus as (typeof STATUS_ORDER)[number]);
  const next = STATUS_ORDER[(idx + 1) % STATUS_ORDER.length];

  await supabase.from("office_tasks").update({ status: next }).eq("id", id).eq("user_id", user.id);
  revalidatePath("/office");
}

export async function deleteOfficeTask(id: string): Promise<void> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw new Error("Unauthorized");

  await supabase.from("office_tasks").delete().eq("id", id).eq("user_id", user.id);
  revalidatePath("/office");
}
