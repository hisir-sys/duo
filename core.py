import base64, json, mimetypes, os, re, time, uuid, wave, tempfile, threading
from pathlib import Path

import provider_registry

HOME = Path.home() / ".duoai"
PROJ, WORK = HOME / "projects", HOME / "workspaces"
for d in (PROJ, WORK):
    d.mkdir(parents=True, exist_ok=True)
CFG, MEM, KEYS = HOME / "config.json", HOME / "memory.md", HOME / "keys.json"
MODELS = {name: list(spec.models) for name, spec in provider_registry.PROVIDERS.items()}
MK = {name: f"{name}_model" for name in MODELS}
MK["chatgpt"] = "openai_model"  # Preserve existing DuoAI user settings.
KN = {name: spec.key_name for name, spec in provider_registry.PROVIDERS.items()}
CODING = ("You are a principal software engineer. Design before you code, write complete, runnable, "
          "production-quality code with error handling and no placeholders, prefer simple robust solutions, "
          "and add brief tests. Put every file in a fenced block whose info string is `lang path=relative/file.ext`. "
          "Explain key decisions in a few lines.")


def _load(p, d):
    try:
        return json.loads(p.read_text("utf-8"))
    except Exception:
        return d


def _atomic_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        try: os.unlink(tmp)
        except OSError: pass
        raise


def _save(p, o):
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{p.name}.", suffix=".tmp", dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(o, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, p)
    except Exception:
        try: os.unlink(tmp)
        except OSError: pass
        raise


# ---- config, login ------------------------------------------------------
def get_cfg():
    c = {key: models[0] for key, models in MODELS.items()}
    c.update({"lead": "claude", "coding": True})
    saved = _load(CFG, {})
    if isinstance(saved, dict):
        c.update({k: v for k, v in saved.items() if k in c})
    if c["lead"] not in KN:
        c["lead"] = "claude"
    c["coding"] = bool(c["coding"])
    for provider in KN:
        key = MK[provider]
        if not isinstance(c[key], str) or not c[key].strip():
            c[key] = MODELS[provider][0]
    return c


def set_cfg(c):
    _save(CFG, c)


def migrate_legacy_keys():
    """Move old plaintext credentials into the OS vault, then delete the legacy file."""
    if not KEYS.exists():
        return
    legacy = _load(KEYS, {})
    if not isinstance(legacy, dict) or not legacy:
        return
    try:
        import keyring
        if getattr(keyring.get_keyring(), "priority", 0) <= 0:
            return
        for provider, storage_name in KN.items():
            value = legacy.get(storage_name)
            if isinstance(value, str) and value:
                keyring.set_password("duoai", storage_name, value)
        KEYS.unlink(missing_ok=True)
    except Exception:
        # The old file is never read as a credential fallback.
        return


def get_key(p):
    migrate_legacy_keys()
    if p not in KN: raise ValueError("Unknown provider")
    env = provider_registry.get_spec(p).env_name
    if os.environ.get(env): return os.environ[env]
    try:
        import keyring
        if getattr(keyring.get_keyring(), "priority", 0) <= 0: return None
        return keyring.get_password("duoai", KN[p])
    except Exception:
        # Never read API credentials from the legacy plaintext keys.json.
        return None


def set_key(p, v):
    if p not in KN or not v.strip(): raise ValueError("Enter a non-empty API key.")
    try:
        import keyring
        if getattr(keyring.get_keyring(), "priority", 0) <= 0:
            raise RuntimeError("No secure OS credential vault is configured.")
        keyring.set_password("duoai", KN[p], v.strip())
    except Exception as e:
        raise RuntimeError(f"Secure credential storage is unavailable; key was not saved: {e}") from e
    legacy = _load(KEYS, {})
    if isinstance(legacy, dict) and KN[p] in legacy:
        legacy.pop(KN[p], None)
        if legacy: _save(KEYS, legacy)
        else: KEYS.unlink(missing_ok=True)


def del_key(p):
    try:
        import keyring
        keyring.delete_password("duoai", KN[p])
    except Exception: pass
    legacy = _load(KEYS, {})
    if isinstance(legacy, dict) and KN.get(p) in legacy:
        legacy.pop(KN[p], None)
        if legacy: _save(KEYS, legacy)
        else: KEYS.unlink(missing_ok=True)

def client(p):
    key = get_key(p)
    if not key:
        raise RuntimeError(f"Sign in to {p.title()} first, or set the matching API-key environment variable.")
    return provider_registry.create_client(p, key, timeout=120, max_retries=2)


