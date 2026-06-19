"use client";

import { useRef } from "react";
import { Paperclip, UploadCloud, X } from "lucide-react";

interface FileDropzoneProps {
  files: File[];
  onChange: (files: File[]) => void;
  accept?: string;
  multiple?: boolean;
}

export function FileDropzone({ files, onChange, accept = ".pdf,.png,.jpg,.jpeg,.doc,.docx", multiple = true }: FileDropzoneProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  return (
    <div className="space-y-3">
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          const dropped = Array.from(event.dataTransfer.files);
          onChange(multiple ? [...files, ...dropped] : dropped.slice(0, 1));
        }}
        className="flex min-h-36 w-full flex-col items-center justify-center rounded-xl border border-dashed border-[hsl(var(--border))] bg-[hsl(var(--bg))] px-4 py-6 text-center"
      >
        <UploadCloud className="mb-3 h-7 w-7 text-[hsl(var(--accent))]" />
        <p className="text-sm font-medium">Drag files here or click to upload</p>
        <p className="mt-1 text-xs text-[hsl(var(--text-muted))]">PDF, image, and document uploads are supported.</p>
      </button>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        multiple={multiple}
        onChange={(event) => {
          const next = Array.from(event.target.files ?? []);
          onChange(multiple ? [...files, ...next] : next.slice(0, 1));
        }}
      />
      {files.length > 0 && (
        <div className="space-y-2">
          {files.map((file, index) => (
            <div key={`${file.name}-${index}`} className="flex items-center justify-between rounded-lg border border-[hsl(var(--border))] px-3 py-2 text-sm">
              <span className="inline-flex items-center gap-2">
                <Paperclip className="h-4 w-4 text-[hsl(var(--text-muted))]" />
                {file.name}
              </span>
              <button type="button" onClick={() => onChange(files.filter((_, fileIndex) => fileIndex !== index))}>
                <X className="h-4 w-4 text-[hsl(var(--text-muted))]" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

