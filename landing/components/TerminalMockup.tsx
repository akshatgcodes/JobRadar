type Row = {
  rank: number;
  score: number;
  company: string;
  role: string;
};

const rows: Row[] = [
  { rank: 1, score: 94, company: "Razorpay", role: "Backend Engineer (Python)" },
  { rank: 2, score: 87, company: "Freshworks", role: "Python Developer - Integrations" },
  { rank: 3, score: 71, company: "Infosys", role: "Associate - Python & Django" },
];

function scoreColor(score: number) {
  if (score >= 80) return "text-emerald-400";
  if (score >= 50) return "text-amber-400";
  return "text-zinc-400";
}

export default function TerminalMockup() {
  return (
    <div className="w-full overflow-hidden rounded-xl border border-white/10 bg-[#0b0d10] shadow-2xl shadow-black/40">
      {/* title bar */}
      <div className="flex items-center gap-2 border-b border-white/10 bg-white/[0.03] px-4 py-3">
        <span className="h-3 w-3 rounded-full bg-[#ff5f56]" />
        <span className="h-3 w-3 rounded-full bg-[#ffbd2e]" />
        <span className="h-3 w-3 rounded-full bg-[#27c93f]" />
        <span className="ml-3 font-mono text-xs text-zinc-500">
          zsh — jobradar
        </span>
      </div>

      {/* body */}
      <div className="overflow-x-auto px-5 py-5 font-mono text-[13px] leading-relaxed sm:text-sm">
        <p className="whitespace-pre text-zinc-300">
          <span className="text-emerald-400">$</span> python jobradar.py
          --role &quot;Python Developer&quot; --location &quot;Bangalore&quot;
        </p>
        <p className="mt-3 text-zinc-500">
          Searching for &quot;Python Developer&quot; in &quot;Bangalore&quot;...
        </p>

        <div className="mt-4 min-w-[420px]">
          <div className="grid grid-cols-[3.5rem_4.5rem_1fr_1fr] gap-x-4 border-b border-white/10 pb-2 text-zinc-500">
            <span>Rank</span>
            <span>Score</span>
            <span>Company</span>
            <span>Role</span>
          </div>
          {rows.map((r) => (
            <div
              key={r.rank}
              className="grid grid-cols-[3.5rem_4.5rem_1fr_1fr] gap-x-4 border-b border-white/5 py-2 text-zinc-300"
            >
              <span className="text-zinc-500">{r.rank}</span>
              <span className={`font-semibold ${scoreColor(r.score)}`}>
                {r.score}%
              </span>
              <span>{r.company}</span>
              <span className="text-zinc-400">{r.role}</span>
            </div>
          ))}
          <div className="py-2 text-zinc-600">...</div>
        </div>

        <p className="mt-4 text-zinc-300">
          <span className="text-sky-400">📁</span> Full results exported to{" "}
          <span className="text-zinc-100">jobs_2023-11-14.csv</span>
        </p>
      </div>
    </div>
  );
}
