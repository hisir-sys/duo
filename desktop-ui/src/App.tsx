import { useEffect, useMemo, useState } from "react";
import { Activity, Bell, BookOpen, Check, ChevronDown, Code2, FolderKanban, GitPullRequest, Gauge, LayoutDashboard, Moon, Search, Settings2, ShieldCheck, Sun, Users, Workflow, Bot, BrainCircuit, FlaskConical, Sparkles, ArrowUpRight, CircleDot } from "lucide-react";
import { AgentOrb } from "./AgentOrb";

const updates = [
  ["OR", "Orchestrator prepared a project plan", "Website refresh · 8 minutes ago", "Planning"],
  ["RV", "Review is waiting for your approval", "API integration · 24 minutes ago", "Review"],
  ["CD", "Coding worker completed a proposal", "Desktop UI · 1 hour ago", "Completed"],
  ["RS", "Research notes were added", "Provider comparison · 2 hours ago", "Research"]
];

const agents = [
  { id: "orchestrator", name: "Master Orchestrator", short: "Orchestrator", role: "Planning & coordination", type: "Coordination", icon: BrainCircuit, color: "blue", description: "Coordinates the work. It reads project context, breaks requests into tasks, and routes work to the right specialist.", responsibilities: ["Understand the request and project context", "Create a structured execution plan", "Assign work to specialist agents", "Collect results for a final response"], tools: ["Project context", "Task planning", "Worker routing"], model: "Configured by backend", state: "Preview profile" },
  { id: "coding", name: "Coding Agent", short: "Coding", role: "Implementation", type: "Build", icon: Code2, color: "slate", description: "Works on implementation tasks in an isolated workspace, keeping proposed changes separate until they are ready to review.", responsibilities: ["Inspect relevant source files", "Implement approved code changes", "Keep changes scoped to the task", "Summarise files changed"], tools: ["Repository workspace", "Code editing", "Change summary"], model: "Configured by backend", state: "Preview profile" },
  { id: "testing", name: "Testing Agent", short: "Testing", role: "Quality assurance", type: "Quality", icon: FlaskConical, color: "green", description: "Checks proposed work with the project's available tests and reports failures or areas that still need attention.", responsibilities: ["Identify relevant tests", "Run available checks", "Report failures clearly", "Summarise verification limits"], tools: ["Test runner", "Validation reports", "Issue summaries"], model: "Configured by backend", state: "Preview profile" },
  { id: "review", name: "Review Agent", short: "Review", role: "Code review & safety", type: "Quality", icon: ShieldCheck, color: "amber", description: "Reviews proposed changes for correctness, scope, maintainability, and potential regressions before they are accepted.", responsibilities: ["Review the change set", "Look for regressions and edge cases", "Check scope and project conventions", "Return actionable findings"], tools: ["Diff inspection", "Review checklist", "Finding reports"], model: "Configured by backend", state: "Preview profile" },
  { id: "research", name: "Research Agent", short: "Research", role: "Technical research", type: "Research", icon: BookOpen, color: "violet", description: "Gathers and organises technical information to support decisions, comparisons, and implementation plans.", responsibilities: ["Investigate a technical question", "Compare suitable approaches", "Record sources and trade-offs", "Deliver a concise research brief"], tools: ["Research workspace", "Source notes", "Comparison briefs"], model: "Configured by backend", state: "Preview profile" }
];

