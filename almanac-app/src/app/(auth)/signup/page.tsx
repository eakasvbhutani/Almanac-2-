"use client";

import { useActionState } from "react";
import Link from "next/link";
import { signUp, signInWithGithub, type AuthState } from "../actions";

const initialState: AuthState = { error: null };

export default function SignupPage() {
  const [state, formAction, pending] = useActionState(signUp, initialState);

  return (
    <div className="flex flex-col gap-4">
      <h1 className="text-2xl">Create your account</h1>

      <form action={formAction} className="flex flex-col gap-3">
        <div>
          <label className="block text-xs opacity-70 mb-1">Full name</label>
          <input className="input" type="text" name="fullName" required autoComplete="name" />
        </div>
        <div>
          <label className="block text-xs opacity-70 mb-1">Email</label>
          <input className="input" type="email" name="email" required autoComplete="email" />
        </div>
        <div>
          <label className="block text-xs opacity-70 mb-1">Password</label>
          <input
            className="input"
            type="password"
            name="password"
            required
            minLength={8}
            autoComplete="new-password"
          />
          <p className="text-xs opacity-50 mt-1">At least 8 characters.</p>
        </div>

        {state.error && (
          <p className="text-sm" style={{ color: "var(--color-accent-700)" }}>
            {state.error}
          </p>
        )}

        <button type="submit" className="btn btn-primary" disabled={pending}>
          {pending ? "Creating account…" : "Create account"}
        </button>
      </form>

      <form action={signInWithGithub}>
        <button type="submit" className="btn btn-secondary w-full">
          Continue with GitHub
        </button>
      </form>

      <p className="text-sm text-center opacity-70">
        Already have an account?{" "}
        <Link href="/login" className="underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
