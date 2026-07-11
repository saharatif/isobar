"use client";

import { FileUp } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function UploadPage() {
  return (
    <section className="rounded-[14px] border border-border-soft bg-panel p-8 shadow-panel">
      <div className="mx-auto flex max-w-2xl flex-col items-center gap-5 rounded-[14px] border border-dashed border-text-2/40 bg-panel-2 p-12 text-center">
        <div className="flex size-14 items-center justify-center rounded-full bg-amber/15 text-amber">
          <FileUp className="size-7" />
        </div>
        <div>
          <h1 className="font-display text-2xl font-semibold">Upload resume</h1>
          <p className="mt-2 text-sm text-text-2">
            PDF and DOCX files will route through the upload BFF once the backend is connected.
          </p>
        </div>
        <Button type="button">Choose file</Button>
      </div>
    </section>
  );
}
