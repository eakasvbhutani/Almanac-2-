"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { ParsedTimetable } from "@/lib/timetable-schema";

type UploadState =
  | { status: "idle" }
  | { status: "uploading" }
  | { status: "done"; timetable: ParsedTimetable }
  | { status: "error"; message: string };

export default function OnboardingPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [state, setState] = useState<UploadState>({ status: "idle" });

  async function handleFile(file: File) {
    setState({ status: "uploading" });
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/parse-timetable", { method: "POST", body: formData });
      const body = await res.json();
      if (!res.ok) {
        setState({ status: "error", message: body.error ?? "Something went wrong." });
        return;
      }
      setState({ status: "done", timetable: body.timetable });
    } catch {
      setState({ status: "error", message: "Upload failed — check your connection and try again." });
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ background: "var(--color-bg)" }}>
      <div className="w-full max-w-lg">
        <h1 className="text-3xl mb-2">Upload your timetable</h1>
        <p className="text-sm opacity-70 mb-6">
          A JPG, PNG, or PDF of your weekly timetable — Claude reads it and builds your schedule automatically.
          You can review and fix anything it gets wrong afterward.
        </p>

        <div className="card">
          {state.status === "idle" && (
            <div className="flex flex-col gap-4">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp,application/pdf"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFile(file);
                }}
              />
              <button type="button" className="btn btn-primary" onClick={() => fileInputRef.current?.click()}>
                Choose a file
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => router.push("/")}>
                Skip for now
              </button>
            </div>
          )}

          {state.status === "uploading" && <p className="text-sm opacity-70">Reading your timetable…</p>}

          {state.status === "error" && (
            <div className="flex flex-col gap-3">
              <p className="text-sm" style={{ color: "var(--color-accent-700)" }}>
                {state.message}
              </p>
              <button type="button" className="btn btn-secondary" onClick={() => setState({ status: "idle" })}>
                Try again
              </button>
            </div>
          )}

          {state.status === "done" && (
            <div className="flex flex-col gap-3">
              <p className="text-sm font-semibold">
                Found {state.timetable.courses.length} course{state.timetable.courses.length === 1 ? "" : "s"} and{" "}
                {state.timetable.slots.length} class slot{state.timetable.slots.length === 1 ? "" : "s"}.
              </p>
              {state.timetable.notes && (
                <p className="text-sm rounded-lg p-3" style={{ background: "var(--color-accent-100)", color: "var(--color-accent-700)" }}>
                  {state.timetable.notes}
                </p>
              )}
              <ul className="text-sm flex flex-col gap-1">
                {state.timetable.courses.map((c) => (
                  <li key={c.course_code} className="opacity-80">
                    {c.course_code} — {c.course_name}
                  </li>
                ))}
              </ul>
              <button type="button" className="btn btn-primary" onClick={() => router.push("/")}>
                Looks good — go to my Almanac
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
