# DuoAI

A desktop workspace (Windows and Linux) where **Claude and ChatGPT work together on one project**.
You write one prompt, a lead AI splits it into tasks, each task goes to the AI best suited for it,
and both share one memory file. Built with Python and PySide6.

---

## 1. Quick start

```bash
pip install -r requirements.txt
python main.py
```

1. Click **Sign in** next to Claude and next to ChatGPT in the top bar and paste an API key for each.
   The two keys can belong to different accounts or email addresses.
2. Click **+ New project**, type your request in the prompt box.
3. Click **Plan with lead AI**, review or edit the task table, then click **Run tasks**.

Keys: Claude keys come from console.anthropic.com, OpenAI keys from platform.openai.com.
API usage is billed per use and is separate from Claude Pro or ChatGPT Plus subscriptions.
Chat-account email/password login is not possible for third-party apps, so DuoAI uses API keys.

---

## 2. How it works

```
Your prompt  ->  Lead AI plans  ->  Task table (you can edit)  ->  Tasks run in order
                                                                      |
              memory.md  <--- lead AI saves new facts  <--- results stream live
```

- **Lead AI:** Claude or ChatGPT (your choice, "Lead" menu). It reads your prompt and the shared memory,
  then returns 2 to 6 tasks, each assigned to `claude` or `chatgpt`.
- **Task table:** every row is a task (title, assigned AI, instructions). Change the AI, rewrite instructions,
  add rows with **+ Task**, delete with **- Task**. You can skip the lead AI and build the table by hand.
- **Running:** tasks run one after another. Each task receives the overall goal plus the results of
  earlier tasks, so the second AI builds on the first one's work.
- **Review toggle:** "Pause to review plan" on = the plan stops for your edits. Off = it runs immediately.
- **After a run:** the lead AI extracts up to 3 durable facts or preferences and appends them to `memory.md`.

---

## 3. Features

### Shared memory (`memory.md`)
- One global file at `~/.duoai/memory.md`, shown in the right-hand panel (the globe icon).
- It is re-read on every AI call, so both AIs always see the latest version.
- The panel and the file sync both ways about every 1.5 seconds. Edit in the app or in any text editor.
- Automatic learning adds new facts after each run. Delete any line you don't want.

### Models, login and logout
- Model boxes for Claude and ChatGPT in the top bar. Pick from the list or type any model name.
  The choice applies immediately and is remembered.
- After you sign in, the model list is loaded from your account.
- **Sign in** validates the key (a bad key is rejected). **Sign out** deletes the saved key.
- Keys are stored in your operating system's secure keyring. If no keyring is available they go in
  `~/.duoai/keys.json`, readable only by your user.

### Coding mode (on by default)
- Both AIs receive a senior-engineer system prompt: design first, complete runnable code, error handling,
  no placeholders, brief tests.
- The planner adds a final review task assigned to the AI that did not write the main code.
- Code files are labeled with a path. **Export code** writes them to
  `~/.duoai/workspaces/<project id>/`.
- **Claude thinking** turns on Claude's extended thinking for harder problems.

### Good prompting
- **Improve prompt** rewrites your request into a clear spec (goal, constraints, tech stack,
  inputs and outputs, acceptance criteria, edge cases). You can edit the result before planning.

### Attachments and voice
- **Attach:** images (sent to both AIs), plain text and code files, PDF and Word (.docx) files (text is extracted).
- **Mic:** records your voice, transcribes it with OpenAI (`gpt-4o-mini-transcribe`) and adds the text to
  the prompt. Needs a microphone and a signed-in ChatGPT key.

### Projects
- Every project is saved and listed in the sidebar. Click one to reload its prompt, task table and results.
- Results stream live while the AIs write.

---

## 4. Where your data lives

| Path | Contents |
|---|---|
| `~/.duoai/memory.md` | Shared memory |
| `~/.duoai/projects/*.json` | Saved projects (prompt, tasks, results log) |
| `~/.duoai/workspaces/<id>/` | Exported code files |
| `~/.duoai/config.json` | Chosen models, lead AI, coding mode |
| `~/.duoai/keys.json` | API keys, only if no OS keyring exists |

Everything stays on your computer. The only network traffic is calls to the Anthropic and OpenAI APIs.
Your prompts, memory and attachments are sent to those services for each task.

---

## 5. Project structure

- `main.py` - the interface (header, sidebar, task table, prompt area, memory panel, background worker thread).
- `core.py` - everything else: settings, keys, memory, projects, model calls with streaming, planning,
  task running, learning, code export, attachments, voice.
- `requirements.txt` - Python dependencies.

To change behavior, start with these in `core.py`: `CODING` (the engineering prompt), `plan()` (how work is split),
`run_tasks()` (what each task receives), `learn()` (what goes into memory).

---

## 6. Troubleshooting

- **"Key rejected" on sign in:** check the key and that the account has API billing enabled.
- **Model not found:** pick a model from the list loaded after sign in, or type an exact model name.
- **Planning fails with a parse error:** the lead AI returned something other than JSON. Click Plan again,
  or build the table by hand.
- **Mic does nothing:** install `sounddevice`, allow microphone access, and sign in to ChatGPT.
- **Export code finds no files:** turn Coding mode on so code blocks carry `path=` labels.
- **Thinking has no effect:** if a model rejects the thinking setting, the app silently runs without it.
- **No keyring on Linux:** install a keyring backend (for example GNOME Keyring), or rely on the key file.

---

## 7. Known limitations

- Tasks run one at a time, not in parallel.
- Keys are API keys only; there is no browser or chat-account login.
- Memory auto-learning is best effort and can occasionally store something unhelpful. Review `memory.md`.
- Very large attachments are truncated (30,000 characters per text file).
- Code is exported but never executed or tested automatically.
- Voice transcription uses OpenAI only.
- No conversation history inside a project beyond the saved results log.

---

## 8. Future upgrades

**Near term**
- Save any result to memory with one click, and a memory search/filter.
- Parallel task running for independent tasks, with a progress bar per task.
- Cancel button for a running job, plus retry for a single failed task.
- Light/dark theme toggle and adjustable text size.
- Single-file installers: `pip install pyinstaller` then `pyinstaller --noconsole --onefile main.py`
  (a Windows .exe and a Linux AppImage).

**Coding power**
- Run the generated code and tests in a sandbox, feed errors back to the AIs, and loop until tests pass.
- Open a real project folder, let the AIs read existing files and propose diffs instead of whole files.
- Git integration: create a branch, commit each task, show a diff before applying.
- A built-in code viewer with syntax highlighting and a file tree for exported workspaces.

**Collaboration between AIs**
- Debate mode: both AIs answer, then critique each other, and the lead merges the best result.
- Automatic role suggestions based on past results (which AI did better on which task type).
- More providers (Gemini, local models through Ollama) and more than two agents.
- Cost and token tracker per project and per AI.

**Memory**
- Memory sections (about me, per-project, coding style) with per-project overrides.
- Memory sync across devices (your own folder, Git or cloud drive).
- Automatic summarising of old results so long projects stay within context limits.

**Interface**
- A real animated globe on the memory panel, timeline view of runs, drag-to-reorder tasks.
- Voice replies (text to speech) and live voice conversation.
- Drag-and-drop attachments, image generation, and an export of any run to PDF or Word.
- Templates for common jobs (web app, API, bug fix, code review, documentation).

**Security**
- Optional encrypted storage for `memory.md` and projects.
- Per-project key profiles, so different projects can use different accounts.
- A redaction filter that blocks secrets (keys, passwords) from being sent or saved to memory.
