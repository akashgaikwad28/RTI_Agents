import { NotificationCenter } from "@/components/feedback/notification-center";
import { SectionHeader } from "@/components/ui/section-header";

export default function CitizenNotificationsPage() {
  return (
    <div className="space-y-6">
      <SectionHeader title="Notifications" description="Approval changes, AI alerts, and live RTI status updates appear here." />
      <NotificationCenter />
    </div>
  );
}
