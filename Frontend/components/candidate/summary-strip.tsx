import type { CandidateSummary } from "@/lib/types";

type SummaryStripProps = {
  summary: CandidateSummary;
};

export function SummaryStrip({ summary }: SummaryStripProps) {
  return (
    <section className="grid gap-5 rounded-[14px] border border-border-soft bg-panel p-5 shadow-panel lg:grid-cols-[minmax(0,1fr)_auto_auto] lg:items-center">
      <div className="flex min-w-0 items-center gap-4">
        <div className="flex size-16 shrink-0 items-center justify-center rounded-[14px] bg-gradient-to-br from-cyan/80 via-violet/70 to-amber/80 font-display text-xl font-bold text-ink">
          {summary.name
            .split(" ")
            .map((part) => part[0])
            .join("")
            .slice(0, 2)}
        </div>
        <div className="min-w-0">
          <h2 className="truncate font-display text-2xl font-semibold">{summary.name}</h2>
          <p className="mt-1 text-sm text-text-2">
            {summary.currentTitle} · {summary.yearsExperience} years · {summary.filename}
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {summary.topSkills.map((skill) => (
              <span key={skill} className="rounded-lg bg-panel-2 px-2.5 py-1 text-xs font-medium text-text-1">
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>
      <Metric label="Signal score" value={summary.signalScore} suffix="/100" />
      <Metric label="Markets matched" value={summary.marketsMatched} />
    </section>
  );
}

function Metric({ label, value, suffix }: { label: string; value: number; suffix?: string }) {
  return (
    <div className="min-w-[150px] rounded-[14px] border border-border-soft bg-panel-2 p-4">
      <div className="text-xs font-medium uppercase tracking-[0.16em] text-text-2">{label}</div>
      <div className="mt-2 font-mono text-3xl font-semibold text-amber">
        {value}
        {suffix ? <span className="text-base text-text-2">{suffix}</span> : null}
      </div>
    </div>
  );
}
