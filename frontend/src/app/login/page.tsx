"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Bot, Mail, Lock, User, ArrowRight, Eye, EyeOff,
  Loader2, Phone, Building2, AlertCircle, CheckCircle2,
} from "lucide-react";
import { useAuthStore } from "@/store";
import { authService } from "@/services/endpoints";
import { roleHome } from "@/lib/rbac";

type Mode = "login" | "register" | "forgot";
type UserRole = "citizen" | "officer";

const DEPARTMENTS = [
  { id: "agriculture", name: "Agriculture" },
  { id: "road-transport", name: "Road & Transport" },
  { id: "education", name: "Education" },
  { id: "health", name: "Health" },
  { id: "municipal", name: "Municipal Corporation" },
  { id: "general", name: "General Administration" },
];

function PasswordStrength({ password }: { password: string }) {
  const score = [
    password.length >= 8,
    /[A-Z]/.test(password),
    /[0-9]/.test(password),
    /[^A-Za-z0-9]/.test(password),
  ].filter(Boolean).length;

  const levels = [
    { label: "Weak", color: "bg-red-500" },
    { label: "Fair", color: "bg-orange-400" },
    { label: "Good", color: "bg-yellow-400" },
    { label: "Strong", color: "bg-green-500" },
  ];
  const level = levels[Math.max(0, score - 1)] ?? levels[0];

  if (!password) return null;
  return (
    <div className="mt-2 space-y-1">
      <div className="flex gap-1">
        {levels.map((l, i) => (
          <div
            key={l.label}
            className={`h-1 flex-1 rounded-full transition-colors ${i < score ? level.color : "bg-[hsl(var(--border))]"}`}
          />
        ))}
      </div>
      <p className="text-xs text-[hsl(var(--text-muted))]">
        Password strength: <span className="font-medium">{level.label}</span>
      </p>
    </div>
  );
}

