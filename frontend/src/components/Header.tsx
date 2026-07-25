import { Cpu, ShieldCheck } from "lucide-react";

function Header() {
  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-icon">
          <Cpu size={22} />
        </div>

        <div className="brand-copy">
          <h1>Local RAG</h1>

          <p>Private Document Intelligence</p>

          <span className="brand-tagline">
            Retrieve • Augment • Generate
          </span>
        </div>
      </div>

      <div className="header-status">
        <div className="privacy-badge">
          <ShieldCheck size={15} />
          <span>Runs locally</span>
        </div>

        <div className="model-badge">
          <span className="status-dot" />
          Phi-4 Mini
        </div>
      </div>
    </header>
  );
}

export default Header;