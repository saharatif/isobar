import { Download, Search, Upload } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export function TopBar() {
  return (
    <header className="flex flex-col gap-3 rounded-[14px] border border-border-soft bg-panel/88 p-3 shadow-panel backdrop-blur lg:flex-row lg:items-center lg:justify-between">
      <div className="min-w-0">
        <div className="text-xs font-medium uppercase tracking-[0.18em] text-text-2">Resume analysis</div>
        <h1 className="mt-1 truncate font-display text-xl font-semibold">Live session</h1>
      </div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <label className="flex h-10 min-w-0 items-center gap-2 rounded-lg border border-border-soft bg-panel-2 px-3 text-text-2 sm:w-[300px]">
          <Search className="size-4 shrink-0" />
          <input
            className="min-w-0 flex-1 bg-transparent text-sm text-text-1 outline-none placeholder:text-text-2"
            placeholder="Search markets, roles, skills"
          />
        </label>
        <Button variant="secondary" type="button">
          <Download className="size-4" />
          Export report
        </Button>
        <Link
          href="/upload"
          className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-amber px-4 text-sm font-semibold text-ink transition hover:bg-amber/90"
        >
          <Upload className="size-4" />
          Upload resume
        </Link>
      </div>
    </header>
  );
}
