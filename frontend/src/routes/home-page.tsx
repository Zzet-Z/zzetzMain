import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { FinalCta } from "../components/home/final-cta";
import { Hero } from "../components/home/hero";
import { OutputPreview } from "../components/home/output-preview";
import { Problem } from "../components/home/problem";
import { Process } from "../components/home/process";
import { createSession } from "../lib/api";

export function HomePage() {
  const navigate = useNavigate();
  const [isCreating, setIsCreating] = useState(false);

  async function handleStart() {
    if (isCreating) {
      return;
    }

    setIsCreating(true);
    try {
      const payload = await createSession();
      navigate(`/session/${payload.token}`);
    } catch (_error) {
      setIsCreating(false);
    }
  }

  return (
    <main className="min-h-screen bg-[var(--color-bg)] text-white">
      <Hero loading={isCreating} onStart={() => void handleStart()} />
      <Problem />
      <Process />
      <OutputPreview />
      <FinalCta loading={isCreating} onStart={() => void handleStart()} />
    </main>
  );
}
