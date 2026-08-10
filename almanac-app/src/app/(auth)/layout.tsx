export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center px-4" style={{ background: "var(--color-bg)" }}>
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="text-3xl" style={{ fontFamily: "var(--font-heading)" }}>
            Almanac
          </div>
          <div className="text-sm opacity-60 mt-1">3EC-ACT123</div>
        </div>
        <div className="card">{children}</div>
      </div>
    </div>
  );
}
