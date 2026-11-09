"""Restricted JSON-lines bridge from Electron to the existing DuoAI Python core.

The renderer never imports Python modules or receives provider credentials.
Requests are allow-listed and each response is a single JSON line.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import core
import provider_registry
from orchestrator.master import validate_master_plan


def _provider_state():
    cfg = core.get_cfg()
    result = []
    for name, spec in provider_registry.PROVIDERS.items():
        result.append({
            "id": name,
            "label": {
                "claude": "Anthropic Claude", "chatgpt": "OpenAI",
                "gemini": "Google Gemini", "mistral": "Mistral",
                "groq": "Groq", "openrouter": "OpenRouter",
                "cerebras": "Cerebras",
            }.get(name, name.title()),
            "connected": bool(core.get_key(name)),
            "model": cfg.get(core.MK[name], spec.default_model),
            "models": list(spec.models),
            "master": cfg.get("master_provider") == name,
        })
    return result


def _list_runs(project_id):
    if project_id != "adhoc" and (len(project_id) != 8 or any(c not in "0123456789abcdef" for c in project_id)):
        raise ValueError("Invalid project identifier.")
    root = core.WORK / project_id / "agents"
    runs = []
    if root.exists():
        for folder in sorted(root.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            record = folder / "run.json"
            if folder.is_dir() and record.is_file():
                try:
                    data = json.loads(record.read_text("utf-8"))
                    if isinstance(data, dict) and data.get("run_id") == folder.name:
                        runs.append(data)
                except (OSError, ValueError):
                    continue
    return runs[:30]


def dispatch(method, args):
    if not isinstance(args, dict):
        raise ValueError("Request arguments must be an object.")

    if method == "health":
        return {
            "ok": True,
            "app": "DuoAI Studio",
            "backend": "python-core",
            "providers": len(provider_registry.PROVIDERS),
            "provider_status": _provider_state(),
        }

    if method == "providers.list":
        cfg = core.get_cfg()
        return {
            "providers": _provider_state(),
            "master_provider": cfg.get("master_provider", "gemini"),
            "lead_provider": cfg.get("lead", "claude"),
            "coding_mode": bool(cfg.get("coding", True)),
        }

    if method == "providers.save":
        provider = args.get("provider")
        if provider not in provider_registry.PROVIDERS:
            raise ValueError("Unsupported provider.")
        api_key = args.get("api_key", "")
        if api_key:
            if not isinstance(api_key, str) or len(api_key) > 4096:
                raise ValueError("Invalid API key value.")
            core.set_key(provider, api_key)
        cfg = core.get_cfg()
        model = args.get("model")
        if model is not None:
            if not isinstance(model, str) or not model.strip() or len(model) > 200:
                raise ValueError("Invalid model name.")
            cfg[core.MK[provider]] = model.strip()
        if args.get("make_master") is True:
            cfg["master_provider"] = provider
        core.set_cfg(cfg)
        return {"providers": _provider_state(), "master_provider": cfg["master_provider"]}

    if method == "providers.remove":
        provider = args.get("provider")
        if provider not in provider_registry.PROVIDERS:
            raise ValueError("Unsupported provider.")
        core.del_key(provider)
        return {"providers": _provider_state()}

    if method == "providers.test":
        provider = args.get("provider")
        if provider not in provider_registry.PROVIDERS:
            raise ValueError("Unsupported provider.")
        models = core.test_provider_connection(provider)
        return {"provider": provider, "connected": True, "models": models}

    if method == "projects.list":
        return {"projects": core.list_projects()}

    if method == "projects.create":
        name = args.get("name")
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 100:
            raise ValueError("Project name must be 1–100 characters.")
        return {"project": core.new_project(name.strip())}

    if method == "projects.get":
        project_id = args.get("project_id")
        project = next((p for p in core.list_projects() if p["id"] == project_id), None)
        if project is None:
            raise ValueError("Project not found.")
        return {"project": project}

    if method == "projects.update":
        project = args.get("project")
        if not isinstance(project, dict):
            raise ValueError("Project must be an object.")
        existing = next((p for p in core.list_projects() if p["id"] == project.get("id")), None)
        if existing is None:
            raise ValueError("Project not found.")
        # The renderer may update only these user-editable fields.
        existing["name"] = str(project.get("name", existing["name"]))[:100].strip()
        existing["prompt"] = str(project.get("prompt", existing.get("prompt", "")))[:12000]
        core.save_project(existing)
        return {"project": existing}

    if method == "memory.get":
        return {"memory": core.get_mem()}

    if method == "memory.save":
        value = args.get("memory")
        if not isinstance(value, str):
            raise ValueError("Memory must be text.")
        core.set_mem(value)
        return {"memory": core.get_mem()}

    if method == "master.plan":
        goal = args.get("goal")
        if not isinstance(goal, str) or not goal.strip() or len(goal) > 12000:
            raise ValueError("Describe the work first (maximum 12,000 characters).")
        project_root = args.get("project_root")
        if project_root is not None and (not isinstance(project_root, str) or len(project_root) > 2048):
            raise ValueError("Invalid project folder.")
        plan = core.create_master_plan(goal.strip(), project_root=project_root)
        return {"plan": plan.as_dict()}

    if method == "master.run":
        payload = args.get("plan")
        if not isinstance(payload, dict):
            raise ValueError("A Master plan is required.")
        cfg = core.get_cfg()
        provider = payload.get("master_provider")
        if provider not in provider_registry.PROVIDERS or not core.get_key(provider):
            raise ValueError("Connect the selected Master provider before running workers.")
        plan = validate_master_plan(payload.get("tasks"), goal=payload.get("goal", ""), provider=provider)
        project_id = args.get("project_id", "adhoc")
        project_context = args.get("project_context", "")
        if not isinstance(project_context, str) or len(project_context) > 20000:
            raise ValueError("Project context is too large.")
        result = core.run_master_workers(plan, project_id=project_id, project_context=project_context)
        return {"run": result}

    if method == "runs.list":
        project_id = args.get("project_id", "adhoc")
        if not isinstance(project_id, str):
            raise ValueError("Invalid project identifier.")
        return {"runs": _list_runs(project_id)}

    if method == "runs.list_all":
        project_ids = ["adhoc"] + [project["id"] for project in core.list_projects()]
        runs = []
        for project_id in project_ids:
            runs.extend(_list_runs(project_id))
        return {"runs": runs[-60:]}

    raise ValueError("Unsupported backend operation.")


def main():
    for line in sys.stdin:
        request_id = None
        try:
            request = json.loads(line)
            request_id = request.get("id")
            method = request.get("method")
            result = dispatch(method, request.get("args", {}))
            response = {"id": request_id, "ok": True, "result": result}
        except Exception as exc:
            response = {
                "id": locals().get("request_id"),
                "ok": False,
                "error": str(exc)[:2000],
            }
        sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
