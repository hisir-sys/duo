import { useState } from "react";
import { Activity, Bell, BookOpen, Check, ChevronDown, FolderKanban, GitPullRequest, Gauge, LayoutDashboard, Search, Settings2, Sparkles, Users, Workflow } from "lucide-react";
import { AgentOrb } from "./AgentOrb";

const updates = [
  ["OR", "Orchestrator prepared a project plan", "Website refresh · 8 minutes ago", "Planning"],
  ["RV", "Review is waiting for your approval", "API integration · 24 minutes ago", "Review"],
  ["CD", "Coding worker completed a proposal", "Desktop UI · 1 hour ago", "Completed"],
  ["RS", "Research notes were added", "Provider comparison · 2 hours ago", "Research"]
];

function Nav({ icon: Icon, label, active = false }: any) {
  return <button className={active ? "nav-item active" : "nav-item"} disabled={!active}><Icon size={16}/><span>{label}</span>{!active && <small>Soon</small>}</button>;
}
function Metric({ label, value, note, icon: Icon, warm = false }: any) {
  return <article className={warm ? "metric warm" : "metric"}><div className="metric-head"><span>{label}</span><Icon size={17}/></div><strong>{value}</strong><small>{note}</small></article>;
}
export default function App() {
  const [query, setQuery] = useState("");
  const [low, setLow] = useState(false);
  const bars = [32, 48, 39, 66, 54, 78, 62];
  const visible = updates.filter((row) => row.join(" ").toLowerCase().includes(query.toLowerCase()));
  return <div className={low ? "shell low" : "shell"}>
    <aside className="sidebar">
      <div className="brand"><img src="./duo-mark.svg" alt=""/><b>DuoAI <small>STUDIO</small></b></div>
      <div className="workspace"><span>D</span><div><b>Personal workspace</b><small>Free workspace</small></div><ChevronDown size={14}/></div>
      <nav>
        <label>OVERVIEW</label><Nav icon={LayoutDashboard} label="Home" active/><Nav icon={FolderKanban} label="Projects"/>
        <label>TEAM</label><Nav icon={Users} label="Agents"/><Nav icon={Workflow} label="Master Control Room"/>
        <label>WORK</label><Nav icon={BookOpen} label="Workspace"/><Nav icon={GitPullRequest} label="Review Center"/>
        <label>ACCOUNT</label><Nav icon={Settings2} label="Settings"/>
      </nav>
      <div className="side-bottom"><div className="profile"><span>S</span><div><b>Studio owner</b><small>Local preview</small></div></div></div>
    </aside>
    <main>
      <header className="topbar"><div className="crumb">Overview <i>/</i> <b>Home</b></div><div className="top-actions"><span className="bridge"><i/>Backend bridge pending</span><div className="search"><Search size={15}/><input placeholder="Search activity..." value={query} onChange={e=>setQuery(e.target.value)}/></div><button className="icon-btn" aria-label="Notifications"><Bell size={17}/></button><AgentOrb compact/></div></header>
      <div className="content">
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
      </div>
    </main>
    <button className="effects" onClick={()=>setLow(v=>!v)}><i className={low ? "on" : ""}/>{low ? "Low effects on" : "Low effects off"}</button>
  </div>;
}