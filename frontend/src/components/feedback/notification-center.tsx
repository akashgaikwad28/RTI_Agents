"use client";

import { Bell, CheckCheck } from "lucide-react";
import { useNotificationsStore } from "@/stores/notifications-store";

export function NotificationCenter() {
  const items = useNotificationsStore((state) => state.items);
  const markAllRead = useNotificationsStore((state) => state.markAllRead);
  const unread = items.filter((item) => !item.read).length;

  return (
    <section className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--surface))] p-4">
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bell className="h-4 w-4 text-[hsl(var(--accent))]" />
          <h2 className="text-sm font-semibold">Notifications</h2>
        </div>
        <button type="button" className="text-xs text-[hsl(var(--accent))]" onClick={() => markAllRead()}>
          <CheckCheck className="mr-1 inline h-3 w-3" />
          Mark all read
        </button>
      </div>
      <div className="space-y-2">
        {items.length === 0 ? (
          <p className="text-sm text-[hsl(var(--text-muted))]">No notifications yet.</p>
        ) : (
          items.slice(0, 6).map((item) => (
            <div key={item.id} className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--bg))] p-3">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-medium">{item.title}</p>
                {!item.read && <span className="h-2 w-2 rounded-full bg-[hsl(var(--accent))]" />}
              </div>
              <p className="mt-1 text-xs text-[hsl(var(--text-muted))]">{item.message}</p>
            </div>
          ))
        )}
      </div>
      {unread > 0 && <p className="mt-3 text-xs text-[hsl(var(--text-muted))]">{unread} unread alerts</p>}
    </section>
  );
}

