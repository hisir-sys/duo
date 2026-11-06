import base64, json, mimetypes, os, re, time, uuid, wave
from pathlib import Path

HOME = Path.home() / ".duoai"
PROJ, WORK = HOME / "projects", HOME / "workspaces"
for d in (PROJ, WORK):
    d.mkdir(parents=True, exist_ok=True)
CFG, MEM, KEYS = HOME / "config.json", HOME / "memory.md", HOME / "keys.json"
MODELS = {"claude": ["claude-sonnet-5-5", "claude-opus-5-5", "claude-haiku-5-5"],
          "chatgpt": ["gpt-4o", "gpt-4o-mini", "o3"]}
MK = {"claude": "claude_model", "chatgpt": "openai_model"}
KN = {"claude": "claude", "chatgpt": "openai"}
CODING = ("You are a principal software engineer. Design before you code, write complete, runnable, "
          "production-quality code with error handling and no placeholders, prefer simple robust solutions, "
          "and add brief tests. Put every file in a fenced block whose info string is `lang path=relative/file.ext`. "
          "Explain key decisions in a few lines.")


def _load(p, d):
    try:
        return json.loads(p.read_text("utf-8"))
    except Exception:
        return d


def _save(p, o):
    p.write_text(json.dumps(o, indent=2), "utf-8")


# ---- config, login ------------------------------------------------------
def get_cfg():
    c = {"claude_model": MODELS["claude"][0], "openai_model": MODELS["chatgpt"][0], "lead": "claude", "coding": True}
    c.update(_load(CFG, {}))
    return c


def set_cfg(c):
    _save(CFG, c)


def get_key(p):
    try:
        import keyring
        k = keyring.get_password("duoai", KN[p])
        if k:
            return k
    except Exception:
        pass
    env = {"claude": "ANTHROPIC_API_KEY", "chatgpt": "OPENAI_API_KEY"}[p]
    return os.environ.get(env) or _load(KEYS, {}).get(KN[p])


def set_key(p, v):
    try:
        import keyring
        keyring.set_password("duoai", KN[p], v)
    except Exception:
        k = _load(KEYS, {})
        k[KN[p]] = v
        _save(KEYS, k)
        try:
            os.chmod(KEYS, 0o600)
        except Exception:
            pass


def del_key(p):
    try:
        import keyring
        keyring.delete_password("duoai", KN[p])
    except Exception:
        pass
    k = _load(KEYS, {})
    if k.pop(KN[p], None) is not None:
        _save(KEYS, k)


def client(p):
    if p == "claude":
        import anthropic
        return anthropic.Anthropic(api_key=get_key(p))
    from openai import OpenAI
    return OpenAI(api_key=get_key(p))


def list_models(p, strict=False):
    try:
        ids = [m.id for m in client(p).models.list().data]
        if p == "chatgpt":
            ids = sorted(i for i in ids if i.startswith(("gpt", "o")) and "audio" not in i and "realtime" not in i)
        return ids or MODELS[p]
    except Exception:
        if strict:
            raise
        return MODELS[p]


# ---- global memory.md (read on every call, so it is always in sync) ------
def get_mem():
    if not MEM.exists():
        MEM.write_text("# Shared memory\n\n", "utf-8")
    return MEM.read_text("utf-8")


def set_mem(t):
    MEM.write_text(t, "utf-8")


def add_mem(lines):
    t = get_mem().rstrip() + "\n" + "\n".join(f"- {x}" for x in lines if x.strip()) + "\n"
    set_mem(t)


def system_prompt(cfg):
    s = "You are one of two AI collaborators (Claude and ChatGPT) working on the same project."
    s += "\n\nShared memory (user facts and preferences; follow them):\n" + get_mem()
    return s + ("\n\n" + CODING if cfg.get("coding") else "")


# ---- projects -----------------------------------------------------------
def new_project(name):
    p = {"id": uuid.uuid4().hex[:8], "name": name, "prompt": "", "tasks": [], "log": []}
    save_project(p)
    return p


def save_project(p):
    _save(PROJ / f"{p['id']}.json", p)


def list_projects():
    ps = [_load(f, None) for f in PROJ.glob("*.json")]
    return sorted([p for p in ps if p], key=lambda p: p["name"].lower())


def export_code(p):
    out = []
    for path, code in re.findall(r"```[^\n]*?path=(\S+)\n(.*?)```", "\n".join(p["log"]), re.S):
        rel = Path(path.strip("`\"'"))
        if rel.is_absolute() or ".." in rel.parts:
            continue
        f = WORK / p["id"] / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(code, "utf-8")
        out.append(str(f))
    return out


# ---- attachments ----------------------------------------------------------
def load_att(path):
    mime = mimetypes.guess_type(path)[0] or "text/plain"
    name = os.path.basename(path)
    if mime.startswith("image/"):
        return {"name": name, "kind": "image", "mime": mime, "b64": base64.b64encode(open(path, "rb").read()).decode()}
    try:
        if path.lower().endswith(".pdf"):
            from pypdf import PdfReader
            text = "\n".join(pg.extract_text() or "" for pg in PdfReader(path).pages)
        elif path.lower().endswith(".docx"):
            import docx
            text = "\n".join(x.text for x in docx.Document(path).paragraphs)
        else:
            text = open(path, "r", encoding="utf-8", errors="replace").read()
    except Exception as e:
        text = f"(could not read file: {e})"
    return {"name": name, "kind": "text", "text": text[:30000]}


