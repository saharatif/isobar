export default function CandidateLoading() {
  return (
    <div className="grid gap-5">
      <div className="h-32 animate-pulse rounded-[14px] border border-border-soft bg-panel" />
      <div className="grid gap-5 lg:grid-cols-[minmax(0,1.55fr)_minmax(340px,0.9fr)]">
        <div className="h-[520px] animate-pulse rounded-[14px] border border-border-soft bg-panel" />
        <div className="h-[520px] animate-pulse rounded-[14px] border border-border-soft bg-panel" />
      </div>
    </div>
  );
}
