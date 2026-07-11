"use client";

import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";
import type { Domain } from "@/lib/types";

type ExpertiseDonutProps = {
  domains: Domain[];
  centerLabel: string;
};

export function ExpertiseDonut({ domains, centerLabel }: ExpertiseDonutProps) {
  return (
    <section className="rounded-[14px] border border-border-soft bg-panel p-5 shadow-panel">
      <div className="mb-3">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-text-2">Expertise mix</p>
        <h2 className="mt-1 font-display text-xl font-semibold">Skill domains</h2>
      </div>
      <div className="relative h-56">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={domains} dataKey="weight" nameKey="name" innerRadius={66} outerRadius={92} paddingAngle={3}>
              {domains.map((domain) => (
                <Cell key={domain.name} fill={domain.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <div className="font-mono text-3xl font-semibold text-text-1">100%</div>
          <div className="text-xs text-text-2">{centerLabel}</div>
        </div>
      </div>
      <div className="grid gap-2">
        {domains.map((domain) => (
          <div key={domain.name} className="flex items-center justify-between gap-3 text-sm">
            <span className="flex min-w-0 items-center gap-2 text-text-2">
              <span className="size-2.5 rounded-full" style={{ background: domain.color }} />
              <span className="truncate">{domain.name}</span>
            </span>
            <span className="font-mono text-text-1">{domain.weight}%</span>
          </div>
        ))}
      </div>
    </section>
  );
}