def list_models(p, strict=False):
    return provider_registry.list_models(p, client(p), fallback=not strict)


def test_provider_connection(p):
    """Verify credentials and connectivity by requesting the provider model list."""
    return list_models(p, strict=True)


# ---- global memory.md (read on every call, so it is always in sync) ------
def get_mem():
    if not MEM.exists():
        _atomic_text(MEM, "# Shared memory\n\n")
    return MEM.read_text("utf-8")


def set_mem(t):
    if len(t) > 100000: raise ValueError("Memory is limited to 100 KB.")
    _atomic_text(MEM, t)


def add_mem(lines):
    existing = get_mem().rstrip()
    known = {line.strip().lstrip("- ").casefold() for line in existing.splitlines()}
    additions = []
    for item in lines:
        value = str(item).strip()
        if value and value.casefold() not in known:
            additions.append(f"- {value}")
            known.add(value.casefold())
    if additions:
        set_mem(existing + "\n" + "\n".join(additions) + "\n")


def system_prompt(cfg):
    s = "You are one of two AI collaborators (Claude and ChatGPT) working on the same project."
    s += "\n\nShared memory (user-approved facts and preferences; follow them):\n" + get_mem()
    return s + ("\n\n" + CODING if cfg.get("coding") else "")


# ---- projects -----------------------------------------------------------
def new_project(name):
    p = {"id": uuid.uuid4().hex[:8], "name": name, "prompt": "", "tasks": [], "log": []}
    save_project(p)
    return p


def save_project(p):
    if not re.fullmatch(r"[a-f0-9]{8}", str(p.get("id", ""))):
        raise ValueError("Invalid project identifier")
    if not isinstance(p.get("name"), str) or not p["name"].strip():
        raise ValueError("Project name is required")
    if not isinstance(p.get("tasks", []), list) or not isinstance(p.get("log", []), list):
        raise ValueError("Project tasks and history must be lists")
    _save(PROJ / f"{p['id']}.json", p)


def list_projects():
    projects = []
    for path in PROJ.glob("*.json"):
        p = _load(path, None)
        if isinstance(p, dict) and re.fullmatch(r"[a-f0-9]{8}", str(p.get("id", ""))) and isinstance(p.get("name"), str):
            p.setdefault("prompt", "")
            p.setdefault("tasks", [])
            p.setdefault("log", [])
            if isinstance(p["tasks"], list) and isinstance(p["log"], list):
                projects.append(p)
    return sorted(projects, key=lambda p: p["name"].casefold())


def safe_export_path(project_id, relative):
    if not re.fullmatch(r"[a-f0-9]{8}", str(project_id)):
        raise ValueError("Invalid project identifier")
    rel = Path(relative)
    if rel.is_absolute() or rel.drive or not rel.parts or ".." in rel.parts:
        raise ValueError("Unsafe export path")
    root = (WORK / project_id).resolve()
    target = (root / rel).resolve()
    if target != root and root not in target.parents:
        raise ValueError("Export path escapes the workspace")
    return target


def export_code(p):
    out = []
    if not re.fullmatch(r"[a-f0-9]{8}", str(p.get("id", ""))):
        return out
    for path, code in re.findall(r"\x60\x60\x60[^\n]*?path=(\S+)\n(.*?)\x60\x60\x60", "\n".join(p.get("log", [])), re.S):
        try:
            f = safe_export_path(p["id"], path.strip("\x60\"'"))
        except ValueError:
            continue
        f.parent.mkdir(parents=True, exist_ok=True)
        _atomic_text(f, code)
        out.append(str(f))
    return out


# ---- attachments ----------------------------------------------------------
def load_att(path):
    if os.path.getsize(path) > 15 * 1024 * 1024:
        raise ValueError("Attachments are limited to 15 MB.")
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

        emitted = False
        def go(options):
            nonlocal emitted
            out = []
            with client(p).messages.stream(**options) as st:
                for t in st.text_stream:
                    emitted = True
                    out.append(t)
                    emit(t)
            return "".join(out)
        if thinking:
            try:
                return go({**kw, "max_tokens": 12000, "thinking": {"type": "enabled", "budget_tokens": 4000}})
            except Exception:
                # Retry without extended thinking only when no partial text was emitted.
                if emitted:
                    raise
                return go(kw)
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


