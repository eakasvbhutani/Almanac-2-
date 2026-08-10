import { redirect } from "next/navigation";
import { createClient } from "@/utils/supabase/server";
import { signOut } from "@/app/(auth)/actions";
import { Nav } from "@/components/Nav";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    redirect("/login");
  }

  return (
    <div className="min-h-screen" style={{ background: "var(--color-bg)" }}>
      <header
        className="flex items-center justify-between gap-4 flex-wrap px-6 py-4"
        style={{ borderBottom: "1px solid var(--color-divider)" }}
      >
        <div className="flex items-center gap-6 flex-wrap">
          <div className="text-xl" style={{ fontFamily: "var(--font-heading)" }}>
            Almanac
          </div>
          <Nav />
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs opacity-55">{user.email}</span>
          <form action={signOut}>
            <button type="submit" className="btn btn-secondary">
              Sign out
            </button>
          </form>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-8">{children}</main>
    </div>
  );
}
