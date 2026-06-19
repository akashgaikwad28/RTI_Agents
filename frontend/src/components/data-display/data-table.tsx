"use client";

import { useMemo, useState } from "react";
import { ArrowDownAZ, ArrowUpAZ, Download, Search } from "lucide-react";
import type { TableColumn } from "@/types/governance";

interface DataTableProps<T> {
  title: string;
  rows: T[];
  columns: Array<TableColumn<T>>;
}

export function DataTable<T extends object>({ title, rows, columns }: DataTableProps<T>) {
  const [query, setQuery] = useState("");
  const [sortKey, setSortKey] = useState<string>("");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const filtered = useMemo(() => {
    const lowered = query.toLowerCase();
    let next = rows.filter((row) => JSON.stringify(row).toLowerCase().includes(lowered));
    if (sortKey) {
      next = [...next].sort((left, right) => {
        const a = String((left as Record<string, unknown>)[sortKey] ?? "");
        const b = String((right as Record<string, unknown>)[sortKey] ?? "");
        return sortDir === "asc" ? a.localeCompare(b) : b.localeCompare(a);
      });
    }
    return next;
  }, [query, rows, sortDir, sortKey]);

  const exportCsv = () => {
    const header = columns.map((column) => column.label).join(",");
    const body = filtered
      .map((row) => columns.map((column) => JSON.stringify((row as Record<string, unknown>)[String(column.key)] ?? "")).join(","))
      .join("\n");
    const blob = new Blob([`${header}\n${body}`], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${title.toLowerCase().replace(/\s+/g, "-")}.csv`;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))]">
      <div className="flex flex-col gap-3 border-b border-[hsl(var(--border))] p-4 md:flex-row md:items-center md:justify-between">
        <h2 className="text-sm font-semibold">{title}</h2>
        <div className="flex flex-wrap items-center gap-2">
          <label className="flex items-center gap-2 rounded-lg border border-[hsl(var(--border))] px-3 py-2 text-xs">
            <Search className="h-3.5 w-3.5 text-[hsl(var(--text-muted))]" />
            <input value={query} onChange={(event) => setQuery(event.target.value)} className="bg-transparent outline-none" placeholder="Search" />
          </label>
          <button type="button" onClick={exportCsv} className="inline-flex items-center gap-2 rounded-lg border border-[hsl(var(--border))] px-3 py-2 text-xs">
            <Download className="h-3.5 w-3.5" />
            Export CSV
          </button>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-[hsl(var(--bg))] text-xs uppercase tracking-[0.16em] text-[hsl(var(--text-muted))]">
            <tr>
              {columns.map((column) => (
                <th key={String(column.key)} className="px-4 py-3">
                  <button
                    type="button"
                    className="inline-flex items-center gap-1"
                    onClick={() => {
                      if (!column.sortable) {
                        return;
                      }
                      const key = String(column.key);
                      setSortDir(sortKey === key && sortDir === "asc" ? "desc" : "asc");
                      setSortKey(key);
                    }}
                  >
                    {column.label}
                    {column.sortable && (sortDir === "asc" ? <ArrowUpAZ className="h-3.5 w-3.5" /> : <ArrowDownAZ className="h-3.5 w-3.5" />)}
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((row, index) => (
              <tr key={index} className="border-t border-[hsl(var(--border))]">
                {columns.map((column) => (
                  <td key={String(column.key)} className="px-4 py-3">
                    {column.render ? column.render(row) : String((row as Record<string, unknown>)[String(column.key)] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
