import { FinalCta } from "../components/home/final-cta";
import { Hero } from "../components/home/hero";
import { OutputPreview } from "../components/home/output-preview";
import { Problem } from "../components/home/problem";
import { Process } from "../components/home/process";

export function HomePage() {
  return (
    <main className="min-h-screen bg-[var(--color-bg)] text-white">
      <Hero />
      <Problem />
      <Process />
      <OutputPreview />
      <FinalCta />
    </main>
  );
}
