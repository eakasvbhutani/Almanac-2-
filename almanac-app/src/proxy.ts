import { type NextRequest } from "next/server";
import { updateSession } from "@/utils/supabase/middleware";

// Renamed from `middleware.ts` — Next.js 16 deprecated that file convention
// in favor of `proxy.ts`. Behavior is identical.
export async function proxy(request: NextRequest) {
  return await updateSession(request);
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