def parse_json_payload(out):
    candidate = out.strip()
    fenced = re.search(r"\x60\x60\x60(?:json)?\s*(.*?)\x60\x60\x60", candidate, re.I | re.S)
    if fenced: candidate = fenced.group(1).strip()
    decoder = json.JSONDecoder()
    for i, char in enumerate(candidate):
        if char in "[{":
            try: return decoder.raw_decode(candidate[i:])[0]
            except json.JSONDecodeError: continue
    raise ValueError("The AI returned invalid JSON. Please retry.")


def validate_plan(value):
    if not isinstance(value, list) or not 2 <= len(value) <= 6:
        raise ValueError("A valid plan must contain 2–6 tasks.")
    tasks = []
    for i, task in enumerate(value, 1):
        if not isinstance(task, dict): raise ValueError(f"Task {i} is not an object.")
        title, instructions = task.get("title"), task.get("instructions")
        assignee = str(task.get("assignee", "")).lower()
        if not isinstance(title, str) or not title.strip() or len(title) > 160:
            raise ValueError(f"Task {i} has an invalid title.")
        if not isinstance(instructions, str) or not instructions.strip() or len(instructions) > 12000:
            raise ValueError(f"Task {i} has invalid instructions.")
        if assignee not in ("claude", "chatgpt", "openai", "gpt"):
            raise ValueError(f"Task {i} has an invalid assignee.")
        tasks.append({"title": title.strip(), "assignee": "chatgpt" if assignee in ("chatgpt","openai","gpt") else "claude",
                      "instructions": instructions.strip(), "output": ""})
    return tasks


def plan(goal, atts, cfg):
    sys = system_prompt(cfg) + (
        '\n\nYou are the lead. Split the request into 2-6 non-overlapping tasks. Include implementation, tests, '
        'and independent review where appropriate. Assign each to "claude" or "chatgpt". '
        'Return ONLY a JSON array of objects with title, assignee, instructions.')
    return validate_plan(parse_json_payload(ask(cfg["lead"], sys, goal, atts, cfg)))

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


def suggest_memory(goal, tasks, cfg):
    sys = ('Return ONLY a JSON array of up to 3 short, durable, non-sensitive facts or preferences worth '
           'remembering, or []. Do not duplicate existing memory:\n' + get_mem())
    out = ask(cfg["lead"], sys, f"Request: {goal}\nTasks: " + "; ".join(t["title"] for t in tasks), [], cfg)
    facts = parse_json_payload(out)
    if not isinstance(facts, list): raise ValueError("Memory suggestions must be a JSON array.")
    return [str(x).strip()[:300] for x in facts[:3] if isinstance(x, str) and x.strip()]

class Recorder:
    MAX_SECONDS = 120

    def __init__(self, max_seconds=120):
        self.max_seconds = min(self.MAX_SECONDS, max(10, int(max_seconds)))
        self.chunks, self.frames = [], 0
        self.lock, self.stopped, self.stream = threading.Lock(), False, None

    def start(self):
        import sounddevice as sd
        if self.stream is not None: raise RuntimeError("Recording is already active.")
        def callback(data, frames, _time, _status):
            with self.lock:
                if self.stopped: raise sd.CallbackStop
                remaining = self.max_seconds * 16000 - self.frames
                if remaining <= 0: raise sd.CallbackStop
                take = min(frames, remaining)
                self.chunks.append(data[:take].copy())
                self.frames += take
                if take < frames or self.frames >= self.max_seconds * 16000:
                    raise sd.CallbackStop
        self.stream = sd.InputStream(samplerate=16000, channels=1, dtype="int16", callback=callback)
        self.stream.start()

    def stop(self):
        import numpy as np
        if self.stream is None: raise RuntimeError("No recording is active.")
        try: self.stream.stop()
        finally:
            self.stream.close()
            self.stream = None
        with self.lock:
            self.stopped = True
            chunks, self.chunks = self.chunks, []
        if not chunks: raise RuntimeError("No audio was captured.")
        fd, path = tempfile.mkstemp(prefix="duo-rec-", suffix=".wav", dir=HOME)
        os.close(fd)
        try:
            with wave.open(path, "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
                w.writeframes(np.concatenate(chunks).tobytes())
            return path
        except Exception:
            Path(path).unlink(missing_ok=True)
            raise

def transcribe(path):
    try:
        with open(path, "rb") as f:
            return client("chatgpt").audio.transcriptions.create(model="gpt-4o-mini-transcribe", file=f).text
    finally:
        Path(path).unlink(missing_ok=True)
