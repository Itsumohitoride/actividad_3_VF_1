# AGENTS.md — Agent map for K8S Microservices Project

> Entry point for any agent. Progressive disclosure: read what you need.

---

## 1. Before start (required)

0. **graphify before ANY operation.** Run `graphify query "<context>"` before any grep, read, glob, or file search. Always. No exceptions.
1. Run python3 scripts/check_harness.py. Fail? Stop, fix env first.
2. Read progress/current.md for last session state.
3. Read feature_list.json. Pick **one** pending feature. Work one at a time.

## 2. Repo structure — SINGLE repo

This root = project repo. Code, configs, charts, and pipelines all live here.

| Location | Contents |
|----------|----------|
| Root ./ | AGENTS.md, scripts/, docs/, progress/, .agents/, feature_list.json |
| src/ | Microservice source code (Java/Spring Boot + Gradle) |
| src/tests/ | Auto tests |
| charts/ | Helm charts for microservice deployment |
| k8s/argocd/ | ArgoCD Application manifests and config |
| .github/workflows/ | CI/CD pipeline definitions |

## 3. Repo map

| File / dir | What | When read |
|-----------------------------|-------------------------------|-----------|
| feature_list.json | Tasks with status | Always, start |
| progress/current.md | Current session state | Always |
| progress/history.md | Append-only past sessions | Historical context |
| docs/architecture.md | Project architecture | Before implement |
| docs/conventions.md | Style, naming, Docker/Helm/K8s conventions | Before write code |
| docs/verification.md | How to verify work | Before mark done |
| scripts/check_harness.py | Verification orchestrator | Validate state |
| src/ | Microservice source code | Implement |
| src/tests/ | Auto tests | Verify |
| charts/ | Helm chart templates | Before Helm changes |
| k8s/argocd/ | ArgoCD manifests | Before ArgoCD work |
| .github/workflows/ | CI/CD pipelines | Before CI/CD work |

## 4. Hard rules (non-negotiable)

- **One feature at a time.** No mix tasks in same session.
- **Features go through testing before done.** Implementer leaves in "testing". Leader asks human if tests pass. Only then mark "done".
- **Each feature in own branch.** Before start: create feature/<id>-<name> from develop.
- **MRs target develop.** Never edit main directly.
- **Document in progress/current.md** while working, not at end.
- **Leave repo clean** before session close (see section 7).
- **Don't know? Search docs/** before invent.
- **NEVER implement code yourself.** You are a Leader (Orquestador). Decompose work, launch subagents, coordinate. Never write code, never edit files in src/, charts/, k8s/, .github/. The `implementer` subagent writes code.
- **graphify before ANY operation (MANDATORY).** Before grep, read, glob, or any file search: ALWAYS run `graphify query "<question>"` first. If graphify returns useful context, use it. Only fall back to grep/read if graphify returns nothing relevant. The user explicitly requires this — do not skip.
- **Always respect the skill system.** Load relevant skill before launching subagents. Skills contain critical context.

## 5. Working with Git

### Push to remote
```bash
git push origin feature/<id>-<name>
```

### Pull latest develop
```bash
git fetch origin develop
git checkout develop
git pull origin develop
```

### Create PR
```bash
gh pr create --base develop --head feature/<id>-<name> --title "Feature <id>: <name>" --body "<short desc>"
```

## 6. Pick and start task

```
1. git checkout develop
2. git pull origin develop
3. python3 scripts/sync_pull.py develop (if remote changed)
4. feature_list.json -> filter pending, pick smallest id
5. git checkout -b feature/<id>-<name>
6. Status -> in_progress in feature_list.json, save
7. progress/current.md: feature, branch, start time, plan
```

## 7. Session close (lifecycle)

Before done:

1. python3 scripts/check_harness.py -- all green.
2. Task done? Set status: "done" in feature_list.json, record transition.
3. Leader asks human for session cost, runs python3 scripts/log_cost.py.
4. Implementer loads skill git-commit, commits in feature branch.
5. Leader pushes feature branch:
   ```bash
   git push origin feature/<id>-<name>
   ```
6. Leader creates Merge Request against develop:
   ```bash
   gh pr create --base develop --head feature/<id>-<name> --title "Feature <id>: <name>" --body "<short desc>"
   ```
7. Move progress/current.md summary to end of progress/history.md.
8. Clear progress/current.md, leave template only.
9. No temp files, no print() debug, no TODOs without context.

## 8. graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, invoke the `skill` tool with `skill: "graphify"` before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## 9. Docker / Helm / K8S development

When working on features for this project (microservice, Docker, Helm, Kubernetes, ArgoCD, CI/CD):

### Load these skills before launching implementer

| Feature type | Skill(s) to load |
|-------------|-----------------|
| Docker / K8S / Helm | `.agents/skills/devops-engineer/SKILL.md` |
| CI/CD pipelines | `.agents/skills/devops-engineer/SKILL.md` |
| Java/Spring Boot microservice | .agents/skills/devops-engineer/SKILL.md (no skill Java puro, usar contexto Spring Boot)
| Documentation | `.agents/skills/documentation-writer/SKILL.md` |

### Build & test commands

```bash
# Local dev with Docker
docker compose up --build -d
curl http://localhost:8080/health

# Docker build
docker build --no-cache -t microservice:latest .

# Helm lint
helm lint ./charts/*

# Helm template preview
helm template ./charts/microservice --values ./charts/microservice/values-dev.yaml

# Run microservice tests
docker compose run --rm test    # tests dentro del contenedor
```

### Key references

- Docker: multi-stage builds, HEALTHCHECK, non-root user, .dockerignore
- Helm: values.yaml + overrides, _helpers.tpl, templates/
- Kubernetes: Deployments, Services, Ingress, ConfigMaps, HPAs
- ArgoCD: Application CRD, auto-sync, self-heal, prune
- GitHub Actions: CI/CD workflows, triggers, secrets

## 10. Blocked?

- Re-read relevant section from docs/.
- Tool not work as expected? No workaround. Document block in progress/current.md, stop session.
