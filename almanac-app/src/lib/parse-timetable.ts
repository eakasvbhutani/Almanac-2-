import Anthropic from "@anthropic-ai/sdk";
import { parsedTimetableSchema, type ParsedTimetable } from "./timetable-schema";

const MODEL = "claude-sonnet-5";

// Mirrors parsedTimetableSchema in timetable-schema.ts. Hand-written rather
// than generated from the Zod schema so the tool call the model receives is
// exactly what we validate against — no schema-library version drift.
const TIMETABLE_TOOL: Anthropic.Tool = {
  name: "record_timetable",
  description: "Record the weekly class timetable extracted from the uploaded image or PDF.",
  input_schema: {
    type: "object",
    properties: {
      section: { type: ["string", "null"], description: "Section/class code printed on the timetable, e.g. 3EC-ACT123." },
      courses: {
        type: "array",
        items: {
          type: "object",
          properties: {
            course_code: { type: "string", description: "Short code, e.g. ECE-201. Invent one from the subject name if none is printed." },
            course_name: { type: "string" },
            theory_faculty: { type: ["string", "null"] },
            theory_room: { type: ["string", "null"] },
            lab_faculty: { type: ["string", "null"] },
            lab_room: { type: ["string", "null"] },
          },
          required: ["course_code", "course_name", "theory_faculty", "theory_room", "lab_faculty", "lab_room"],
        },
      },
      slots: {
        type: "array",
        items: {
          type: "object",
          properties: {
            day: { type: "string", enum: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] },
            start_time: { type: "string", description: "24-hour HH:MM" },
            end_time: { type: "string", description: "24-hour HH:MM" },
            slot_type: { type: "string", enum: ["theory", "lab", "activity", "break"] },
            course_code: { type: ["string", "null"], description: "Must match a courses[].course_code for theory/lab slots, else null." },
            label: { type: ["string", "null"], description: "Label for activity/break slots, e.g. 'NCC / NSS / Sports', 'Library', 'Lunch break'." },
            room: { type: ["string", "null"] },
          },
          required: ["day", "start_time", "end_time", "slot_type", "course_code", "label", "room"],
        },
      },
      notes: {
        type: ["string", "null"],
        description:
          "Flag anything uncertain: illegible text, cells that stack multiple options (e.g. several lab batches sharing one time block — record only the first as a provisional slot and describe the alternatives here so the user can correct it), or anything else that needs the user's confirmation.",
      },
    },
    required: ["section", "courses", "slots", "notes"],
  },
};

const SYSTEM_PROMPT = `You read a college weekly timetable image or PDF and extract it into structured data via the record_timetable tool.

Rules:
- One row of theory classes and, separately, weekly lab blocks (often 2-3 contiguous periods) per course.
- A cell that stacks multiple course/faculty/room options in the same time block usually means different student batches/groups use that slot for different labs. Do not guess which one belongs to the uploader — record the first listed option as a provisional slot and explain the alternatives in "notes" so the user can correct it in the app afterward.
- NCC/NSS/Sports and Library periods are "activity" type, not "theory" or "lab" — they are typically optional.
- A lunch break is "break" type.
- Times are 24-hour HH:MM. Infer end times from the grid's period boundaries when not printed directly.
- If a course has both a theory room and a lab room, capture both on the same course entry rather than creating two courses.
- Never invent classes that are not visibly on the timetable.`;

export async function parseTimetableFile(params: {
  base64Data: string;
  mediaType: string;
}): Promise<ParsedTimetable> {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    throw new Error("ANTHROPIC_API_KEY is not configured on the server.");
  }

  const client = new Anthropic({ apiKey });
  const isPdf = params.mediaType === "application/pdf";

  const message = await client.messages.create({
    model: MODEL,
    max_tokens: 4096,
    system: SYSTEM_PROMPT,
    tools: [TIMETABLE_TOOL],
    tool_choice: { type: "tool", name: "record_timetable" },
    messages: [
      {
        role: "user",
        content: [
          isPdf
            ? {
                type: "document",
                source: { type: "base64", media_type: "application/pdf", data: params.base64Data },
              }
            : {
                type: "image",
                source: {
                  type: "base64",
                  media_type: params.mediaType as "image/jpeg" | "image/png" | "image/webp",
                  data: params.base64Data,
                },
              },
          { type: "text", text: "Extract this timetable using the record_timetable tool." },
        ],
      },
    ],
  });

  const toolUse = message.content.find(
    (block): block is Anthropic.ToolUseBlock => block.type === "tool_use",
  );
  if (!toolUse) {
    throw new Error("The model did not return structured timetable data.");
  }

  const parsed = parsedTimetableSchema.safeParse(toolUse.input);
  if (!parsed.success) {
    throw new Error(`Parsed timetable failed validation: ${parsed.error.message}`);
  }

  return parsed.data;
}
