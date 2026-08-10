"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "Today" },
  { href: "/courses", label: "Courses" },
  { href: "/tasks", label: "Tasks" },
  { href: "/notes", label: "Notes" },
  { href: "/office", label: "Office Work" },
];

export function Nav() {
  const pathname = usePathname();

  return (
    <nav className="flex gap-1.5 overflow-x-auto">
      {NAV_ITEMS.map((item) => {
        const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
        return (
          <Link key={item.href} href={item.href} className={active ? "btn btn-primary" : "btn btn-secondary"} style={{ flex: "none" }}>
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
