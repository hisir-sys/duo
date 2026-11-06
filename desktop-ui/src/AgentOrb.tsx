import { useEffect, useState } from "react";

export function AgentOrb({ compact = false }: { compact?: boolean }) {
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setReduced(media.matches);
    update();
    media.addEventListener?.("change", update);
    return () => media.removeEventListener?.("change", update);
  }, []);

  return (
    <div
      className={["orb", compact ? "compact" : "", reduced ? "static" : ""].filter(Boolean).join(" ")}
      role="img"
      aria-label="DuoAI assistant orb"
    >
      <span className="orb-aura" />
      <span className="orb-shell" />
      <span className="orb-flow orb-flow-one" />
      <span className="orb-flow orb-flow-two" />
      <span className="orb-highlight" />
      <span className="orb-ring" />
    </div>
  );
}
