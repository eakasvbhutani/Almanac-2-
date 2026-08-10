"use client";

import { useState } from "react";

export interface AgendaSlot {
  id: string;
  day: string;
  start_time: string;
  end_time: string;
  slot_type: "theory" | "lab" | "activity" | "break";
  title: string;
  meta: string;
}

const DAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const TYPE_LABEL: Record<AgendaSlot["slot_type"], string> = {
  theory: "Lecture",
  lab: "Lab",
  activity: "Optional",
  break: "Break",
};

const TYPE_BG: Record<AgendaSlot["slot_type"], string> = {
  theory: "var(--color-accent-100)",
  lab: "var(--color-accent-2-100)",
  activity: "color-mix(in srgb, var(--color-text) 8%, transparent)",
  break: "color-mix(in srgb, var(--color-text) 8%, transparent)",
};

const TYPE_COLOR: Record<AgendaSlot["slot_type"], string> = {
  theory: "var(--color-accent-700)",
  lab: "var(--color-accent-2-700)",
  activity: "var(--color-text)",
  break: "var(--color-text)",
};

function todayDayName(): string {
  const idx = new Date().getDay(); // 0=Sun
  const names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const name = names[idx];
  return DAY_ORDER.includes(name) ? name : "Mon";
}

export function WeekAgenda({ slots }: { slots: AgendaSlot[] }) {
  const [activeDay, setActiveDay] = useState(todayDayName());
  const daySlots = slots
    .filter((s) => s.day === activeDay)
    .sort((a, b) => a.start_time.localeCompare(b.start_time));

  return (
    <div>
      <div className="flex gap-1.5 overflow-x-auto pb-2 mb-4">
        {DAY_ORDER.map((day) => (
          <button
            key={day}
            type="button"
            onClick={() => setActiveDay(day)}
            className={day === activeDay ? "btn btn-primary" : "btn btn-secondary"}
            style={{ flex: "none" }}
          >
            {day}
          </button>
        ))}
      </div>

      <div className="flex flex-col gap-2">
        {daySlots.length === 0 && (
          <div className="card text-center text-sm opacity-60 py-8">Nothing scheduled for {activeDay}.</div>
        )}
        {daySlots.map((slot) => (
          <div key={slot.id} className="card flex flex-row items-center gap-3">
            <div className="flex-none w-13 text-xs opacity-60 leading-relaxed">
              <div>{slot.start_time}</div>
              <div>{slot.end_time}</div>
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-bold">{slot.title}</div>
              {slot.meta && <div className="text-xs opacity-60 mt-0.5">{slot.meta}</div>}
            </div>
            <span
              className="flex-none text-xs rounded-full px-2.5 py-1"
              style={{ background: TYPE_BG[slot.slot_type], color: TYPE_COLOR[slot.slot_type] }}
            >
              {TYPE_LABEL[slot.slot_type]}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
