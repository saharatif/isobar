import type { SkillSignal } from "@/lib/types";

type SkillCloudProps = {
  skills: SkillSignal[];
};

export function SkillCloud({ skills }: SkillCloudProps) {
  return (
    <section className="rounded-[14px] border border-border-soft bg-panel p-5 shadow-panel">
      <div className="mb-4">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-text-2">Skill signal cloud</p>
        <h2 className="mt-1 font-display text-xl font-semibold">Strongest signals</h2>
      </div>
      <div className="flex flex-wrap gap-2">
        {skills.map((skill) => (
          <span
            key={skill.skill}
            className="rounded-lg border border-border-soft bg-panel-2 px-3 py-2 text-sm text-text-1"
            style={{ opacity: 0.62 + skill.weight / 260 }}
          >
            {skill.skill}
            <span className="ml-2 font-mono text-xs text-amber">{skill.weight}</span>
          </span>
        ))}
      </div>
    </section>
  );
}