# ---- model calls (streaming) ------------------------------------------------
def ask(p, system, prompt, atts, cfg, thinking=False, on_chunk=None):
    prompt += "".join(f"\n\n[File: {a['name']}]\n{a['text']}" for a in atts if a["kind"] == "text")
    imgs = [a for a in atts if a["kind"] == "image"]
    emit = on_chunk or (lambda t: None)
    if p == "claude":
        content = [{"type": "image", "source": {"type": "base64", "media_type": a["mime"], "data": a["b64"]}} for a in imgs]
        content.append({"type": "text", "text": prompt})
        kw = dict(model=cfg[MK[p]], max_tokens=8000, system=system, messages=[{"role": "user", "content": content}])

        def go(kw):
            out = []
            with client(p).messages.stream(**kw) as st:
                for t in st.text_stream:
                    out.append(t)
                    emit(t)
            return "".join(out)
        if thinking:
            try:
                return go({**kw, "max_tokens": 12000, "thinking": {"type": "enabled", "budget_tokens": 4000}})
            except Exception:
                pass
        return go(kw)
    content = [{"type": "text", "text": prompt}] + [
        {"type": "image_url", "image_url": {"url": f"data:{a['mime']};base64,{a['b64']}"}} for a in imgs]
    out = []
    for ch in client(p).chat.completions.create(model=cfg[MK[p]], stream=True, messages=[
            {"role": "system", "content": system}, {"role": "user", "content": content}]):
        t = ch.choices[0].delta.content if ch.choices else None
        if t:
            out.append(t)
            emit(t)
    return "".join(out)


def improve(prompt, cfg):
    sys = ("Rewrite the user's request as a clear, detailed spec: goal, constraints, tech stack, inputs/outputs, "
           "acceptance criteria, edge cases. Keep their intent. Return only the rewritten prompt.")
    return ask(cfg["lead"], sys, prompt, [], cfg).strip()


def plan(goal, atts, cfg):
    sys = system_prompt(cfg) + (
        '\n\nYou are the lead. Split the request into 2-6 tasks (for software: design, implementation, tests, and a final '
        'review task given to the AI that did not write the main code). Assign each to "claude" or "chatgpt" by strengths. '
        'Reply with ONLY a JSON array: [{"title":"...","assignee":"claude|chatgpt","instructions":"..."}]')
    out = ask(cfg["lead"], sys, goal, atts, cfg)
    return [{"title": t.get("title", ""), "assignee": "chatgpt" if "gpt" in t.get("assignee", "").lower() else "claude",
             "instructions": t.get("instructions", ""), "output": ""}
            for t in json.loads(re.search(r"\[.*\]", out, re.S).group(0))]


def run_tasks(goal, tasks, atts, cfg, thinking, cb, ch):
    done = []
    for i, t in enumerate(tasks, 1):
        cb(f"Running {i}/{len(tasks)}: {t['title']} ({t['assignee']})...")
        ch(f"\n\n### {t['title']} - {t['assignee']}\n\n")
        prior = "".join(f"\n\n## Result of '{d['title']}' ({d['assignee']})\n{d['output']}" for d in done)
        prompt = (f"Overall goal: {goal}\n\nYour task: {t['title']}\n{t['instructions']}{prior}"
                  "\n\nDo only your task and give a complete result.")
        t["output"] = ask(t["assignee"], system_prompt(cfg), prompt, atts, cfg, thinking, ch)
        done.append(t)
    return tasks


def learn(goal, tasks, cfg):
    sys = ('Return ONLY a JSON array of up to 3 short, durable facts or preferences about the user or project worth '
           'remembering for future work, or []. No duplicates of existing memory:\n' + get_mem())
    out = ask(cfg["lead"], sys, f"Request: {goal}\nTasks: " + "; ".join(t["title"] for t in tasks), [], cfg)
    facts = json.loads(re.search(r"\[.*\]", out, re.S).group(0))
    if facts:
        add_mem([str(f) for f in facts])


# ---- voice ----------------------------------------------------------------
class Recorder:
    def start(self):
        import sounddevice as sd
        self.chunks = []
        self.stream = sd.InputStream(samplerate=16000, channels=1, dtype="int16",
                                     callback=lambda d, f, t, s: self.chunks.append(d.copy()))
        self.stream.start()

    def stop(self):
        import numpy as np
        self.stream.stop()
        self.stream.close()
        path = str(HOME / f"rec_{int(time.time())}.wav")
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(16000)
            w.writeframes(np.concatenate(self.chunks).tobytes() if self.chunks else b"")
        return path


def transcribe(path):
    with open(path, "rb") as f:
        return client("chatgpt").audio.transcriptions.create(model="gpt-4o-mini-transcribe", file=f).text
