"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useState, useEffect } from "react";
import {
  ArrowRight,
  Bot,
  Shield,
  Zap,
  FileSearch,
  Users,
  BarChart3,
  Globe,
  GitBranch,
  FileText,
  Tags,
  Search,
  ShieldCheck,
  UserCheck,
  RefreshCw,
  CheckCircle2,
  ChevronRight,
  Wheat,
  Route,
  GraduationCap,
  Heart,
  Building2,
  Sun,
  Moon,
} from "lucide-react";
import { useTheme } from "next-themes";
import { config } from "@/config";

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.1, duration: 0.6, ease: "easeOut" as const },
  }),
};

const iconMap: Record<string, React.ElementType> = {
  Wheat, Route, GraduationCap, Heart, Building2,
  GitBranch, FileText, Tags, Search, ShieldCheck, UserCheck, RefreshCw, CheckCircle2,
};

export default function LandingPage() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="min-h-screen grid-pattern">
      {/* ── Navbar ─────────────────────────────────────────── */}
      <nav className="fixed top-0 inset-x-0 z-50 glass border-b border-[hsl(var(--border))]">
        <div className="max-w-7xl mx-auto flex items-center justify-between px-6 h-16">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[hsl(var(--accent))] to-[hsl(var(--accent2,192_91%_36%))] flex items-center justify-center">
              <Bot className="w-4.5 h-4.5 text-white" />
            </div>
            <span className="font-semibold text-lg tracking-tight">RTI-Agent</span>
          </Link>
          <div className="hidden md:flex items-center gap-8 text-sm text-[hsl(var(--text-muted))]">
            <a href="#features" className="hover:text-[hsl(var(--text))] transition-colors">Features</a>
            <a href="#workflow" className="hover:text-[hsl(var(--text))] transition-colors">How It Works</a>
            <a href="#departments" className="hover:text-[hsl(var(--text))] transition-colors">Departments</a>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="w-9 h-9 rounded-lg border border-[hsl(var(--border))] flex items-center justify-center hover:bg-[hsl(var(--surface2))] transition-colors"
              aria-label="Toggle theme"
            >
              {mounted ? (
                theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />
              ) : (
                <div className="w-4 h-4" />
              )}
            </button>
            <Link
              href="/login"
              className="text-sm px-4 py-2 rounded-lg border border-[hsl(var(--border))] hover:bg-[hsl(var(--surface2))] transition-colors"
            >
              Log In
            </Link>
            <Link
              href="/login"
              className="text-sm px-4 py-2 rounded-lg bg-[hsl(var(--accent))] text-white hover:opacity-90 transition-opacity"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ───────────────────────────────────────────── */}
      <section className="pt-32 pb-24 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-[hsl(var(--accent)/0.3)] bg-[hsl(var(--accent)/0.08)] text-[hsl(var(--accent))] text-xs font-mono mb-8"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[hsl(var(--accent))] animate-pulse" />
            AI-Powered Governance Platform
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.7 }}
            className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight leading-[1.08] mb-6"
          >
            Right to Information
            <br />
            <span className="bg-gradient-to-r from-[hsl(var(--accent))] via-[hsl(var(--accent2,192_91%_36%))] to-[hsl(var(--accent))] bg-clip-text text-transparent">
              Reimagined with AI
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.7 }}
            className="text-lg text-[hsl(var(--text-muted))] max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            File, track, and manage RTI applications with an intelligent multi-agent system.
            Seven specialized AI agents work together to draft, classify, validate, and submit your requests.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.7 }}
            className="flex flex-wrap items-center justify-center gap-4"
          >
            <Link
              href="/dashboard/submit"
              className="group inline-flex items-center gap-2 px-7 py-3 rounded-xl bg-[hsl(var(--accent))] text-white font-medium text-sm hover:opacity-90 transition-all shadow-lg shadow-[hsl(var(--accent)/0.25)]"
            >
              File an RTI
              <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
            </Link>
            <Link
              href="/dashboard/track"
              className="inline-flex items-center gap-2 px-7 py-3 rounded-xl border border-[hsl(var(--border))] text-sm font-medium hover:bg-[hsl(var(--surface2))] transition-colors"
            >
              <FileSearch className="w-4 h-4" />
              Track RTI
            </Link>
          </motion.div>
        </div>
      </section>

      {/* ── Features ───────────────────────────────────────── */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            className="text-center mb-16"
          >
            <motion.p variants={fadeUp} custom={0} className="text-xs font-mono text-[hsl(var(--accent))] uppercase tracking-widest mb-3">
              Platform Features
            </motion.p>
            <motion.h2 variants={fadeUp} custom={1} className="text-3xl sm:text-4xl font-bold mb-4">
              Enterprise-Grade AI Governance
            </motion.h2>
            <motion.p variants={fadeUp} custom={2} className="text-[hsl(var(--text-muted))] max-w-xl mx-auto">
              Built with production-level AI engineering — multi-agent orchestration, human oversight, and real-time tracking.
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            className="grid md:grid-cols-2 lg:grid-cols-3 gap-5"
          >
            {[
              { icon: Bot, title: "Multi-Agent AI", desc: "7 specialized agents collaborate — Router, Formatter, Classifier, Retriever, Reviewer, Reflection, Tracker." },
              { icon: Shield, title: "Human-in-the-Loop", desc: "Every RTI draft is reviewed by a human before submission. AI recommends, humans decide." },
              { icon: Zap, title: "Real-Time Tracking", desc: "SSE-powered live updates. Watch each AI agent process your request in real time." },
              { icon: Globe, title: "Multilingual", desc: "Submit RTIs in English, Hindi, or Marathi. AI handles translation and formatting." },
              { icon: BarChart3, title: "Analytics Dashboard", desc: "Department performance, AI metrics, approval rates — all visualized in real time." },
              { icon: Users, title: "Role-Based Access", desc: "Citizens file requests. Officers review cases. Admins monitor the entire platform." },
            ].map((f, i) => (
              <motion.div
                key={f.title}
                variants={fadeUp}
                custom={i}
                className="group p-6 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] hover:border-[hsl(var(--accent)/0.3)] transition-all duration-300"
              >
                <div className="w-10 h-10 rounded-lg bg-[hsl(var(--accent)/0.1)] flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <f.icon className="w-5 h-5 text-[hsl(var(--accent))]" />
                </div>
                <h3 className="font-semibold mb-2">{f.title}</h3>
                <p className="text-sm text-[hsl(var(--text-muted))] leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── Workflow Pipeline ──────────────────────────────── */}
      <section id="workflow" className="py-24 px-6 bg-[hsl(var(--surface))]">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <motion.p variants={fadeUp} custom={0} className="text-xs font-mono text-[hsl(var(--accent2,192_91%_36%))] uppercase tracking-widest mb-3">
              AI Pipeline
            </motion.p>
            <motion.h2 variants={fadeUp} custom={1} className="text-3xl sm:text-4xl font-bold mb-4">
              How RTI-Agent Works
            </motion.h2>
            <motion.p variants={fadeUp} custom={2} className="text-[hsl(var(--text-muted))] max-w-xl mx-auto">
              Your query passes through a LangGraph-orchestrated pipeline of specialized AI agents.
            </motion.p>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="flex flex-wrap items-center justify-center gap-3"
          >
            {config.workflowNodes.map((node, i) => {
              const Icon = iconMap[node.icon] || Bot;
              return (
                <motion.div key={node.id} variants={fadeUp} custom={i} className="flex items-center gap-3">
                  <div className="flex flex-col items-center gap-2 p-4 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--bg))] min-w-[110px] hover:border-[hsl(var(--accent)/0.4)] hover:glow-accent transition-all duration-300">
                    <div className="w-10 h-10 rounded-lg bg-[hsl(var(--accent)/0.1)] flex items-center justify-center">
                      <Icon className="w-5 h-5 text-[hsl(var(--accent))]" />
                    </div>
                    <span className="text-xs font-semibold">{node.label}</span>
                    <span className="text-[10px] text-[hsl(var(--text-muted))]">{node.description}</span>
                  </div>
                  {i < config.workflowNodes.length - 1 && (
                    <ChevronRight className="w-4 h-4 text-[hsl(var(--text-muted))] hidden sm:block" />
                  )}
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </section>

      {/* ── Departments ────────────────────────────────────── */}
      <section id="departments" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} className="text-center mb-16">
            <motion.p variants={fadeUp} custom={0} className="text-xs font-mono text-[hsl(var(--saffron))] uppercase tracking-widest mb-3">
              Supported Departments
            </motion.p>
            <motion.h2 variants={fadeUp} custom={1} className="text-3xl sm:text-4xl font-bold mb-4">
              File RTIs Across Departments
            </motion.h2>
          </motion.div>

          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4"
          >
            {config.departments.map((dept, i) => {
              const Icon = iconMap[dept.icon] || Building2;
              return (
                <motion.div
                  key={dept.id}
                  variants={fadeUp}
                  custom={i}
                  className="group p-5 rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--surface))] text-center hover:border-opacity-50 transition-all duration-300 cursor-pointer"
                  style={{ ["--dept-color" as string]: dept.color }}
                >
                  <div
                    className="w-12 h-12 rounded-xl mx-auto mb-3 flex items-center justify-center group-hover:scale-110 transition-transform"
                    style={{ background: `${dept.color}15`, color: dept.color }}
                  >
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="font-semibold text-sm mb-1">{dept.name}</h3>
                  <p className="text-[10px] font-mono text-[hsl(var(--text-muted))]">{dept.shortName}</p>
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </section>

      {/* ── Stats Bar ──────────────────────────────────────── */}
      <section className="py-16 px-6 bg-[hsl(var(--surface))] border-y border-[hsl(var(--border))]">
        <div className="max-w-5xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-8">
          {[
            { value: "7", label: "AI Agents" },
            { value: "5", label: "Departments" },
            { value: "3", label: "Languages" },
            { value: "<30s", label: "Avg Response" },
          ].map((s) => (
            <div key={s.label} className="text-center">
              <p className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-[hsl(var(--accent))] to-[hsl(var(--accent2,192_91%_36%))] bg-clip-text text-transparent">
                {s.value}
              </p>
              <p className="text-xs text-[hsl(var(--text-muted))] mt-1 uppercase tracking-wider">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Footer ─────────────────────────────────────────── */}
      <footer className="py-12 px-6 border-t border-[hsl(var(--border))]">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-md bg-gradient-to-br from-[hsl(var(--accent))] to-[hsl(var(--accent2,192_91%_36%))] flex items-center justify-center">
              <Bot className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-semibold text-sm">RTI-Agent v2.0</span>
          </div>
          <p className="text-xs text-[hsl(var(--text-muted))]">
            © 2025 RTI-Agent. AI-Powered RTI Automation for India.
          </p>
          <div className="flex gap-6 text-xs text-[hsl(var(--text-muted))]">
            <a href="#" className="hover:text-[hsl(var(--text))] transition-colors">Privacy</a>
            <a href="#" className="hover:text-[hsl(var(--text))] transition-colors">Terms</a>
            <a href="#" className="hover:text-[hsl(var(--text))] transition-colors">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
