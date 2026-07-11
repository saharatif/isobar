import type { RegionSignal } from "@/lib/types";

type TopRegionsProps = {
  regions: RegionSignal[];
};

export function TopRegions({ regions }: TopRegionsProps) {
  return (
    <section className="rounded-[14px] border border-border-soft bg-panel p-5 shadow-panel">
      <div className="mb-4">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-text-2">Top regions</p>
        <h2 className="mt-1 font-display text-xl font-semibold">Market fit</h2>
      </div>
      <div className="grid gap-4">
        {regions.map((region) => (
          <div key={region.region}>
            <div className="mb-2 flex items-center justify-between gap-3 text-sm">
              <span className="font-medium text-text-1">{region.region}</span>
              <span className="font-mono text-text-2">{region.roles} roles</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-panel-2">
              <div className="h-full rounded-full bg-gradient-to-r from-cyan via-amber to-crimson" style={{ width: `${region.score}%` }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
