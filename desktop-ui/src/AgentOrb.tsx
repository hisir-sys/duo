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
  return <div className={["orb", compact ? "compact" : "", reduced ? "static" : ""].join(" ")} role="img" aria-label="DuoAI assistant preview">
    <span className="orb-halo"/><span className="orb-core"/><span className="orb-glint"/>
  </div>;
}