import { useEffect, useMemo, useState } from "react";
import { Activity, Bell, BookOpen, Check, ChevronDown, Code2, FolderKanban, GitPullRequest, Gauge, LayoutDashboard, Moon, Search, Settings2, ShieldCheck, Sun, Users, Workflow, Bot, BrainCircuit, FlaskConical, Sparkles, ArrowUpRight, CircleDot, GitBranch, Radio, ListChecks, ArrowRight, Clock3, FileCode2, FileText, Folder, ChevronRight, Plus, Play, Terminal, CircleCheck, CircleDashed, AlertTriangle, MessageSquare, FileDiff, GitCommit } from "lucide-react";


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
  return <button className={active ? "nav-item active" : "nav-item"} onClick={onClick} aria-current={active ? "page" : undefined}><Icon size={16}/><span>{label}</span>{!onClick && <small>Soon</small>}</button>;
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
const controlNodes = [
  { id: "orchestrator", name: "Master Orchestrator", role: "Plans and coordinates work", type: "Coordinator", icon: BrainCircuit, color: "blue", description: "The central coordinator reads the request and project context, creates a plan, and routes suitable tasks to specialist workers.", inputs: ["User request", "Project context"], outputs: ["Execution plan", "Assigned tasks"], stage: "Central coordinator" },
  { id: "coding", name: "Coding Agent", role: "Implements approved tasks", type: "Worker", icon: Code2, color: "slate", description: "Handles implementation in an isolated workspace and returns a proposed change set with a clear summary.", inputs: ["Assigned task", "Relevant source files"], outputs: ["Proposed code changes", "Change summary"], stage: "Specialist worker" },
  { id: "testing", name: "Testing Agent", role: "Runs relevant checks", type: "Worker", icon: FlaskConical, color: "green", description: "Runs available project checks against proposed work and reports what passed, failed, or could not be verified.", inputs: ["Proposed changes", "Project test setup"], outputs: ["Test results", "Failure details"], stage: "Specialist worker" },
  { id: "review", name: "Review Agent", role: "Inspects quality and scope", type: "Worker", icon: ShieldCheck, color: "amber", description: "Inspects the proposed change set for correctness, regressions, maintainability, and alignment with the requested scope.", inputs: ["Proposed changes", "Task requirements"], outputs: ["Review findings", "Approval recommendation"], stage: "Specialist worker" },
  { id: "research", name: "Research Agent", role: "Finds technical context", type: "Worker", icon: BookOpen, color: "violet", description: "Collects technical information and compares options to help the coordinator make informed implementation decisions.", inputs: ["Research question", "Project constraints"], outputs: ["Research notes", "Option comparison"], stage: "Specialist worker" }
];

function MasterControlRoom({ query }: { query: string }) {
  const [selectedId, setSelectedId] = useState("orchestrator");
  const selected = controlNodes.find(node => node.id === selectedId) ?? controlNodes[0];
  const SelectedIcon = selected.icon;
  const matches = controlNodes.filter(node => [node.name, node.role, node.description, node.type].join(" ").toLowerCase().includes(query.toLowerCase()));
  const workers = matches.filter(node => node.id !== "orchestrator");
  const showCoordinator = matches.some(node => node.id === "orchestrator");
  return <div className="content control-content">
    <section className="welcome control-welcome"><div><label>— ORCHESTRATION</label><h1>Master Control Room.</h1><p>A visual map of how the coordinator and specialist agents fit together.</p></div><span className="preview">● UI PREVIEW · STATIC WORKFLOW</span></section>
    <section className="control-summary">
      <article><span className="control-summary-icon"><BrainCircuit size={17}/></span><div><strong>01</strong><small>Coordinator</small></div></article>
      <article><span className="control-summary-icon"><Bot size={17}/></span><div><strong>04</strong><small>Specialist roles</small></div></article>
      <article><span className="control-summary-icon"><GitBranch size={17}/></span><div><strong>05</strong><small>Workflow profiles</small></div></article>
      <div className="control-status"><CircleDot size={14}/><span>Execution bridge not connected</span></div>
    </section>
    <div className="control-layout">
      <section className="control-map-panel">
        <div className="control-panel-head"><div><label>TEAM TOPOLOGY</label><h2>Orchestration map</h2></div><span className="map-legend"><i/> Profile preview</span></div>
        <div className="workflow-map">
          {showCoordinator && <button className={selectedId === "orchestrator" ? "workflow-node coordinator selected" : "workflow-node coordinator"} onClick={() => setSelectedId("orchestrator")}>
            <span className="workflow-node-icon blue"><BrainCircuit size={20}/></span><span className="workflow-node-copy"><small>MASTER · COORDINATION</small><strong>Master Orchestrator</strong><em>Plans · Delegates · Collects</em></span><ArrowUpRight size={16}/>
          </button>}
          {showCoordinator && <div className="workflow-connector"><i/><span>Task routing · conceptual</span><i/></div>}
          <div className="workflow-workers">
            {workers.map(node => { const Icon = node.icon; return <button key={node.id} className={selectedId === node.id ? "workflow-node worker selected" : "workflow-node worker"} onClick={() => setSelectedId(node.id)}>
              <span className={"workflow-node-icon " + node.color}><Icon size={18}/></span><span className="workflow-node-copy"><small>{node.type.toUpperCase()}</small><strong>{node.name}</strong><em>{node.role}</em></span><ArrowUpRight size={15}/>
            </button>; })}
          </div>
          {!matches.length && <div className="control-empty">No workflow profiles match this search.</div>}
          <div className="workflow-footnote"><Radio size={14}/> Connections illustrate intended responsibilities, not live agent traffic.</div>
        </div>
      </section>
      <aside className="control-detail">
        <div className="control-detail-head"><span>NODE INSPECTOR</span><span className="control-preview-tag">PREVIEW</span></div>
        <div className={"control-detail-icon " + selected.color}><SelectedIcon size={23}/></div>
        <h2>{selected.name}</h2><p className="control-detail-role">{selected.role}</p>
        <div className="control-detail-state"><CircleDot size={13}/><span>Not connected to a live session</span></div>
        <p className="control-detail-description">{selected.description}</p>
        <div className="control-detail-section"><h3><ArrowRight size={14}/> Inputs</h3>{selected.inputs.map(item => <span className="control-data-chip" key={item}>{item}</span>)}</div>
        <div className="control-detail-section"><h3><Check size={14}/> Outputs</h3>{selected.outputs.map(item => <span className="control-data-chip" key={item}>{item}</span>)}</div>
        <div className="control-detail-meta"><span>ROLE TYPE</span><strong>{selected.stage}</strong><small>Actual execution and task routing remain managed by the existing Python backend.</small></div>
      </aside>
    </div>
    <section className="control-lifecycle">
      <div><span className="lifecycle-icon"><ListChecks size={17}/></span><div><strong>Conceptual work cycle</strong><p>Request → Plan → Delegate → Check → Review → Result. This is an explanatory map, not a live run or an executable workflow.</p></div></div>
      <span className="lifecycle-note"><Clock3 size={13}/> Live run history comes later</span>
    </section>
    <footer className="page-foot"><span>DuoAI Studio · Master Control Room preview</span><span>Static sample topology · No backend actions exposed</span></footer>
  </div>;
}

