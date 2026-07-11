import { NavRail } from "@/components/layout/nav-rail";
import { TopBar } from "@/components/layout/top-bar";

export default function AppLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="min-h-screen bg-ink text-text-1">
      <NavRail />
      <main className="min-h-screen pl-[76px]">
        <div className="mx-auto flex w-full max-w-[1280px] flex-col gap-5 px-5 py-5 lg:px-8">
          <TopBar />
          {children}
        </div>
      </main>
    </div>
  );
}
