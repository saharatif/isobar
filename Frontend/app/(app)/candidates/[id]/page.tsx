import { DemandHeatmap } from "@/components/candidate/demand-heatmap";
import { ExpertiseDonut } from "@/components/candidate/expertise-donut";
import { OpportunitiesTable } from "@/components/candidate/opportunities-table";
import { SkillCloud } from "@/components/candidate/skill-cloud";
import { SummaryStrip } from "@/components/candidate/summary-strip";
import { TopRegions } from "@/components/candidate/top-regions";
import { getCandidateSnapshot } from "@/lib/api-client";

type CandidatePageProps = {
  params: Promise<{ id: string }>;
};

export default async function CandidatePage({ params }: CandidatePageProps) {
  const { id } = await params;
  const snapshot = await getCandidateSnapshot(id);

  return (
    <div className="grid gap-5">
      <SummaryStrip summary={snapshot.summary} />
      <section className="grid gap-5 lg:grid-cols-[minmax(0,1.55fr)_minmax(340px,0.9fr)]">
        <DemandHeatmap hotspots={snapshot.hotspots} scope="thisRole" />
        <aside className="grid gap-5">
          <ExpertiseDonut domains={snapshot.domains} centerLabel={`${snapshot.domains.length} domains`} />
          <TopRegions regions={snapshot.topRegions} />
          <SkillCloud skills={snapshot.skills} />
        </aside>
      </section>
      <OpportunitiesTable opportunities={snapshot.opportunities} />
    </div>
  );
}
