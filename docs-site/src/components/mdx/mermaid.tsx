"use client";

import mermaid from "mermaid";
import { useEffect, useRef, useState } from "react";
import { useTheme } from "next-themes";

export function Mermaid({ chart }: { chart: string }) {
  const { resolvedTheme } = useTheme();
  const [svg, setSvg] = useState<string>("");
  const id = useRef(`mermaid-${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: resolvedTheme === "dark" ? "dark" : "default",
    });

    const renderMermaid = async () => {
      try {
        const { svg: renderedSvg } = await mermaid.render(id.current, chart);
        setSvg(renderedSvg);
      } catch (error) {
        console.error("Mermaid parsing error:", error);
      }
    };

    renderMermaid();
  }, [chart, resolvedTheme]);

  return <div dangerouslySetInnerHTML={{ __html: svg }} />;
}
