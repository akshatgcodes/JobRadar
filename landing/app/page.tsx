import TerminalMockup from "@/components/TerminalMockup";
import Badge from "@/components/Badge";

const techBadges = [
  "Python 3.8+",
  "BeautifulSoup4",
  "pandas",
  "requests",
  "argparse",
  "regex keyword scoring",
  "robots.txt awareness",
  "rate limiting",
  "config-driven skill profiles",
  "CSV export",
];

const skillProfileSnippet = `{
  "profile_name": "Python Backend / Data Roles",
  "skills": [
    { "keyword": "python",     "weight": 3.0 },
    { "keyword": "django",     "weight": 2.0 },
    { "keyword": "rest api",   "weight": 2.0 },
    { "keyword": "docker",     "weight": 1.5 },
    { "keyword": "kubernetes", "weight": 1.0 }
  ]
}`;

const flags: { flag: string; def: string; desc: string }[] = [
  { flag: "--role", def: "required", desc: "Role to search for" },
  { flag: "--location", def: "required", desc: "Location to search in" },
  {
    flag: "--skills-config",
    def: "config/skills_profile.json",
    desc: "Skill profile used to compute fit scores",
  },
  { flag: "--top-n", def: "10", desc: "Ranked rows to print to the console" },
  { flag: "--live", def: "off", desc: "Fetch a real job board instead of the local fixture" },
  { flag: "--rate-limit", def: "2.0", desc: "Seconds to sleep before each live request" },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-[#08090b] text-zinc-100 selection:bg-emerald-500/30">
      {/* ambient background glow */}
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 -z-10 bg-[radial-gradient(ellipse_60%_50%_at_50%_-10%,rgba(16,185,129,0.15),transparent)]"
      />

      <div className="mx-auto max-w-4xl px-6 pb-28">
        {/* ---------- Hero ---------- */}
        <header className="pt-20 sm:pt-28">
          <div className="flex flex-wrap items-center gap-2 font-mono text-xs uppercase tracking-widest text-emerald-400/80">
            <span>CLI tool</span>
            <span className="text-zinc-600">·</span>
            <span>Python</span>
            <span className="text-zinc-600">·</span>
            <span>November 2023</span>
          </div>

          <h1 className="mt-5 text-5xl font-bold tracking-tight text-zinc-50 sm:text-6xl">
            JobRadar
          </h1>

          <p className="mt-5 max-w-2xl text-xl leading-8 text-zinc-400">
            Stop scrolling job boards.{" "}
            <span className="text-zinc-100">
              Get a ranked, fit-scored shortlist
            </span>{" "}
            of the listings that actually match your skills, in one command.
          </p>

          <p className="mt-4 max-w-2xl text-base leading-7 text-zinc-500">
            A command-line tool that scrapes job listings by role and
            location, filters and deduplicates them, scores each one against
            a skills profile you define, and exports the ranked list to CSV.
            Run it daily to get a fresh, personalized shortlist instead of
            manually re-scrolling the same job boards.
          </p>

          <div className="mt-8 flex flex-wrap gap-3 font-mono text-sm">
            <a
              href="#x-factor"
              className="rounded-md border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-emerald-300 transition-colors hover:bg-emerald-500/20"
            >
              See the fit score →
            </a>
            <a
              href="#run-it"
              className="rounded-md border border-white/10 px-4 py-2 text-zinc-300 transition-colors hover:bg-white/5"
            >
              Run it
            </a>
          </div>
        </header>

        {/* ---------- Terminal mockup ---------- */}
        <section className="mt-16">
          <TerminalMockup />
        </section>

        {/* ---------- Tech badges ---------- */}
        <section className="mt-10 flex flex-wrap gap-2">
          {techBadges.map((t) => (
            <Badge key={t}>{t}</Badge>
          ))}
        </section>

        {/* ---------- X-Factor ---------- */}
        <section id="x-factor" className="mt-28 scroll-mt-10">
          <div className="flex items-center gap-3">
            <span className="h-px flex-1 bg-gradient-to-r from-emerald-500/60 to-transparent" />
            <span className="font-mono text-xs uppercase tracking-widest text-emerald-400">
              The X-Factor
            </span>
          </div>

          <h2 className="mt-4 text-3xl font-bold tracking-tight text-zinc-50 sm:text-4xl">
            A real fit score, not just a sort-by-date list
          </h2>

          <p className="mt-5 max-w-2xl text-base leading-7 text-zinc-400">
            Every listing gets a <span className="text-zinc-100">fit
            score</span> from 0–100% instead of being dumped in chronological
            order. It&apos;s a deterministic, weighted keyword match —
            no randomness, fully explainable:
          </p>

          <ol className="mt-6 space-y-4 text-base leading-7 text-zinc-400">
            <li className="flex gap-4">
              <span className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-500/10 font-mono text-xs text-emerald-400">
                1
              </span>
              <span>
                You define a skill profile in{" "}
                <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-sm text-zinc-200">
                  config/skills_profile.json
                </code>{" "}
                — keywords with weights, so you can tell JobRadar which
                skills matter most.
              </span>
            </li>
            <li className="flex gap-4">
              <span className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-500/10 font-mono text-xs text-emerald-400">
                2
              </span>
              <span>
                Every scraped job description is checked against each
                keyword with a case-insensitive, word-boundary regex — so{" "}
                <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-sm text-zinc-200">
                  sql
                </code>{" "}
                won&apos;t falsely match inside{" "}
                <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-sm text-zinc-200">
                  mysqlite
                </code>
                , and multi-word skills like{" "}
                <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-sm text-zinc-200">
                  rest api
                </code>{" "}
                are matched as a phrase.
              </span>
            </li>
            <li className="flex gap-4">
              <span className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-500/10 font-mono text-xs text-emerald-400">
                3
              </span>
              <span>
                The results are sorted by score, descending — the most
                relevant listings float to the top instead of being buried
                in an unsorted pile.
              </span>
            </li>
          </ol>

          <div className="mt-8 rounded-lg border border-white/10 bg-white/[0.03] p-5 font-mono text-sm text-zinc-300">
            <div className="text-zinc-500"># scoring.py</div>
            <div className="mt-2 whitespace-pre-wrap leading-7">
              fit_score = (sum of weights of skills{" "}
              <span className="text-emerald-400">FOUND</span> in the
              description){"\n"}
              {"            "}/ (sum of weights of{" "}
              <span className="text-zinc-100">ALL</span> skills in the
              profile){"\n"}
              {"            "}* 100
            </div>
          </div>

          <p className="mt-6 max-w-2xl text-base leading-7 text-zinc-400">
            Change{" "}
            <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-sm text-zinc-200">
              config/skills_profile.json
            </code>{" "}
            and every score, and the ranking, updates to reflect it — no
            code changes needed:
          </p>

          <pre className="mt-4 overflow-x-auto rounded-lg border border-white/10 bg-[#0b0d10] p-5 font-mono text-[13px] leading-relaxed text-zinc-300">
            {skillProfileSnippet}
          </pre>
        </section>

        {/* ---------- Key concepts / pipeline ---------- */}
        <section className="mt-28">
          <div className="flex items-center gap-3">
            <span className="h-px flex-1 bg-gradient-to-r from-zinc-600/60 to-transparent" />
            <span className="font-mono text-xs uppercase tracking-widest text-zinc-500">
              Pipeline
            </span>
          </div>

          <h2 className="mt-4 text-3xl font-bold tracking-tight text-zinc-50">
            Scrape → score → dedup → export
          </h2>

          <div className="mt-8 grid gap-4 sm:grid-cols-2">
            <div className="rounded-lg border border-white/10 bg-white/[0.02] p-5">
              <h3 className="font-mono text-sm text-emerald-400">
                scraper.py
              </h3>
              <p className="mt-2 text-sm leading-6 text-zinc-400">
                Parses job-board result cards with BeautifulSoup. Checks the
                target host&apos;s <code>robots.txt</code> via{" "}
                <code>urllib.robotparser</code> before any live fetch, and
                sleeps <code>--rate-limit</code> seconds (default 2s) before
                every request.
              </p>
            </div>
            <div className="rounded-lg border border-white/10 bg-white/[0.02] p-5">
              <h3 className="font-mono text-sm text-emerald-400">
                scoring.py
              </h3>
              <p className="mt-2 text-sm leading-6 text-zinc-400">
                The fit-score algorithm — weighted, regex-based,
                word-boundary keyword matching against your configurable
                skill profile.
              </p>
            </div>
            <div className="rounded-lg border border-white/10 bg-white/[0.02] p-5">
              <h3 className="font-mono text-sm text-emerald-400">
                dedup.py
              </h3>
              <p className="mt-2 text-sm leading-6 text-zinc-400">
                Listings are loaded into a pandas DataFrame and deduplicated
                on normalized <code>(company, role)</code>, keeping the
                highest-scoring copy of each.
              </p>
            </div>
            <div className="rounded-lg border border-white/10 bg-white/[0.02] p-5">
              <h3 className="font-mono text-sm text-emerald-400">
                jobradar.py
              </h3>
              <p className="mt-2 text-sm leading-6 text-zinc-400">
                The CLI entry point — wires the pipeline together with{" "}
                <code>argparse</code> and exports the final ranked set with{" "}
                <code>DataFrame.to_csv(...)</code>.
              </p>
            </div>
          </div>
        </section>

        {/* ---------- Run it ---------- */}
        <section id="run-it" className="mt-28 scroll-mt-10">
          <div className="flex items-center gap-3">
            <span className="h-px flex-1 bg-gradient-to-r from-emerald-500/60 to-transparent" />
            <span className="font-mono text-xs uppercase tracking-widest text-emerald-400">
              Run it
            </span>
          </div>

          <h2 className="mt-4 text-3xl font-bold tracking-tight text-zinc-50">
            Two commands, one ranked shortlist
          </h2>

          <p className="mt-4 max-w-2xl text-base leading-7 text-zinc-400">
            Requires Python 3.8+. By default it parses a bundled local HTML
            fixture so the full scrape → score → dedup → export pipeline
            runs offline, deterministically, with no live network calls.
          </p>

          <pre className="mt-6 overflow-x-auto rounded-lg border border-white/10 bg-[#0b0d10] p-5 font-mono text-sm leading-7 text-zinc-300">
            <span className="text-zinc-500"># install dependencies</span>
            {"\n"}
            <span className="text-emerald-400">$</span> pip install -r
            requirements.txt{"\n\n"}
            <span className="text-zinc-500"># search + score + export</span>
            {"\n"}
            <span className="text-emerald-400">$</span> python jobradar.py
            --role &quot;Python Developer&quot; --location &quot;Bangalore&quot;
          </pre>

          <div className="mt-8 overflow-x-auto rounded-lg border border-white/10">
            <table className="w-full min-w-[480px] border-collapse text-left font-mono text-sm">
              <thead>
                <tr className="border-b border-white/10 bg-white/[0.03] text-zinc-500">
                  <th className="px-4 py-3 font-normal">Flag</th>
                  <th className="px-4 py-3 font-normal">Default</th>
                  <th className="px-4 py-3 font-normal">Description</th>
                </tr>
              </thead>
              <tbody>
                {flags.map((f) => (
                  <tr
                    key={f.flag}
                    className="border-b border-white/5 last:border-0"
                  >
                    <td className="px-4 py-3 text-emerald-400">{f.flag}</td>
                    <td className="px-4 py-3 text-zinc-500">{f.def}</td>
                    <td className="px-4 py-3 text-zinc-300">{f.desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* ---------- Footer ---------- */}
        <footer className="mt-28 border-t border-white/10 pt-8 text-sm text-zinc-500">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <p>
              JobRadar · CLI Tool · Python · Licensed under{" "}
              <span className="text-zinc-300">GPLv3</span>
            </p>
            <p className="font-mono text-xs text-zinc-600">
              part of a 10-project portfolio
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}
