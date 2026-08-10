import { z } from "zod";

export const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] as const;
export const SLOT_TYPES = ["theory", "lab", "activity", "break"] as const;

const timeString = z
  .string()
  .regex(/^([01]\d|2[0-3]):[0-5]\d$/, "Expected 24-hour HH:MM");

export const parsedCourseSchema = z.object({
  course_code: z.string().min(1).describe("Short course code, e.g. ECE-201. Invent a short one from the subject name if none is printed."),
  course_name: z.string().min(1),
  theory_faculty: z.string().nullable(),
  theory_room: z.string().nullable(),
  lab_faculty: z.string().nullable(),
  lab_room: z.string().nullable(),
});

export const parsedSlotSchema = z.object({
  day: z.enum(DAYS),
  start_time: timeString,
  end_time: timeString,
  slot_type: z.enum(SLOT_TYPES),
  course_code: z.string().nullable().describe("Must match a course_code from the courses array when slot_type is theory or lab, otherwise null."),
  label: z.string().nullable().describe("Human label for activity/break slots, e.g. 'NCC / NSS / Sports', 'Library', 'Lunch break'."),
  room: z.string().nullable(),
});

export const parsedTimetableSchema = z.object({
  section: z.string().nullable().describe("Section/class code printed on the timetable, e.g. 3EC-ACT123."),
  courses: z.array(parsedCourseSchema),
  slots: z.array(parsedSlotSchema),
  notes: z
    .string()
    .nullable()
    .describe("Anything in the image the parser was unsure about — merged cells, illegible text, ambiguous room numbers. Null if none."),
});

export type ParsedTimetable = z.infer<typeof parsedTimetableSchema>;
