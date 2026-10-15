# 🚀 EnvDoctor Launch & Distribution Kit

> **Goal**: Position **EnvDoctor** as the essential zero-dependency tool for preventing `.env` drift, missing environment variables, and production deployment outages.
>
> Live Repository: [https://github.com/umutgungorr/envdoctor](https://github.com/umutgungorr/envdoctor)  
> PyPI Package: `pip install envdoctor-cli` / `uvx --from envdoctor-cli envdoctor`  
> GitHub Marketplace Action: `uses: umutgungorr/envdoctor@v1`

---

## 📅 High-Impact Launch Schedule (Timing Blueprint)

| Platform | Recommended Day & Time (EST) | Turkey Time (TRT / UTC+3) | Target Community & Tone |
|---|---|---|---|
| **Hacker News (Show HN)** | Tuesday or Wednesday, 08:30–09:00 AM EST | 15:30–16:00 | Developers, SREs, zero-dependency enthusiasts |
| **Reddit (`r/Python`)** | Tuesday or Wednesday, 10:30 AM EST | 17:30 | Python builders, CLI developers, clean code advocates |
| **Reddit (`r/devops`, `r/webdev`)** | Wednesday or Thursday, 09:30 AM EST | 16:30 | Fullstack engineers, DevOps/CI engineers, Docker users |
| **X / Twitter (Global)** | Simultaneous with HN (Tue 09:00 AM EST) | 16:00 | High-contrast visual terminal screenshots and launch thread |
| **LinkedIn (Global & TR)** | Wednesday, 11:00 AM EST | 18:00 | Engineering leads, DevOps professionals, open-source supporters |

---

## 1. 🟠 Hacker News (Show HN)

### Title Options
1. **Recommended**: `Show HN: EnvDoctor – Zero-dependency CLI to stop .env drift, auto-mask templates, and audit code`
2. **Alternative A**: `Show HN: EnvDoctor – End silent production outages caused by missing environment variables`
3. **Alternative B**: `Show HN: EnvDoctor – A pure Python .env contract linter, template synchronizer, and codebase scanner`

---

### First Comment (OP Introduction — Post Immediately After Submitting)

```markdown
Hey HN! I built EnvDoctor because every engineering team I've worked with has suffered from this exact sequence:

1. A developer adds a new required variable (`STRIPE_WEBHOOK_SECRET`, `REDIS_CLUSTER_URL`) to their local `.env`.
2. They ship their PR, but forget to update `.env.example`.
3. CI passes because tests mock everything.
4. Production deploys and crashes instantly on boot with `KeyError` or `undefined`.
5. When a new engineer joins the team, onboarding takes half a day because `.env.example` is 6 months out of date.

Existing tools either:
- Only lint syntax (like basic quote linters).
- Require huge runtime ecosystems or heavy node_modules dependencies.
- Copy live production secrets into template files if you try to automate it.

EnvDoctor (`envdoctor`) is a zero-dependency CLI written entirely in Python standard library (`re`, `pathlib`, `argparse`, `json`) to fix this:

- 🩺 **Contract Verification (`envdoctor check`)**: Verifies that your active `.env` satisfies all keys required by `.env.example` (with `--strict` for bidirectionality). Returns exit code 1 for CI gates.
- 🔄 **Secret-Safe Auto-Synchronizer (`envdoctor sync`)**: Appends missing variables to `.env.example` while intelligently synthesizing safe dummy placeholders (`your_stripe_secret_here`, `8080`, `localhost`)—never leaking real secret values or private comments.
- 🔍 **Codebase Variable Auditor (`envdoctor audit ./src`)**: Fast heuristic scan across Python, TypeScript, JavaScript, Go, Rust, and PHP files to catch variables referenced in code that are missing from your `.env`.
- 🤖 **GitHub Marketplace Action (`uses: umutgungorr/envdoctor@v1`)**: Drops directly into GitHub Actions to enforce environment contract integrity on every Pull Request.
- ⚡ **Zero Dependencies & Sub-15ms Startup**: Runs anywhere via `uvx --from envdoctor-cli envdoctor` or `pip install envdoctor-cli`.

Code & CI Action: https://github.com/umutgungorr/envdoctor

I'd love your thoughts and feedback!
```

---

## 2. 🔴 Reddit Launch Posts

### A. Subreddit: `r/Python`
**Title**: `I built EnvDoctor: A zero-dependency CLI to prevent missing .env variables, auto-mask template secrets, and audit codebases`  
**Flair**: `Project` / `Showcase`

**Body**:
```markdown
Hi r/Python!

Almost every production outage I've debugged recently traced back to a missing environment variable that was forgotten in `.env.example` during a feature branch merge.

I built **EnvDoctor** (https://github.com/umutgungorr/envdoctor) to eliminate environment drift with zero dependencies:

### Key Capabilities:
- **`envdoctor check`**: Instant contract validation. Flags missing or empty variables and returns clean exit codes for CI.
- **`envdoctor sync`**: Updates `.env.example` automatically with safe mock placeholders (e.g. `API_KEY` -> `your_api_key_here`, `PORT` -> `8080`). Private secrets never leak.
- **`envdoctor audit <path>`**: Scans your codebase (Python `os.environ`/`os.getenv`, Node `process.env`, Go `os.Getenv`, etc.) and alerts you to variables used in code that don't exist in `.env`.
- **Zero Dependencies**: Pure Python stdlib. Starts in <15ms.

Run instantly with uv:
```bash
uvx --from envdoctor-cli envdoctor check
```

Or install via pip:
```bash
pip install envdoctor-cli
```

Feedback and PRs are super welcome!
```

---

## 3. 🌐 X / Twitter Launch Thread

```text
🚨 Tired of production crashing because someone forgot to add a new environment variable to .env.example?

Meet EnvDoctor 🩺 — A zero-dependency CLI to stop .env drift, auto-generate safe template placeholders, and audit your code.

Pure Python stdlib. Sub-15ms startup.

🧵👇
```
