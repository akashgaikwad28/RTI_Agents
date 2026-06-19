import type { Metadata } from "next";
import { Providers } from "@/providers";
import "./globals.css";

export const metadata: Metadata = {
  title: "RTI-Agent — AI-Powered RTI Automation",
  description:
    "File and track Right to Information requests powered by AI agents. Modern, secure, and multilingual governance platform.",
  keywords: ["RTI", "Right to Information", "AI", "India", "Government", "Governance"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