const workspaceProjects = [
  { id: "desktop", name: "Desktop experience refresh", initials: "DE", language: "React · TypeScript", branch: "feature/workspace-ui", progress: 68, tasks: "5 of 8 tasks", color: "blue" },
  { id: "api", name: "API integration", initials: "AI", language: "Python · FastAPI", branch: "feature/provider-api", progress: 42, tasks: "3 of 7 tasks", color: "green" },
  { id: "website", name: "Website refresh", initials: "WR", language: "React · Vite", branch: "main", progress: 84, tasks: "8 of 10 tasks", color: "amber" }
];
const workspaceFiles = [
  { id: "app", name: "App.tsx", path: "src / App.tsx", kind: "code", language: "tsx", content: 'import { useState } from "react";\n\nexport function WorkspaceHome() {\n  const [activeTab, setActiveTab] = useState("overview");\n\n  return (\n    <main className="workspace-home">\n      <h1>Project workspace</h1>\n      <p>Keep your work organised.</p>\n    </main>\n  );\n}' },
  { id: "agents", name: "agents.py", path: "backend / agents.py", kind: "code", language: "python", content: 'class AgentRegistry:\n    """Keeps the available worker roles."""\n\n    def __init__(self):\n        self.roles = [\n            "coding",\n            "testing",\n            "review",\n            "research",\n        ]\n\n    def list_roles(self):\n        return self.roles' },
  { id: "readme", name: "README.md", path: "docs / README.md", kind: "text", language: "markdown", content: '# Desktop experience refresh\n\nA focused workspace for planning, implementing, and reviewing project changes.\n\n## Current focus\n\n- Organise project files\n- Track implementation tasks\n- Keep proposed changes reviewable\n\n> Preview content only. No repository files are being edited here.' },
  { id: "config", name: "package.json", path: "root / package.json", kind: "text", language: "json", content: '{\n  "name": "desktop-experience",\n  "private": true,\n  "scripts": {\n    "dev": "vite",\n    "build": "tsc --noEmit && vite build"\n  }\n}' }
];
const workspaceTasks = [
  { id: "task-1", title: "Set up the workspace shell", detail: "Create the main project layout and navigation.", status: "Done", agent: "Coding" },
  { id: "task-2", title: "Add project file explorer", detail: "Show a simple, searchable project structure.", status: "Done", agent: "Coding" },
  { id: "task-3", title: "Build task overview", detail: "Group work by status and show progress.", status: "In progress", agent: "Orchestrator" },
  { id: "task-4", title: "Review responsive layout", detail: "Check narrow screens and dark theme.", status: "To do", agent: "Review" }
];
function WorkspaceScreen({ query }: { query: string }) {
  const [projectId, setProjectId] = useState("desktop");
  const [fileId, setFileId] = useState("app");
  const [taskFilter, setTaskFilter] = useState("All");
  const project = workspaceProjects.find(item => item.id === projectId) ?? workspaceProjects[0];
  const file = workspaceFiles.find(item => item.id === fileId) ?? workspaceFiles[0];
  const filteredFiles = workspaceFiles.filter(item => [item.name, item.path, item.language].join(" ").toLowerCase().includes(query.toLowerCase()));
  const filteredTasks = workspaceTasks.filter(item => (taskFilter === "All" || item.status === taskFilter) && [item.title, item.detail, item.agent, item.status].join(" ").toLowerCase().includes(query.toLowerCase()));
  const doneCount = workspaceTasks.filter(item => item.status === "Done").length;
  return <div className="content workspace-content">
    <section className="welcome workspace-welcome"><div><label>— PROJECT WORKSPACE</label><h1>Make space for good work.</h1><p>Your project files, tasks and agent hand-offs in one organised view.</p></div><span className="preview">● UI PREVIEW · SAMPLE PROJECT</span></section>
    <section className="workspace-project-strip">
      <div className="workspace-project-picker"><span className={"workspace-project-mark " + project.color}>{project.initials}</span><div><small>ACTIVE PROJECT</small><strong>{project.name}</strong><em>{project.language}</em></div><ChevronDown size={15}/></div>
      <div className="workspace-project-meta"><span><GitBranch size={14}/>{project.branch}</span><span><CircleDot size={13}/>{project.tasks}</span></div>
      <div className="workspace-progress"><div><span>Project progress</span><b>{project.progress}%</b></div><i><span style={{width: project.progress + "%"}}/></i></div>
    </section>
    <div className="workspace-project-tabs" role="group" aria-label="Choose sample project">
      {workspaceProjects.map(item => <button key={item.id} className={projectId === item.id ? "active" : ""} onClick={() => { setProjectId(item.id); setFileId("app"); }}>{item.name}</button>)}
    </div>
    <div className="workspace-main-grid">
      <section className="workspace-files-panel">
        <div className="workspace-panel-heading"><div><label>PROJECT EXPLORER</label><h2>Files <span>{filteredFiles.length}</span></h2></div><button className="workspace-quiet-action" aria-label="Add file (preview only)" title="Preview only"><Plus size={16}/></button></div>
        <div className="workspace-root"><Folder size={15}/><strong>{project.id === "desktop" ? "desktop-experience" : project.id === "api" ? "api-integration" : "website-refresh"}</strong><ChevronDown size={14}/></div>
        <div className="workspace-file-list">
          {filteredFiles.map(item => <button key={item.id} className={fileId === item.id ? "workspace-file active" : "workspace-file"} onClick={() => setFileId(item.id)}><span className="workspace-file-icon">{item.kind === "code" ? <FileCode2 size={15}/> : <FileText size={15}/>}</span><span><strong>{item.name}</strong><small>{item.path}</small></span><ChevronRight size={14}/></button>)}
          {!filteredFiles.length && <p className="workspace-no-results">No files match this search.</p>}
        </div>
        <div className="workspace-explorer-foot"><span>4 sample files</span><span>Read-only preview</span></div>
      </section>
      <section className="workspace-editor-panel">
        <div className="workspace-editor-top"><div className="workspace-editor-tabs"><span className="workspace-editor-tab"><FileCode2 size={14}/>{file.name}<i/></span></div><span className="workspace-readonly"><CircleCheck size={13}/> Preview file</span></div>
        <div className="workspace-file-path">{project.name} <ChevronRight size={12}/> {file.path}</div>
        <div className="workspace-code-area"><div className="workspace-line-numbers">{file.content.split("\n").map((_,index)=><span key={index}>{index+1}</span>)}</div><pre><code>{file.content}</code></pre></div>
        <div className="workspace-editor-foot"><span>{file.language.toUpperCase()}</span><span>Sample content · Not connected to disk</span></div>
      </section>
    </div>
    <section className="workspace-tasks-panel">
      <div className="workspace-panel-heading"><div><label>EXECUTION PLAN</label><h2>Task board <span>{doneCount}/{workspaceTasks.length} complete</span></h2></div><div className="workspace-task-filters">{["All","To do","In progress","Done"].map(item=><button key={item} className={taskFilter === item ? "active" : ""} onClick={()=>setTaskFilter(item)}>{item}</button>)}</div></div>
      <div className="workspace-task-list">{filteredTasks.map(task=><article className="workspace-task" key={task.id}><span className={"workspace-task-status " + task.status.toLowerCase().replace(" ","-")}>{task.status === "Done" ? <CircleCheck size={16}/> : task.status === "In progress" ? <Play size={14}/> : <CircleDashed size={16}/>}</span><div className="workspace-task-copy"><strong>{task.title}</strong><small>{task.detail}</small></div><span className="workspace-task-agent"><Bot size={13}/>{task.agent}</span><span className={"workspace-task-pill " + task.status.toLowerCase().replace(" ","-")}>{task.status}</span></article>)}{!filteredTasks.length && <p className="workspace-no-results">No tasks match this filter or search.</p>}</div>
    </section>
    <section className="workspace-terminal-note"><span><Terminal size={16}/></span><div><strong>Execution panel comes next</strong><p>Terminal output, run controls, and real agent task updates will be connected only when the Electron-to-Python bridge is ready.</p></div><span className="workspace-bridge-tag">BACKEND BRIDGE PENDING</span></section>
    <footer className="page-foot"><span>DuoAI Studio · Workspace UI preview</span><span>Sample files and tasks · No disk or backend actions</span></footer>
  </div>;
}


