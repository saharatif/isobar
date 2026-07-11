"use client";

import { useMemo, useState } from "react";
import type { Hotspot } from "@/lib/types";
import { cn } from "@/lib/utils";

type DemandHeatmapProps = {
  hotspots: Hotspot[];
  scope: "thisRole" | "allMatches";
};

const tierColor = {
  cool: "var(--cyan)",
  warm: "var(--amber)",
  hot: "var(--crimson)"
};

const landMasses = [
  "M92 147c30-40 80-50 123-30 27 13 42 35 35 58-7 25-42 31-70 24-44-11-91-13-106 17-10 20 2 39 18 48Z",
  "M214 246c33-8 76 12 87 43 11 33-15 80-48 88-25 6-46-19-53-49-6-28-21-70 14-82Z",
  "M360 130c45-30 117-22 151 16 25 29 19 63-19 80-47 22-118 7-145-29-18-24-13-50 13-67Z",
  "M455 242c37-16 84-4 108 27 29 39 16 94-24 119-34 22-78 4-94-35-15-37-23-97 10-111Z",
  "M603 168c46-31 129-24 176 15 41 34 32 82-18 99-58 20-137-4-169-47-20-27-16-50 11-67Z",
  "M741 343c31-12 80-3 103 20 25 26 10 62-27 70-40 9-84-10-98-39-11-23-2-42 22-51Z"
];

function project(lon: number, lat: number) {
  return {
    x: ((lon + 180) / 360) * 920,
    y: ((90 - lat) / 180) * 460
  };
}

export function DemandHeatmap({ hotspots, scope }: DemandHeatmapProps) {
  const [activeScope, setActiveScope] = useState(scope);
  const [hovered, setHovered] = useState<Hotspot | null>(null);

  const maxRoles = useMemo(() => Math.max(...hotspots.map((spot) => spot.openRoles), 1), [hotspots]);

  return (
    <section className="relative min-h-[520px] overflow-hidden rounded-[14px] border border-border-soft bg-panel p-5 shadow-panel">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-text-2">Global demand heatmap</p>
          <h2 className="mt-1 font-display text-2xl font-semibold">Hiring hotspots</h2>
        </div>
        <div className="grid grid-cols-2 rounded-lg border border-border-soft bg-panel-2 p-1 text-xs font-semibold">
          {[
            ["thisRole", "This role"],
            ["allMatches", "All matches"]
          ].map(([value, label]) => (
            <button
              key={value}
              type="button"
              onClick={() => setActiveScope(value as typeof activeScope)}
              className={cn(
                "rounded-md px-3 py-2 transition",
                activeScope === value ? "bg-amber text-ink" : "text-text-2 hover:text-text-1"
              )}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
      <div className="relative h-[410px] overflow-hidden rounded-[14px] border border-border-soft bg-ink/45">
        <svg viewBox="0 0 920 460" role="img" aria-label="World demand heatmap" className="h-full w-full">
          <defs>
            <pattern id="cartogram-dots" width="18" height="18" patternUnits="userSpaceOnUse">
              <circle cx="3" cy="3" r="1.4" fill="#2A3552" />
            </pattern>
          </defs>
          <rect width="920" height="460" fill="url(#cartogram-dots)" opacity="0.75" />
          {landMasses.map((path, index) => (
            <path key={index} d={path} fill="#17213A" stroke="#26304B" strokeWidth="1.2" opacity="0.94" />
          ))}
          {hotspots.map((spot) => {
            const point = project(spot.lon, spot.lat);
            const radius = 5 + (spot.openRoles / maxRoles) * 10;
            const color = tierColor[spot.tier];
            return (
              <g
                key={`${spot.city}-${spot.country}`}
                transform={`translate(${point.x} ${point.y})`}
                onMouseEnter={() => setHovered(spot)}
                onMouseLeave={() => setHovered(null)}
                className="cursor-pointer"
              >
                <circle r={radius * 1.8} fill={color} opacity="0.18" className="origin-center animate-[pulse-marker_2.4s_ease-out_infinite]" />
                <circle r={radius} fill={color} stroke="#090D18" strokeWidth={2} />
              </g>
            );
          })}
        </svg>
        {hovered ? (
          <div className="pointer-events-none absolute right-4 top-4 w-56 rounded-[14px] border border-border-soft bg-panel-2 p-4 shadow-panel">
            <div className="font-display text-lg font-semibold">{hovered.city}</div>
            <div className="text-sm text-text-2">{hovered.country}</div>
            <div className="mt-3 grid grid-cols-2 gap-3 font-mono text-sm">
              <div>
                <div className="text-text-2">Score</div>
                <div className="text-amber">{hovered.demandScore}</div>
              </div>
              <div>
                <div className="text-text-2">Roles</div>
                <div className="text-cyan">{hovered.openRoles}</div>
              </div>
              <div className="col-span-2 text-text-2">
                {hovered.lat.toFixed(2)}, {hovered.lon.toFixed(2)}
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </section>
  );
}
