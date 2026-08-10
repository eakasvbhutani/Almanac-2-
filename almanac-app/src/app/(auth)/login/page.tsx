"use client";

import { useActionState } from "react";
import Link from "next/link";
import { signIn, signInWithGithub, type AuthState } from "../actions";

const initialState: AuthState = { error: null };

export default function LoginPage() {
  const [state, formAction, pending] = useActionState(signIn, initialState);

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl">Sign in</h1>

      <form action={formAction} className="flex flex-col gap-3">
        <div>
          <label className="block text-xs opacity-70 mb-1">Email</label>
          <input className="input" type="email" name="email" required autoComplete="email" />
        </div>
        <div>
          <label className="block text-xs opacity-70 mb-1">Password</label>
          <input className="input" type="password" name="password" required autoComplete="current-password" />
        </div>

        {state.error && (
          <p className="text-sm" style={{ color: "var(--color-accent-700)" }}>
            {state.error}
          </p>
        )}

        <button type="submit" className="btn btn-primary" disabled={pending}>
          {pending ? "Signing in…" : "Sign in"}
        </button>
      </form>

      <form action={signInWithGithub}>
        <button type="submit" className="btn btn-secondary w-full">
          Continue with GitHub
        </button>
      </form>

      <p className="text-sm text-center opacity-70">
        No account yet?{" "}
        <Link href="/signup" className="underline">
          Create one
        </Link>
      </p>
    </div>
  );
}