export default function LoginPage() {
  const pathname = usePathname();
  const [mode, setMode] = useState<Mode>(
    pathname === "/register" ? "register" : pathname === "/forgot-password" ? "forgot" : "login"
  );

  // shared
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  // register only
  const [name, setName] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showConfirm, setShowConfirm] = useState(false);
  const [role, setRole] = useState<UserRole>("citizen");
  const [department, setDepartment] = useState("");
  const [phone, setPhone] = useState("");

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const router = useRouter();
  const loginStore = useAuthStore((s) => s.login);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      if (mode === "login") {
        const response = await authService.login(email, password);
        const { user: apiUser, access_token, refresh_token } = response.data;
        if (apiUser && access_token) {
          loginStore(apiUser, { accessToken: access_token, refreshToken: refresh_token });
          router.push(roleHome[apiUser.role as UserRole]);
          return;
        }
        throw new Error("Invalid login response from server.");

      } else if (mode === "register") {
        if (password !== confirmPassword) {
          setError("Passwords do not match.");
          return;
        }
        if (role === "officer" && !department) {
          setError("Please select your department.");
          return;
        }
        const response = await authService.register({
          name,
          email,
          password,
          confirm_password: confirmPassword,
          role,
          department: role === "officer" ? department : undefined,
          phone: phone || undefined,
        });
        const { user: apiUser, access_token, refresh_token } = (response as any).data;
        if (apiUser && access_token) {
          loginStore(apiUser, { accessToken: access_token, refreshToken: refresh_token });
          router.push(roleHome[apiUser.role as UserRole]);
          return;
        }
        setSuccess("Account created! Please sign in.");
        setMode("login");

      } else if (mode === "forgot") {
        await authService.forgotPassword({ email });
        setSuccess("If that email is registered, a reset link has been sent.");
        setTimeout(() => setMode("login"), 4000);
      }
    } catch (err: any) {
      // Surface backend error message if available
      const detail = err?.details?.detail;
      if (typeof detail === "object" && detail?.message) {
        setError(detail.message);
      } else if (typeof err?.message === "string" && err.message !== "Network Error") {
        setError(err.message);
      } else {
        setError("Something went wrong. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const switchMode = (next: Mode) => {
    setError("");
    setSuccess("");
    setMode(next);
  };

  return (
    <div className="min-h-screen grid-pattern flex items-center justify-center px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.45 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[hsl(var(--accent))] to-[hsl(var(--accent2,192_91%_36%))] flex items-center justify-center shadow-lg shadow-[hsl(var(--accent)/0.25)]">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold">RTI-Agent</span>
          </Link>
          <p className="text-sm text-[hsl(var(--text-muted))]">
            {mode === "login" && "Sign in to your account"}
            {mode === "register" && "Create your RTI account"}
            {mode === "forgot" && "Reset your password"}
          </p>
        </div>

        {/* Card */}
        <div className="rounded-2xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-8 shadow-xl">
          <AnimatePresence mode="wait">
            <motion.form
              key={mode}
              initial={{ opacity: 0, x: 12 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -12 }}
              transition={{ duration: 0.2 }}
              onSubmit={handleSubmit}
              className="space-y-4"
            >
              {/* === REGISTER FIELDS === */}
              {mode === "register" && (
                <>
                  {/* Full Name */}
                  <div>
                    <label className="block text-xs font-medium text-[hsl(var(--text-muted))] mb-1.5">Full Name</label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--text-muted))]" />
                      <input
                        type="text"
                        id="reg-name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Your full name"
                        required
                        className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] text-sm placeholder:text-[hsl(var(--text-muted)/0.5)] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent)/0.3)] focus:border-[hsl(var(--accent))] transition-all"
                      />
                    </div>
                  </div>

                  {/* Phone (optional) */}
                  <div>
                    <label className="block text-xs font-medium text-[hsl(var(--text-muted))] mb-1.5">
                      Phone <span className="opacity-50">(optional)</span>
                    </label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--text-muted))]" />
                      <input
                        type="tel"
                        id="reg-phone"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        placeholder="+91 98765 43210"
                        className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] text-sm placeholder:text-[hsl(var(--text-muted)/0.5)] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent)/0.3)] focus:border-[hsl(var(--accent))] transition-all"
                      />
                    </div>
                  </div>

                  {/* Role selector */}
                  <div>
                    <label className="block text-xs font-medium text-[hsl(var(--text-muted))] mb-1.5">I am a</label>
                    <div className="grid grid-cols-2 gap-2">
                      {(["citizen", "officer"] as UserRole[]).map((r) => (
                        <button
                          key={r}
                          type="button"
                          id={`role-${r}`}
                          onClick={() => { setRole(r); setDepartment(""); }}
                          className={`py-2 rounded-lg text-sm font-medium border transition-all capitalize ${
                            role === r
                              ? "bg-[hsl(var(--accent))] text-white border-[hsl(var(--accent))] shadow-md"
                              : "border-[hsl(var(--border))] text-[hsl(var(--text-muted))] hover:border-[hsl(var(--accent)/0.5)]"
                          }`}
                        >
                          {r === "citizen" ? "🧑 Citizen" : "🏛 Officer"}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Department — only for officer */}
                  {role === "officer" && (
                    <div>
                      <label className="block text-xs font-medium text-[hsl(var(--text-muted))] mb-1.5">Department *</label>
                      <div className="relative">
                        <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--text-muted))]" />
                        <select
                          id="reg-department"
                          value={department}
                          onChange={(e) => setDepartment(e.target.value)}
                          required
                          className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] text-sm focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent)/0.3)] focus:border-[hsl(var(--accent))] transition-all appearance-none"
                        >
                          <option value="">Select department...</option>
                          {DEPARTMENTS.map((d) => (
                            <option key={d.id} value={d.id}>{d.name}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* === EMAIL (all modes) === */}
              <div>
                <label className="block text-xs font-medium text-[hsl(var(--text-muted))] mb-1.5">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--text-muted))]" />
                  <input
                    id="auth-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    required
                    autoComplete="email"
                    className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] text-sm placeholder:text-[hsl(var(--text-muted)/0.5)] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent)/0.3)] focus:border-[hsl(var(--accent))] transition-all"
                  />
                </div>
              </div>

              {/* === PASSWORD (login + register) === */}
              {mode !== "forgot" && (
                <div>
                  <label className="block text-xs font-medium text-[hsl(var(--text-muted))] mb-1.5">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--text-muted))]" />
                    <input
                      id="auth-password"
                      type={showPassword ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      autoComplete={mode === "login" ? "current-password" : "new-password"}
                      className="w-full pl-10 pr-10 py-2.5 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] text-sm placeholder:text-[hsl(var(--text-muted)/0.5)] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent)/0.3)] focus:border-[hsl(var(--accent))] transition-all"
                    />
                    <button type="button" onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[hsl(var(--text-muted))] hover:text-[hsl(var(--text))] transition-colors">
                      {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  {mode === "register" && <PasswordStrength password={password} />}
                </div>
              )}

              {/* === CONFIRM PASSWORD (register) === */}
              {mode === "register" && (
                <div>
                  <label className="block text-xs font-medium text-[hsl(var(--text-muted))] mb-1.5">Confirm Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--text-muted))]" />
                    <input
                      id="auth-confirm-password"
                      type={showConfirm ? "text" : "password"}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      autoComplete="new-password"
                      className={`w-full pl-10 pr-10 py-2.5 rounded-lg border text-sm placeholder:text-[hsl(var(--text-muted)/0.5)] focus:outline-none focus:ring-2 transition-all bg-[hsl(var(--bg))] ${
                        confirmPassword && confirmPassword !== password
                          ? "border-red-500 focus:ring-red-400/30"
                          : "border-[hsl(var(--border))] focus:ring-[hsl(var(--accent)/0.3)] focus:border-[hsl(var(--accent))]"
                      }`}
                    />
                    <button type="button" onClick={() => setShowConfirm(!showConfirm)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[hsl(var(--text-muted))] hover:text-[hsl(var(--text))] transition-colors">
                      {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  {confirmPassword && confirmPassword !== password && (
                    <p className="text-xs text-red-400 mt-1">Passwords do not match.</p>
                  )}
                </div>
              )}

              {/* Forgot password link */}
              {mode === "login" && (
                <div className="flex justify-end">
                  <button type="button" onClick={() => switchMode("forgot")}
                    className="text-xs text-[hsl(var(--accent))] hover:underline">
                    Forgot password?
                  </button>
                </div>
              )}

              {/* Error / Success banners */}
              <AnimatePresence>
                {error && (
                  <motion.p
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="flex items-center gap-2 text-xs text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2"
                  >
                    <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                    {error}
                  </motion.p>
                )}
                {success && (
                  <motion.p
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="flex items-center gap-2 text-xs text-green-400 bg-green-500/10 border border-green-500/20 rounded-lg px-3 py-2"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                    {success}
                  </motion.p>
                )}
              </AnimatePresence>

              {/* Submit */}
              <button
                id="auth-submit"
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg bg-[hsl(var(--accent))] text-white text-sm font-medium hover:opacity-90 disabled:opacity-50 transition-all shadow-lg shadow-[hsl(var(--accent)/0.2)] mt-2"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    {mode === "login" && "Sign In"}
                    {mode === "register" && "Create Account"}
                    {mode === "forgot" && "Send Reset Link"}
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </motion.form>
          </AnimatePresence>

          {/* Mode switcher */}
          <div className="mt-5 text-center text-sm text-[hsl(var(--text-muted))]">
            {mode === "login" ? (
              <>
                Don&apos;t have an account?{" "}
                <button onClick={() => switchMode("register")} className="text-[hsl(var(--accent))] hover:underline font-medium">
                  Sign up
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button onClick={() => switchMode("login")} className="text-[hsl(var(--accent))] hover:underline font-medium">
                  Sign in
                </button>
              </>
            )}
          </div>
        </div>

        {/* Admin hint (dev only) */}
        {process.env.NODE_ENV === "development" && mode === "login" && (
          <p className="text-center text-xs text-[hsl(var(--text-muted)/0.5)] mt-4">
            Admin: acashtech28@gmail.com / acash@9945
          </p>
        )}
      </motion.div>
    </div>
  );
}