function Nav({ icon: Icon, label, active = false, onClick }: any) {
  return <button className={active ? "nav-item active" : "nav-item"} onClick={onClick} aria-current={active ? "page" : undefined}><Icon size={16}/><span>{label}</span>{!active && <small>Soon</small>}</button>;
}
function Metric({ label, value, note, icon: Icon, warm = false }: any) {
  return <article className={warm ? "metric warm" : "metric"}><div className="metric-head"><span>{label}</span><Icon size={17}/></div><strong>{value}</strong><small>{note}</small></article>;
}
function AgentsScreen({ query }: { query: string }) {
  const [filter, setFilter] = useState("All profiles");
  const [selectedId, setSelectedId] = useState("orchestrator");
  const filters = ["All profiles", "Coordination", "Build", "Quality", "Research"];
  const visibleAgents = useMemo(() => agents.filter(agent => {
    const matchesFilter = filter === "All profiles" || agent.type === filter;
    const matchesQuery = [agent.name, agent.role, agent.type, agent.description].join(" ").toLowerCase().includes(query.toLowerCase());
    return matchesFilter && matchesQuery;
  }), [filter, query]);
  const selected = agents.find(agent => agent.id === selectedId) ?? agents[0];
  const SelectedIcon = selected.icon;
  return <div className="content agent-content">
    <section className="welcome agent-welcome"><div><label>— YOUR TEAM</label><h1>Meet your agents.</h1><p>Specialist roles, coordinated by one central orchestrator.</p></div><span className="preview">● UI PREVIEW · SAMPLE PROFILES</span></section>
    <section className="agent-summary">
      <article><span className="summary-icon"><Users size={17}/></span><div><strong>05</strong><small>Agent profiles</small></div></article>
      <article><span className="summary-icon"><BrainCircuit size={17}/></span><div><strong>01</strong><small>Orchestrator</small></div></article>
      <article><span className="summary-icon"><Bot size={17}/></span><div><strong>04</strong><small>Worker roles</small></div></article>
      <div className="connection-note"><CircleDot size={14}/><span>Backend connection pending</span></div>
    </section>
    <div className="agent-layout">
      <section className="agent-list-panel">
        <div className="agent-list-head"><div><label>AGENT DIRECTORY</label><h2>All profiles <span>{visibleAgents.length}</span></h2></div><span className="profile-note">Designed roles · not live sessions</span></div>
        <div className="agent-filters" role="group" aria-label="Filter agents">
          {filters.map(item => <button key={item} className={filter === item ? "selected" : ""} onClick={() => setFilter(item)}>{item}</button>)}
        </div>
        <div className="agent-cards">
          {visibleAgents.map(agent => {
            const Icon = agent.icon;
            return <button key={agent.id} className={selectedId === agent.id ? "agent-card selected" : "agent-card"} onClick={() => setSelectedId(agent.id)} aria-pressed={selectedId === agent.id}>
              <span className={"agent-avatar " + agent.color}><Icon size={19}/></span>
              <span className="agent-card-copy"><strong>{agent.name}</strong><small>{agent.role}</small><em><i/>{agent.state}</em></span>
              <ArrowUpRight size={16} className="agent-open"/>
            </button>;
          })}
          {!visibleAgents.length && <div className="agent-empty">No agent profiles match this search.</div>}
        </div>
      </section>
      <aside className="agent-detail">
        <div className="detail-top"><span>PROFILE DETAILS</span><span className="detail-preview">PREVIEW</span></div>
        <div className={"detail-avatar " + selected.color}><SelectedIcon size={25}/></div>
        <h2>{selected.name}</h2><p className="detail-role">{selected.role}</p>
        <div className="detail-state"><span><CircleDot size={13}/>{selected.state}</span><small>Not connected to a live session</small></div>
        <p className="detail-description">{selected.description}</p>
        <div className="detail-section"><h3>Responsibilities</h3>{selected.responsibilities.map(item => <div className="detail-line" key={item}><Check size={14}/><span>{item}</span></div>)}</div>
        <div className="detail-section"><h3>Capability areas</h3><div className="capability-tags">{selected.tools.map(item => <span key={item}>{item}</span>)}</div></div>
        <div className="detail-model"><span>MODEL CONFIGURATION</span><strong>{selected.model}</strong><small>Actual provider and model are managed by the existing backend.</small></div>
      </aside>
    </div>
    <section className="agent-flow-note"><span><Workflow size={17}/></span><div><strong>One coordinator. Four specialists.</strong><p>The Orchestrator plans and delegates; worker profiles describe the specialist roles. Live execution, logs, and configuration will appear after the gradual backend connection is implemented.</p></div></section>
    <footer className="page-foot"><span>DuoAI Studio · Agents UI preview</span><span>Profile descriptions only · No backend actions exposed</span></footer>
  </div>;
}
export default function App() {
  const [query, setQuery] = useState("");
  const [low, setLow] = useState(false);
  const [page, setPage] = useState<"Home" | "Agents">("Home");
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    const saved = localStorage.getItem("duoai-theme");
    return saved === "dark" ? "dark" : "light";
  });
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("duoai-theme", theme);
  }, [theme]);
  const bars = [32, 48, 39, 66, 54, 78, 62];
  const visible = updates.filter((row) => row.join(" ").toLowerCase().includes(query.toLowerCase()));
  return <div className={low ? "shell low" : "shell"}>
    <aside className="sidebar">
      <div className="brand"><img src="./duo-mark.svg" alt=""/><b>DuoAI <small>STUDIO</small></b></div>
      <div className="workspace"><span>D</span><div><b>Personal workspace</b><small>Free workspace</small></div><ChevronDown size={14}/></div>
      <nav>
        <label>OVERVIEW</label><Nav icon={LayoutDashboard} label="Home" active={page === "Home"} onClick={() => { setPage("Home"); setQuery(""); }}/><Nav icon={FolderKanban} label="Projects"/>
        <label>TEAM</label><Nav icon={Users} label="Agents" active={page === "Agents"} onClick={() => { setPage("Agents"); setQuery(""); }}/><Nav icon={Workflow} label="Master Control Room"/>
        <label>WORK</label><Nav icon={BookOpen} label="Workspace"/><Nav icon={GitPullRequest} label="Review Center"/>
        <label>ACCOUNT</label><Nav icon={Settings2} label="Settings"/>
      </nav>
      <div className="side-bottom"><div className="profile"><span>S</span><div><b>Studio owner</b><small>Local preview</small></div></div></div>
    </aside>
    <main>
      <header className="topbar"><div className="crumb">Overview <i>/</i> <b>{page}</b></div><div className="top-actions"><span className="bridge"><i/>Backend bridge pending</span><div className="search"><Search size={15}/><input placeholder={page === "Agents" ? "Search agent profiles..." : "Search activity..."} value={query} onChange={e=>setQuery(e.target.value)}/></div><button className="icon-btn" aria-label="Notifications"><Bell size={17}/></button><button className="icon-btn theme-toggle" aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"} title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"} onClick={()=>setTheme(current=>current === "dark" ? "light" : "dark")}>{theme === "dark" ? <Sun size={17}/> : <Moon size={17}/>}</button><AgentOrb compact/></div></header>
      {page === "Agents" ? <AgentsScreen query={query}/> : <div className="content">
        <section className="welcome"><div><label>— YOUR WORKSPACE</label><h1>Good to see you.</h1><p>Here’s what’s happening across your projects today.</p></div><span className="preview">● UI PREVIEW · SAMPLE DATA</span></section>
        <section className="metrics">
          <Metric label="Active projects" value="04" note="↗ 2 this month" icon={FolderKanban}/>
          <Metric label="Tasks in progress" value="12" note="Across 4 projects" icon={Activity}/>
          <Metric label="Reviews waiting" value="03" note="Needs your attention" icon={GitPullRequest} warm/>
          <article className="metric"><div className="metric-head"><span>Completion rate</span><Gauge size={17}/></div><div className="gauge"><svg viewBox="0 0 100 58"><path d="M10 50 A40 40 0 0 1 90 50" className="track"/><path d="M10 50 A40 40 0 0 1 90 50" className="value"/></svg><b>78<small>%</small></b></div><small>↗ 6.4% vs. last month</small></article>
        </section>
        <section className="middle">
          <article className="panel project"><div className="panel-head"><div><label>YOUR WORK</label><h2>Project activity</h2></div><span>View projects ↗</span></div>
            <div className="project-row"><div className="project-icon"><Workflow size={18}/></div><div><b>Desktop experience refresh</b><small>Updated a few minutes ago</small></div><em>In progress</em></div>
            <div className="progress-label"><span>Overall progress</span><b>68%</b></div><div className="progress"><i/></div><div className="project-meta"><span>◉ ◉ ◉ &nbsp;3 workers assigned</span><span>5 of 8 tasks complete</span></div>
            <hr/><div className="chart-head"><div><b>Weekly activity</b><small>Task updates over the last 7 days</small></div><span>● Activity</span></div>
            <div className="chart">{bars.map((n,i)=><div key={i}><i style={{height:n+"%"}}/><small>{"MTWTFSS"[i]}</small></div>)}</div>
          </article>
          <div className="right-col">
            <article className="focus"><div className="focus-head"><span><Sparkles size={14}/> ORCHESTRATOR</span><small>PREVIEW</small></div><div className="focus-body"><div><h2>One clear view.<br/>Every moving part.</h2><p>Your AI team’s command layer will live here.</p></div><AgentOrb/></div><footer>● Waiting for backend connection <b>↗</b></footer></article>
            <article className="review"><div className="review-head"><GitPullRequest size={17}/><b>REVIEW QUEUE</b><strong>03</strong></div><h3>Good work deserves a second look.</h3><p>Proposed changes will appear here when the review workflow is connected.</p><footer>Approval workflow <b>Not connected</b></footer></article>
          </div>
        </section>
        <section className="panel recent"><div className="panel-head"><div><label>LATEST UPDATES</label><h2>Recent activity</h2></div><small>Sample timeline · not live backend data</small></div>
          {visible.map((row)=><div className="feed" key={row[0]}><span className="avatar">{row[0]}</span><div><b>{row[1]}</b><small>{row[2]}</small></div><em>{row[3]}</em><Check size={14}/></div>)}
          {!visible.length && <p className="empty">No sample activity matches that search.</p>}
        </section>
        <footer className="page-foot"><span>DuoAI Studio · Desktop UI preview</span><span>Python backend unchanged · Electron shell only</span></footer>
      </div>}
    </main>
    <button className="effects" onClick={()=>setLow(v=>!v)}><i className={low ? "on" : ""}/>{low ? "Low effects on" : "Low effects off"}</button>
  </div>;
}