const reviewItems = [
  { id:"desktop-ui", title:"Polish responsive workspace layout", project:"Desktop experience refresh", author:"Coding Agent", branch:"feature/workspace-ui", status:"Needs review", files:3, additions:46, deletions:12, summary:"Tightens the project explorer and editor layout across smaller window sizes.", findings:[{level:"Note",title:"Responsive breakpoint added",detail:"The file explorer switches to a stacked layout on narrower windows."},{level:"Check",title:"Reduced-motion support",detail:"Interactive transitions respect the operating system motion preference."}], diff:[{file:"src/components/Workspace.tsx",change:"@@ layout\n- grid-template-columns: 260px 1fr;\n+ grid-template-columns: minmax(220px, .72fr) minmax(0, 1.6fr);\n\n+ // Keep the editor readable on narrow windows\n+ @media (max-width: 850px) {\n+   .workspace-main-grid { grid-template-columns: 1fr; }\n+ }"}]},
  { id:"provider-config", title:"Add provider configuration validation", project:"API integration", author:"Coding Agent", branch:"feature/provider-validation", status:"Needs review", files:2, additions:31, deletions:4, summary:"Adds clearer validation messages for incomplete provider settings.", findings:[{level:"Warning",title:"Credential handling needs confirmation",detail:"Confirm secrets are never written to logs or returned in validation messages."},{level:"Note",title:"Input validation added",detail:"Required fields are checked before the provider configuration is accepted."}], diff:[{file:"backend/providers/config.py",change:"@@ validation\n+ def validate_provider(config):\n+     required = (\"provider\", \"model\")\n+     missing = [key for key in required if not config.get(key)]\n+     if missing:\n+         raise ValueError(\"Missing provider settings\")"}]},
  { id:"docs-refresh", title:"Update project setup guide", project:"Website refresh", author:"Research Agent", branch:"docs/setup-guide", status:"Approved", files:1, additions:18, deletions:3, summary:"Clarifies the local setup steps and documents the current development workflow.", findings:[{level:"Note",title:"Documentation-only change",detail:"No application runtime code is changed in this proposal."}], diff:[{file:"README.md",change:"@@ local setup\n+ ## Local development\n+ Install dependencies, then run the desktop UI from its own folder.\n+ The Python backend remains a separate process during this preview phase."}]}
];
function ReviewCenter({ query }: { query: string }) {
  const [items,setItems] = useState(reviewItems);
  const [selectedId,setSelectedId] = useState("desktop-ui");
  const [filter,setFilter] = useState("All");
  const [tab,setTab] = useState("Overview");
  const visible = items.filter(item => (filter === "All" || item.status === filter) && [item.title,item.project,item.author,item.branch,item.summary].join(" ").toLowerCase().includes(query.toLowerCase()));
  const selected = visible.find(item=>item.id===selectedId) ?? visible[0];
  const decide = (status:"Approved" | "Changes requested") => { if(!selected) return; setItems(current=>current.map(item=>item.id===selected.id?{...item,status}:item)); };
  return <div className="content review-content">
    <section className="welcome review-welcome"><div><label>— QUALITY GATE</label><h1>Review before it ships.</h1><p>Inspect proposed changes, understand findings and record a review decision.</p></div><span className="preview">● UI PREVIEW · SAMPLE PROPOSALS</span></section>
    <section className="review-summary">
      <article><span className="review-summary-icon pending"><GitPullRequest size={17}/></span><div><strong>{items.filter(x=>x.status==="Needs review").length.toString().padStart(2,"0")}</strong><small>Awaiting review</small></div></article>
      <article><span className="review-summary-icon approved"><Check size={17}/></span><div><strong>{items.filter(x=>x.status==="Approved").length.toString().padStart(2,"0")}</strong><small>Approved previews</small></div></article>
      <article><span className="review-summary-icon findings"><AlertTriangle size={17}/></span><div><strong>{items.reduce((n,x)=>n+x.findings.filter(f=>f.level==="Warning").length,0).toString().padStart(2,"0")}</strong><small>Warnings to inspect</small></div></article>
      <span className="review-summary-note"><CircleDot size={13}/> Decisions are local preview state</span>
    </section>
    <div className="review-filter-row">{["All","Needs review","Approved","Changes requested"].map(item=><button key={item} className={filter===item?"active":""} onClick={()=>setFilter(item)}>{item}<span>{item==="All"?items.length:items.filter(x=>x.status===item).length}</span></button>)}</div>
    <div className="review-layout">
      <section className="review-queue">
        <div className="review-section-head"><div><label>PROPOSAL QUEUE</label><h2>Change requests <span>{visible.length}</span></h2></div><span className="review-queue-hint">Select a proposal</span></div>
        {visible.map(item=><button key={item.id} className={selected?.id===item.id?"review-proposal selected":"review-proposal"} onClick={()=>{setSelectedId(item.id);setTab("Overview");}}>
          <span className="review-proposal-icon"><FileDiff size={17}/></span><span className="review-proposal-copy"><strong>{item.title}</strong><small>{item.project}</small><em><Bot size={12}/>{item.author} · {item.files} files</em></span><span className={"review-status "+item.status.toLowerCase().replaceAll(" ","-")}>{item.status}</span>
        </button>)}
        {!visible.length&&<p className="review-empty">No proposals match this filter or search.</p>}
        <div className="review-queue-foot"><span>Sample proposals only</span><span>Not linked to Git</span></div>
      </section>
      {selected ? <section className="review-detail">
        <div className="review-detail-top"><div><span className="review-project-label">{selected.project}</span><h2>{selected.title}</h2><p><GitBranch size={13}/>{selected.branch}<span>·</span><Bot size={13}/>{selected.author}</p></div><span className={"review-status large "+selected.status.toLowerCase().replaceAll(" ","-")}>{selected.status}</span></div>
        <div className="review-change-stats"><span><FileDiff size={14}/>{selected.files} files changed</span><span className="review-add">+{selected.additions}</span><span className="review-remove">−{selected.deletions}</span><span><GitCommit size={14}/> Sample change set</span></div>
        <div className="review-tabs">{["Overview","Diff","Findings"].map(item=><button key={item} className={tab===item?"active":""} onClick={()=>setTab(item)}>{item}{item==="Findings"&&<span>{selected.findings.length}</span>}</button>)}</div>
        {tab==="Overview"&&<div className="review-overview"><h3>Proposal summary</h3><p>{selected.summary}</p><div className="review-overview-note"><MessageSquare size={15}/><span>This proposal is illustrative sample content. No repository files have been changed by this screen.</span></div><h3>Change summary</h3><div className="review-change-row"><FileDiff size={15}/><span>{selected.files} files included in this proposal</span><b>View diff →</b></div></div>}
        {tab==="Diff"&&<div className="review-diff-list">{selected.diff.map((entry,index)=><div className="review-diff-file" key={index}><div><FileCode2 size={14}/><strong>{entry.file}</strong><span>Sample diff</span></div><pre>{entry.change}</pre></div>)}</div>}
        {tab==="Findings"&&<div className="review-findings">{selected.findings.map((finding,index)=><article className={"review-finding "+finding.level.toLowerCase()} key={index}><span>{finding.level==="Warning"?<AlertTriangle size={16}/>:<CircleCheck size={16}/>}</span><div><strong>{finding.title}</strong><p>{finding.detail}</p></div></article>)}</div>}
        <div className="review-decision-bar"><div><strong>Review decision</strong><small>Changes here affect this preview only.</small></div><div><button className="review-request" onClick={()=>decide("Changes requested")}><MessageSquare size={14}/> Request changes</button><button className="review-approve" onClick={()=>decide("Approved")}><Check size={14}/> Approve preview</button></div></div>
      </section> : <section className="review-detail review-no-selection"><GitPullRequest size={26}/><strong>Select a proposal to inspect it</strong><span>Choose an item from the queue.</span></section>}
    </div>
    <section className="review-safety-note"><span><ShieldCheck size={17}/></span><div><strong>Human review stays in control.</strong><p>Real approval will require backend integration, permission checks and a verified change set. These preview buttons do not merge, commit, or modify repository files.</p></div><span className="review-bridge">BACKEND CONNECTION PENDING</span></section>
    <footer className="page-foot"><span>DuoAI Studio · Review Center UI preview</span><span>Sample proposals and local decisions · No Git actions</span></footer>
  </div>;
}


