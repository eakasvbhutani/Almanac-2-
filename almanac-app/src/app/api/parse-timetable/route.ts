import { NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { parseTimetableFile } from "@/lib/parse-timetable";

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "application/pdf"];
const MAX_BYTES = 8 * 1024 * 1024; // 8MB — comfortable for a phone photo or scanned PDF

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : "Unexpected error";
}

export async function POST(request: Request) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ error: "Sign in to upload a timetable." }, { status: 401 });
  }

  const formData = await request.formData();
  const file = formData.get("file");

  if (!(file instanceof File)) {
    return NextResponse.json({ error: "No file provided." }, { status: 400 });
  }
  if (!ALLOWED_TYPES.includes(file.type)) {
    return NextResponse.json({ error: "Only JPG, PNG, WebP, or PDF files are supported." }, { status: 400 });
  }
  if (file.size > MAX_BYTES) {
    return NextResponse.json({ error: "File is too large (max 8MB)." }, { status: 400 });
  }

  const bytes = new Uint8Array(await file.arrayBuffer());
  const storagePath = `${user.id}/${Date.now()}-${file.name}`;

  const { error: uploadError } = await supabase.storage
    .from("timetables")
    .upload(storagePath, bytes, { contentType: file.type });
  if (uploadError) {
    return NextResponse.json({ error: uploadError.message }, { status: 500 });
  }

  const { data: uploadRow, error: insertUploadError } = await supabase
    .from("timetable_uploads")
    .insert({ user_id: user.id, storage_path: storagePath, status: "pending" })
    .select()
    .single();
  if (insertUploadError || !uploadRow) {
    return NextResponse.json({ error: insertUploadError?.message ?? "Could not record upload." }, { status: 500 });
  }

  try {
    const base64Data = Buffer.from(bytes).toString("base64");
    const parsed = await parseTimetableFile({ base64Data, mediaType: file.type });

    const courseIdByCode = new Map<string, string>();
    for (const course of parsed.courses) {
      const { data: courseRow, error: courseError } = await supabase
        .from("courses")
        .insert({
          user_id: user.id,
          course_code: course.course_code,
          course_name: course.course_name,
          theory_faculty: course.theory_faculty,
          theory_room: course.theory_room,
          lab_faculty: course.lab_faculty,
          lab_room: course.lab_room,
        })
        .select()
        .single();
      if (!courseError && courseRow) {
        courseIdByCode.set(course.course_code, courseRow.id as string);
      }
    }

    const slotsToInsert = parsed.slots.map((slot) => ({
      user_id: user.id,
      day: slot.day,
      start_time: slot.start_time,
      end_time: slot.end_time,
      slot_type: slot.slot_type,
      course_id: slot.course_code ? (courseIdByCode.get(slot.course_code) ?? null) : null,
      label: slot.label,
      room: slot.room,
    }));
    if (slotsToInsert.length > 0) {
      await supabase.from("timetable_slots").insert(slotsToInsert);
    }

    await supabase
      .from("timetable_uploads")
      .update({ status: "parsed", parsed_json: parsed })
      .eq("id", uploadRow.id);

    return NextResponse.json({ success: true, timetable: parsed });
  } catch (err: unknown) {
    const message = errorMessage(err);
    await supabase.from("timetable_uploads").update({ status: "failed", error: message }).eq("id", uploadRow.id);
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
