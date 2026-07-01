import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(date));
}

export function truncate(str: string, len: number): string {
  return str.length > len ? str.slice(0, len) + "..." : str;
}

export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function statusColor(status: string): string {
  const map: Record<string, string> = {
    submitted: "bg-blue-500/15 text-blue-400 border-blue-500/30",
    pending: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    approved: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    rejected: "bg-red-500/15 text-red-400 border-red-500/30",
    processing: "bg-violet-500/15 text-violet-400 border-violet-500/30",
    completed: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    closed: "bg-slate-500/15 text-slate-400 border-slate-500/30",
  };
  return map[status.toLowerCase()] ?? map.pending;
}