const projectDirectory = [
  { id:"desktop", name:"Desktop experience refresh", initials:"DE", description:"A polished desktop workspace for planning, coding, testing and reviewing work.", stack:"Electron · React · TypeScript", branch:"main", status:"In progress", progress:68, tasks:"5 / 8 tasks", updated:"Updated recently", color:"blue", lead:"Coding Agent", next:"Finish the responsive workspace layout", tags:["Desktop UI","Electron","Frontend"] },
  { id:"api", name:"API integration", initials:"AI", description:"A gradual integration layer connecting the desktop interface to the existing Python services.", stack:"Python · FastAPI", branch:"feature/provider-api", status:"In progress", progress:42, tasks:"3 / 7 tasks", updated:"Updated today", color:"green", lead:"Master Orchestrator", next:"Document the local bridge contract", tags:["Backend","Integration","Python"] },
  { id:"website", name:"Website refresh", initials:"WR", description:"A refreshed public website with clear product information and a focused application flow.", stack:"React · Vite", branch:"main", status:"In review", progress:84, tasks:"8 / 10 tasks", updated:"Awaiting review", color:"amber", lead:"Review Agent", next:"Resolve the remaining review notes", tags:["Website","Frontend","Review"] },
  { id:"research", name:"Provider comparison", initials:"PC", description:"Research notes comparing model providers, capabilities and practical trade-offs.", stack:"Research · Documentation", branch:"docs/provider-notes", status:"Completed", progress:100, tasks:"6 / 6 tasks", updated:"Completed this week", color:"violet", lead:"Research Agent", next:"Keep the decision record up to date", tags:["Research","Planning","Docs"] }
];
function ProjectsScreen({ query, onOpenWorkspace }: { query:string; onOpenWorkspace:()=>void }) {
  const [filter,setFilter]=useState("All projects");
  const [selectedId,setSelectedId]=useState("desktop");
  const filters=["All projects","In progress","In review","Completed"];
  const visible=projectDirectory.filter(project=>(filter==="All projects"||project.status===filter)&&[project.name,project.description,project.stack,project.branch,...project.tags].join(" ").toLowerCase().includes(query.toLowerCase()));
  const selected=visible.find(project=>project.id===selectedId)??visible[0];
  return <div className="content projects-content">
    <section className="welcome projects-welcome"><div><label>— YOUR WORK</label><h1>Every project, in one place.</h1><p>Keep an eye on progress, ownership and the next step across your workspace.</p></div><span className="preview">● UI PREVIEW · SAMPLE PROJECTS</span></section>
    <section className="projects-summary">
      <article><span className="projects-summary-icon"><FolderKanban size={17}/></span><div><strong>04</strong><small>Total projects</small></div></article>
      <article><span className="projects-summary-icon"><Activity size={17}/></span><div><strong>02</strong><small>In progress</small></div></article>
      <article><span className="projects-summary-icon"><GitPullRequest size={17}/></span><div><strong>01</strong><small>In review</small></div></article>
      <article><span className="projects-summary-icon"><Check size={17}/></span><div><strong>01</strong><small>Completed</small></div></article>
      <div className="projects-connection"><CircleDot size={14}/><span>Sample data · backend not connected</span></div>
    </section>
    <div className="projects-toolbar"><div className="projects-filters" role="group" aria-label="Filter projects">{filters.map(item=><button key={item} className={filter===item?"active":""} onClick={()=>setFilter(item)}>{item}</button>)}</div><span>{visible.length} {visible.length===1?"project":"projects"}</span></div>
    <div className="projects-layout">
      <section className="projects-grid" aria-label="Project directory">
        {visible.map(project=><button key={project.id} className={selected?.id===project.id?"project-card selected":"project-card"} onClick={()=>setSelectedId(project.id)} aria-pressed={selected?.id===project.id}>
          <div className="project-card-top"><span className={"project-card-mark "+project.color}>{project.initials}</span><span className={"project-status "+project.status.toLowerCase().replaceAll(" ","-")}>{project.status}</span></div>
          <strong>{project.name}</strong><p>{project.description}</p>
          <div className="project-card-stack">{project.stack}</div>
          <div className="project-card-progress"><span>Progress</span><b>{project.progress}%</b></div><div className="project-card-track"><i style={{width:project.progress+"%"}}/></div>
          <div className="project-card-foot"><span><Check size={12}/>{project.tasks}</span><span>{project.updated}</span></div>
        </button>)}
        {!visible.length&&<div className="projects-empty">No projects match this search or filter.</div>}
      </section>
      {selected?<aside className="project-inspector">
        <div className="project-inspector-head"><span>PROJECT OVERVIEW</span><span>PREVIEW</span></div>
        <span className={"project-inspector-mark "+selected.color}>{selected.initials}</span>
        <h2>{selected.name}</h2><p>{selected.description}</p>
        <div className="project-inspector-status"><span className={"project-status "+selected.status.toLowerCase().replaceAll(" ","-")}>{selected.status}</span><small>{selected.updated}</small></div>
        <div className="project-inspector-progress"><div><span>Overall progress</span><b>{selected.progress}%</b></div><i><span style={{width:selected.progress+"%"}}/></i></div>
        <div className="project-inspector-section"><label>TECH STACK</label><strong>{selected.stack}</strong></div>
        <div className="project-inspector-section"><label>ACTIVE BRANCH</label><strong><GitBranch size={13}/>{selected.branch}</strong></div>
        <div className="project-inspector-section"><label>COORDINATION</label><strong><Bot size={13}/>{selected.lead}</strong></div>
        <div className="project-next-step"><label>NEXT STEP</label><p>{selected.next}</p></div>
        <div className="project-inspector-tags">{selected.tags.map(tag=><span key={tag}>{tag}</span>)}</div>
        <button className="project-open-workspace" onClick={onOpenWorkspace}>Open workspace <ArrowUpRight size={15}/></button>
        <small className="project-inspector-note">Preview navigation only · no files or repository data are accessed.</small>
      </aside>:<aside className="project-inspector project-inspector-empty">Select a project to see its overview.</aside>}
    </div>
    <footer className="page-foot"><span>DuoAI Studio · Projects UI preview</span><span>Sample project data · No repository actions exposed</span></footer>
  </div>;
}


