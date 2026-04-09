import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { FinalCta } from "../components/home/final-cta";
import { Hero } from "../components/home/hero";
import { OutputPreview } from "../components/home/output-preview";
import { Problem } from "../components/home/problem";
import { Process } from "../components/home/process";
import { TokenEntry } from "../components/home/token-entry";

export function HomePage() {
  const navigate = useNavigate();
  const [isTokenEntryVisible, setIsTokenEntryVisible] = useState(false);
  const [token, setToken] = useState("");

  function handleStart() {
    setIsTokenEntryVisible(true);
  }

  function handleSubmitToken() {
    const normalizedToken = token.trim();
    if (!normalizedToken) {
      return;
    }

    navigate(`/session/${normalizedToken}`);
  }

  return (
    <main className="min-h-screen bg-[var(--color-bg)] text-white">
      <Hero loading={false} onStart={handleStart} />
      {isTokenEntryVisible ? (
        <TokenEntry
          value={token}
          onChange={setToken}
          onSubmit={handleSubmitToken}
        />
      ) : null}
      <Problem />
      <Process />
      <OutputPreview />
      <FinalCta loading={false} onStart={handleStart} />
    </main>
  );
}
