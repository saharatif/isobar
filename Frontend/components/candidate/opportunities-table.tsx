import type { Opportunity } from "@/lib/types";

type OpportunitiesTableProps = {
  opportunities: Opportunity[];
};

export function OpportunitiesTable({ opportunities }: OpportunitiesTableProps) {
  return (
    <section className="overflow-hidden rounded-[14px] border border-border-soft bg-panel shadow-panel">
      <div className="flex flex-col gap-2 border-b border-border-soft p-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-text-2">Matching opportunities</p>
          <h2 className="mt-1 font-display text-2xl font-semibold">Ranked live openings</h2>
        </div>
        <div className="font-mono text-sm text-text-2">{opportunities.length} shown</div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] border-collapse text-left text-sm">
          <thead className="bg-panel-2 text-xs uppercase tracking-[0.14em] text-text-2">
            <tr>
              <th className="px-5 py-3 font-medium">Region</th>
              <th className="px-5 py-3 font-medium">Role focus</th>
              <th className="px-5 py-3 font-medium">Seniority</th>
              <th className="px-5 py-3 font-medium">Comp band</th>
              <th className="px-5 py-3 font-medium">Openings</th>
              <th className="px-5 py-3 font-medium">Match</th>
            </tr>
          </thead>
          <tbody>
            {opportunities.map((opportunity) => (
              <tr key={opportunity.id} className="border-t border-border-soft/80">
                <td className="px-5 py-4 text-text-1">{opportunity.region}</td>
                <td className="px-5 py-4 text-text-1">{opportunity.roleFocus}</td>
                <td className="px-5 py-4">
                  <span className="rounded-full border border-border-soft bg-panel-2 px-3 py-1 text-xs font-semibold text-cyan">
                    {opportunity.seniority}
                  </span>
                </td>
                <td className="px-5 py-4 font-mono text-text-1">{opportunity.compBand}</td>
                <td className="px-5 py-4 font-mono text-text-2">{opportunity.openings}</td>
                <td className="px-5 py-4">
                  <span className="font-mono text-base font-semibold text-amber">{opportunity.matchPercent}%</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