function SettingsScreen({ query, theme, onThemeChange, lowEffects, onLowEffectsChange }: { query:string; theme:"light"|"dark"; onThemeChange:(value:"light"|"dark")=>void; lowEffects:boolean; onLowEffectsChange:(value:boolean)=>void }) {
  const [section,setSection]=useState("Appearance");
  const [notifications,setNotifications]=useState({reviews:true,agentUpdates:true,projectActivity:false,weeklySummary:true});
  const [privacy,setPrivacy]=useState({localHistory:true,diagnostics:false});
  const sections=[{name:"Profile",icon:Users,description:"Your workspace identity"},{name:"Appearance",icon:Sparkles,description:"Theme and motion"},{name:"Notifications",icon:Bell,description:"Choose what appears"},{name:"Privacy & security",icon:ShieldCheck,description:"Local data and diagnostics"},{name:"Workspace",icon:FolderKanban,description:"Workspace preferences"}];
  const visibleSections=sections.filter(item=>(item.name+" "+item.description).toLowerCase().includes(query.toLowerCase()));
  const toggle=(group:"notifications"|"privacy",key:string,value:boolean)=> {
    if(group==="notifications") setNotifications(old=>({...old,[key]:value}));
    else setPrivacy(old=>({...old,[key]:value}));
  };
  const Switch=({checked,onChange,label}:{checked:boolean;onChange:(value:boolean)=>void;label:string})=><button className={"settings-switch "+(checked?"enabled":"")} role="switch" aria-checked={checked} aria-label={label} onClick={()=>onChange(!checked)}><i/></button>;
  const Row=({title,description,checked,onChange}:{title:string;description:string;checked:boolean;onChange:(value:boolean)=>void})=><div className="settings-row"><div><strong>{title}</strong><p>{description}</p></div><Switch checked={checked} onChange={onChange} label={title}/></div>;
  return <div className="content settings-content">
    <section className="welcome settings-welcome"><div><label>— PREFERENCES</label><h1>Make Duo feel like yours.</h1><p>Manage the desktop preview’s appearance and workspace preferences.</p></div><span className="preview">● UI PREVIEW · LOCAL SETTINGS</span></section>
    <div className="settings-layout">
      <aside className="settings-nav"><div className="settings-nav-title">SETTINGS</div>{visibleSections.map(item=><button key={item.name} className={section===item.name?"selected":""} onClick={()=>setSection(item.name)}><item.icon size={16}/><span><b>{item.name}</b><small>{item.description}</small></span><ChevronRight size={14}/></button>)}</aside>
      <section className="settings-panel">
        {section==="Profile"&&<><div className="settings-panel-head"><div><label>YOUR PROFILE</label><h2>Personal workspace</h2><p>Basic identity shown in this local preview.</p></div><span className="settings-preview-tag">PREVIEW</span></div><div className="settings-profile"><span>S</span><div><strong>Studio owner</strong><small>Local preview account</small></div></div><div className="settings-info"><label>DISPLAY NAME</label><strong>Studio owner</strong><small>Profile editing and account sync are not connected yet.</small></div><div className="settings-info"><label>WORKSPACE</label><strong>Personal workspace</strong><small>Free workspace · sample information</small></div></>}
        {section==="Appearance"&&<><div className="settings-panel-head"><div><label>DISPLAY</label><h2>Appearance</h2><p>Choose a comfortable look for your workspace.</p></div><span className="settings-preview-tag">ACTIVE PREVIEW</span></div><div className="settings-group"><h3>Theme</h3><p>Switch between light and dark appearance.</p><div className="theme-choices"><button className={theme==="light"?"chosen":""} onClick={()=>onThemeChange("light")}><span className="theme-swatch light-swatch"><i/><i/><i/></span><b>Light</b>{theme==="light"&&<Check size={14}/>}</button><button className={theme==="dark"?"chosen":""} onClick={()=>onThemeChange("dark")}><span className="theme-swatch dark-swatch"><i/><i/><i/></span><b>Dark</b>{theme==="dark"&&<Check size={14}/>}</button></div></div><div className="settings-group"><h3>Motion and effects</h3><p>Reduce decorative movement and transitions.</p><Row title="Low effects mode" description="Use calmer transitions and reduce visual effects." checked={lowEffects} onChange={onLowEffectsChange}/><div className="settings-note">The operating system’s reduced-motion preference is also respected where supported.</div></div></>}
        {section==="Notifications"&&<><div className="settings-panel-head"><div><label>UPDATES</label><h2>Notifications</h2><p>Choose which preview notifications you would like to see.</p></div><span className="settings-preview-tag">LOCAL ONLY</span></div><div className="settings-group"><h3>Activity notifications</h3><Row title="Review requests" description="When a proposal is ready for your review." checked={notifications.reviews} onChange={v=>toggle("notifications","reviews",v)}/><Row title="Agent updates" description="When an agent reports a task update." checked={notifications.agentUpdates} onChange={v=>toggle("notifications","agentUpdates",v)}/><Row title="Project activity" description="General progress and project updates." checked={notifications.projectActivity} onChange={v=>toggle("notifications","projectActivity",v)}/><Row title="Weekly summary" description="A compact overview of workspace activity." checked={notifications.weeklySummary} onChange={v=>toggle("notifications","weeklySummary",v)}/></div><div className="settings-note">These switches currently change this screen only. System notifications are not connected.</div></>}
        {section==="Privacy & security"&&<><div className="settings-panel-head"><div><label>DATA CONTROLS</label><h2>Privacy & security</h2><p>Review the privacy-related options planned for the desktop app.</p></div><span className="settings-preview-tag">PREVIEW</span></div><div className="settings-group"><h3>Local data preferences</h3><Row title="Keep local activity history" description="Preference preview for keeping recent activity on this device." checked={privacy.localHistory} onChange={v=>toggle("privacy","localHistory",v)}/><Row title="Share anonymous diagnostics" description="Preference preview only; no diagnostic data is sent." checked={privacy.diagnostics} onChange={v=>toggle("privacy","diagnostics",v)}/></div><div className="settings-security-card"><ShieldCheck size={18}/><div><strong>Credential protection</strong><p>Provider credentials remain managed by the existing Python backend. This UI preview does not read, display, or change secrets.</p><small>Backend connection pending</small></div></div></>}
        {section==="Workspace"&&<><div className="settings-panel-head"><div><label>WORKSPACE</label><h2>Workspace preferences</h2><p>Information about this local preview environment.</p></div><span className="settings-preview-tag">READ ONLY</span></div><div className="settings-info"><label>WORKSPACE NAME</label><strong>Personal workspace</strong></div><div className="settings-info"><label>DESKTOP SHELL</label><strong>Electron + React</strong></div><div className="settings-info"><label>EXISTING BACKEND</label><strong>Python · connection pending</strong></div><div className="settings-note">The gradual backend migration is not part of this UI-only step. Existing Python functionality is unchanged.</div></>}
      </section>
    </div>
    <footer className="page-foot"><span>DuoAI Studio · Settings UI preview</span><span>Preferences are local to this screen · no backend writes</span></footer>
  </div>;
}

