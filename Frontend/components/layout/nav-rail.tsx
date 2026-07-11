import { BarChart3, BriefcaseBusiness, Gauge, Settings, Upload } from "lucide-react";
import Link from "next/link";

const navItems = [
  { href: "/candidates/demo", label: "Dashboard", icon: Gauge },
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/dashboard", label: "Markets", icon: BarChart3 },
  { href: "/dashboard", label: "Roles", icon: BriefcaseBusiness },
  { href: "/dashboard", label: "Settings", icon: Settings }
];

export function NavRail() {
  return (
    <nav className="fixed inset-y-0 left-0 z-20 flex w-[76px] flex-col items-center border-r border-border-soft bg-ink/92 py-5 backdrop-blur">
      <Link
        href="/candidates/demo"
        className="mb-8 flex size-11 items-center justify-center rounded-[14px] border border-amber/30 bg-amber/15 font-display text-lg font-bold text-amber"
        aria-label="Isobar dashboard"
      >
        I
      </Link>
      <div className="flex flex-1 flex-col items-center gap-3">
        {navItems.map((item, index) => {
          const Icon = item.icon;
          return (
            <Link
              key={`${item.label}-${index}`}
              href={item.href}
              className="group relative flex size-11 items-center justify-center rounded-xl text-text-2 transition hover:bg-panel-2 hover:text-text-1"
              aria-label={item.label}
              title={item.label}
            >
              <Icon className="size-5" />
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