export default function App() {
  const [query, setQuery] = useState("");
  const [low, setLow] = useState(false);
  const [page, setPage] = useState<"Home" | "Projects" | "Agents" | "Master Control Room" | "Workspace" | "Review Center" | "Settings">("Home");
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    const saved = localStorage.getItem("duoai-theme");
    return saved === "dark" ? "dark" : "light";
  });
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("duoai-theme", theme);
  }, [theme]);
  const visible = updates.filter((row) => row.join(" ").toLowerCase().includes(query.toLowerCase()));
  return <div className={low ? "shell low" : "shell"}>
    <aside className="sidebar">
      <div className="brand"><img src="./duo-mark.svg" alt=""/><b>DuoAI <small>STUDIO</small></b></div>
      <div className="workspace"><span>D</span><div><b>Personal workspace</b><small>Free workspace</small></div><ChevronDown size={14}/></div>
      <nav>
        <label>OVERVIEW</label><Nav icon={LayoutDashboard} label="Home" active={page === "Home"} onClick={() => { setPage("Home"); setQuery(""); }}/><Nav icon={FolderKanban} label="Projects" active={page === "Projects"} onClick={() => { setPage("Projects"); setQuery(""); }}/>
        <label>TEAM</label><Nav icon={Users} label="Agents" active={page === "Agents"} onClick={() => { setPage("Agents"); setQuery(""); }}/><Nav icon={Workflow} label="Master Control Room" active={page === "Master Control Room"} onClick={() => { setPage("Master Control Room"); setQuery(""); }}/>
        <label>WORK</label><Nav icon={BookOpen} label="Workspace" active={page === "Workspace"} onClick={() => { setPage("Workspace"); setQuery(""); }}/><Nav icon={GitPullRequest} label="Review Center" active={page === "Review Center"} onClick={() => { setPage("Review Center"); setQuery(""); }}/>
        <label>ACCOUNT</label><Nav icon={Settings2} label="Settings" active={page === "Settings"} onClick={() => { setPage("Settings"); setQuery(""); }}/>
      </nav>
      <div className="side-bottom"><div className="profile"><span>S</span><div><b>Studio owner</b><small>Local preview</small></div></div></div>
    </aside>
    <main>
      <header className="topbar"><div className="crumb">Overview <i>/</i> <b>{page}</b></div><div className="top-actions"><span className="bridge"><i/>Backend bridge pending</span><div className="search"><Search size={15}/><input placeholder={page === "Settings" ? "Search settings..." : page === "Projects" ? "Search projects..." : page === "Agents" ? "Search agent profiles..." : page === "Master Control Room" ? "Search workflow roles..." : page === "Workspace" ? "Search files and tasks..." : page === "Review Center" ? "Search proposals..." : "Search activity..."} value={query} onChange={e=>setQuery(e.target.value)}/></div><button className="icon-btn" aria-label="Notifications"><Bell size={17}/></button><button className="icon-btn theme-toggle" aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"} title={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"} onClick={()=>setTheme(current=>current === "dark" ? "light" : "dark")}>{theme === "dark" ? <Sun size={17}/> : <Moon size={17}/>}</button><span className="topbar-mark" aria-label="Duo Studio">D</span></div></header>
      {page === "Settings" ? <SettingsScreen query={query} theme={theme} onThemeChange={setTheme} lowEffects={low} onLowEffectsChange={setLow}/> : page === "Projects" ? <ProjectsScreen query={query} onOpenWorkspace={() => { setPage("Workspace"); setQuery(""); }}/> : page === "Agents" ? <AgentsScreen query={query}/> : page === "Master Control Room" ? <MasterControlRoom query={query}/> : page === "Workspace" ? <WorkspaceScreen query={query}/> : page === "Review Center" ? <ReviewCenter query={query}/> : <div className="content editorial-dashboard">
          <section className="dashboard-heading">
            <div>
              <span className="eyebrow"><i/> DUO STUDIO / WORKSPACE OVERVIEW</span>
              <h1>A clearer view of<br/><em>what’s moving.</em></h1>
              <p>Projects, agent roles and review work — brought together in one considered workspace.</p>
            </div>
            <div className="dashboard-heading-side"><span className="sample-pill">SAMPLE WORKSPACE DATA</span><small>Preview environment<br/>Python bridge not connected</small></div>
          </section>

          <section className="dashboard-kpis" aria-label="Workspace metrics">
            <article className="kpi-card"><span>PROJECTS</span><strong>04</strong><small><i className="kpi-dot sage"/> 3 shown below</small><span className="kpi-index">01</span></article>
            <article className="kpi-card"><span>OPEN TASKS</span><strong>12</strong><small><i className="kpi-dot blue"/> Across 4 projects</small><span className="kpi-index">02</span></article>
            <article className="kpi-card"><span>IN REVIEW</span><strong>03</strong><small><i className="kpi-dot amber"/> Awaiting attention</small><span className="kpi-index">03</span></article>
            <article className="kpi-card kpi-progress"><span>COMPLETION</span><strong>78<small>%</small></strong><div className="kpi-track"><i/></div><small>Illustrative project average</small><span className="kpi-index">04</span></article>
          </section>

          <section className="dashboard-main-grid">
            <article className="editorial-panel project-board">
              <header className="editorial-panel-head"><div><span className="section-kicker">01 — CURRENT WORK</span><h2>Projects in motion</h2><p>A snapshot of the work currently represented in this preview.</p></div><button onClick={()=>setPage("Projects")}>Browse projects <ArrowUpRight size={15}/></button></header>
              <div className="project-board-list">
                <button className="project-board-row" onClick={()=>setPage("Workspace")}><span className="project-monogram monogram-sage">DE</span><span className="project-board-copy"><b>Desktop experience refresh</b><small>React · TypeScript <i/> 5 of 8 tasks</small><span className="project-board-track"><i style={{width:"68%"}}/></span></span><span className="project-board-value">68%</span><ArrowUpRight size={15}/></button>
                <button className="project-board-row" onClick={()=>setPage("Projects")}><span className="project-monogram monogram-clay">AI</span><span className="project-board-copy"><b>API integration</b><small>Python · FastAPI <i/> 3 of 7 tasks</small><span className="project-board-track"><i style={{width:"42%"}}/></span></span><span className="project-board-value">42%</span><ArrowUpRight size={15}/></button>
                <button className="project-board-row" onClick={()=>setPage("Projects")}><span className="project-monogram monogram-blue">WR</span><span className="project-board-copy"><b>Website refresh</b><small>React · Vite <i/> 8 of 10 tasks</small><span className="project-board-track"><i style={{width:"84%"}}/></span></span><span className="project-board-value">84%</span><ArrowUpRight size={15}/></button>
              </div>
              <footer className="editorial-panel-foot"><span><i className="kpi-dot sage"/> Example project records</span><span>Open a row to explore the UI preview</span></footer>
            </article>

            <article className="editorial-panel throughput-panel">
              <header className="editorial-panel-head"><div><span className="section-kicker">02 — DELIVERY RHYTHM</span><h2>Task throughput</h2><p>Illustrative completed tasks by day.</p></div><span className="chart-period">7 DAYS</span></header>
              <div className="throughput-summary"><strong>24</strong><span>sample completions<br/><b>+18% vs. prior period</b></span></div>
              <div className="throughput-chart" role="img" aria-label="Illustrative task throughput line chart over seven days">
                <div className="chart-y-labels"><span>12</span><span>8</span><span>4</span><span>0</span></div>
                <svg viewBox="0 0 440 156" preserveAspectRatio="none" aria-hidden="true">
                  <defs><linearGradient id="throughputFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stopColor="#8b9d82" stopOpacity=".25"/><stop offset="100%" stopColor="#8b9d82" stopOpacity="0"/></linearGradient></defs>
                  <path className="chart-gridline" d="M0 18H440 M0 57H440 M0 96H440 M0 135H440"/>
                  <path className="chart-area" d="M0 112 C24 103 35 83 73 91 S125 104 146 76 S199 83 220 61 S272 72 293 51 S345 60 366 34 S414 42 440 18 L440 135 L0 135Z"/>
                  <path className="chart-line" d="M0 112 C24 103 35 83 73 91 S125 104 146 76 S199 83 220 61 S272 72 293 51 S345 60 366 34 S414 42 440 18"/>
                  <circle className="chart-point" cx="440" cy="18" r="4"/>
                </svg>
                <div className="chart-x-labels"><span>MON</span><span>TUE</span><span>WED</span><span>THU</span><span>FRI</span><span>SAT</span><span>SUN</span></div>
              </div>
              <div className="chart-legend"><span><i/> Completed tasks</span><small>Illustrative series · not live telemetry</small></div>
            </article>
          </section>

          <section className="dashboard-lower-grid">
            <article className="editorial-panel topology-panel">
              <header className="editorial-panel-head"><div><span className="section-kicker">03 — SYSTEM MAP</span><h2>Coordination topology</h2><p>How a request is intended to move through specialist roles.</p></div><button onClick={()=>setPage("Master Control Room")}>Inspect workflow <ArrowUpRight size={15}/></button></header>
              <div className="topology-canvas" role="img" aria-label="Conceptual task routing from the master orchestrator to coding, testing, review and research roles">
                <svg className="topology-lines" viewBox="0 0 600 230" preserveAspectRatio="none" aria-hidden="true"><path d="M300 72 V104 M300 104 H82 V137 M300 104 H218 V137 M300 104 H382 V137 M300 104 H518 V137"/></svg>
                <div className="topology-master"><span className="topology-node-mark">M</span><span><b>Master Orchestrator</b><small>Plan · Prioritise · Delegate</small></span><em>COORDINATOR</em></div>
                <div className="topology-workers">
                  <div className="topology-worker"><span className="worker-symbol sage-symbol">01</span><b>Coding</b><small>Implementation</small></div>
                  <div className="topology-worker"><span className="worker-symbol blue-symbol">02</span><b>Testing</b><small>Verification</small></div>
                  <div className="topology-worker"><span className="worker-symbol clay-symbol">03</span><b>Review</b><small>Quality check</small></div>
                  <div className="topology-worker"><span className="worker-symbol ink-symbol">04</span><b>Research</b><small>Technical context</small></div>
                </div>
              </div>
              <footer className="editorial-panel-foot"><span>Conceptual agent routing</span><span>Not a live neural-network or execution trace</span></footer>
            </article>

            <div className="dashboard-side-stack">
              <article className="editorial-panel review-spotlight">
                <span className="section-kicker">04 — NEEDS ATTENTION</span><div className="review-spotlight-count">03</div><h3>Reviews waiting</h3><p>Proposed changes are ready for a closer look in the review workspace.</p><button onClick={()=>setPage("Review Center")}>Open review centre <ArrowUpRight size={15}/></button>
              </article>
              <article className="editorial-panel provider-panel">
                <header className="editorial-panel-head"><div><span className="section-kicker">05 — PROVIDER LAYER</span><h2>Provider setup</h2></div><span className="setup-state">NOT CONNECTED</span></header>
                <div className="provider-row"><span className="provider-monogram">G</span><span><b>Gemini</b><small>Master provider · planned</small></span><em>Pending</em></div>
                <div className="provider-row"><span className="provider-monogram">M</span><span><b>Mistral</b><small>Coding workers · planned</small></span><em>Pending</em></div>
                <div className="provider-row"><span className="provider-monogram">G</span><span><b>Groq</b><small>Fast workers · planned</small></span><em>Pending</em></div>
                <footer className="editorial-panel-foot"><span>Provider roles from the project plan</span><span>No keys are read here</span></footer>
              </article>
            </div>
          </section>

          <section className="editorial-panel activity-panel">
            <header className="editorial-panel-head"><div><span className="section-kicker">06 — RECENT SIGNAL</span><h2>Workspace activity</h2><p>Example events to demonstrate the activity layout.</p></div><span className="sample-pill">SAMPLE FEED</span></header>
            <div className="editorial-activity-list">{visible.slice(0,4).map((row,i)=><div className="editorial-activity-row" key={row[0]}><span className="activity-monogram">{row[0]}</span><span className="activity-copy"><b>{row[1]}</b><small>{row[2]}</small></span><em>{row[3]}</em><span className="activity-age">{i===0?"NOW":i===1?"24M":"1H"}</span></div>)}{!visible.length&&<p className="empty">No sample activity matches that search.</p>}</div>
          </section>
          <footer className="page-foot"><span>DuoAI Studio · Workspace</span><span>Illustrative metrics · Existing Python backend unchanged</span></footer>
        </div>}
    </main>
    <button className="effects" onClick={()=>setLow(v=>!v)}><i className={low ? "on" : ""}/>{low ? "Low effects on" : "Low effects off"}</button>
  </div>;
}
