# 📖 MLops Learning Path — Guided Walkthrough

This is the hands-on companion to the [README](../README.md). Work through it top to bottom. Every stage has three parts:

- **🎓 Concept** — the idea, in plain language.
- **🔍 In this repo** — exactly which files and lines to read.
- **🧪 Exercise** — something to change yourself, so the lesson sticks.

Don't just read — **type the commands and break things on purpose.** That's how MLops clicks.

> **Prerequisites:** basic Python, a terminal, and Git. Docker and an AWS account are only needed for Stages 4 and 6.

---

## Stage 0 — Setup

```bash
git clone https://github.com/Parsa8304/Intent-classifier-model.git
cd Intent-classifier-model
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

✅ **Check:** `python -c "import flask, sklearn; print('ok')"` prints `ok`.

---

## Stage 1 — Data & Training 📊🏋️

### 🎓 Concept
A model is only as good as its data, and reproducible ML depends on keeping **data separate from code**. You train a model, then save the fitted model as a **artifact** (here a pickle file) so you never have to retrain just to make a prediction.

### 🔍 In this repo
- `data/intents.csv` — 20 labelled sentences across 4 intents.
- `model/train.py` — loads the CSV, builds a `CountVectorizer → MultinomialNB` pipeline, prints accuracy, and writes `model/artifacts/intent_model.pkl`.

```bash
python model/train.py
```

You should see the accuracy printed and the artifact saved. The `.pkl` is git-ignored on purpose — **artifacts are build outputs, not source code.**

### 🧪 Exercise
1. Add a new intent (e.g. `farewell` with `bye`, `see you`, `goodbye`) to `data/intents.csv`.
2. Re-run `python model/train.py`.
3. Predict on `"goodbye"` (after Stage 2) and confirm the new intent appears.

> ❓ **Think:** why is training accuracy 100%? (Hint: the model is being scored on the same tiny data it learned from — great for a demo, misleading in real life. Real projects split into train/test sets.)

---

## Stage 2 — Serving the model 🌐

### 🎓 Concept
A trained model is useless until something can *call* it. Wrapping it in an HTTP API lets any application send text and get a prediction back. Loading the model **once at startup** (not per request) is a key performance pattern.

### 🔍 In this repo
- `model/intent_model.py` — `IntentModel` loads the artifact and exposes `predict()` returning `{intent, probabilities}`.
- `app.py` — Flask app with `/`, `/health`, and `/predict`; validates input and returns `400` on bad requests.
- `wsgi.py` — the entrypoint Gunicorn imports in production.

```bash
python app.py
# in another terminal:
curl -X POST http://127.0.0.1:6000/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"how do I reset my password"}'
```

Notice `app.py` never imports scikit-learn — it only talks to `IntentModel`. That separation is what lets you swap the model later without touching the API.

### 🧪 Exercise
- Send a request with no `text` field and confirm you get HTTP `400`.
- Add a new endpoint `GET /labels` that returns `model.labels`.

---

## Stage 3 — Testing ✅

### 🎓 Concept
Tests are the safety net that makes automation (CI/CD) possible. For ML services you test two things: the **model** (does it return the right shape and sane outputs?) and the **API** (does each endpoint behave, including errors?).

### 🔍 In this repo
- `tests/test_model.py` — output shape, probabilities summing to 1, a known prediction.
- `tests/test_app.py` — `/health`, a successful `/predict`, and the `400` error paths, using Flask's test client (no server needed).

```bash
pytest -q        # expect: 7 passed
```

### 🧪 Exercise
- Add a test asserting that `"thank you so much"` is classified as `praise`.
- Break `app.py` (e.g. remove the validation) and watch a test fail — that's the net working.

---

## Stage 4 — Containerising with Docker 🐳

### 🎓 Concept
"It works on my machine" is the enemy of deployment. A container bundles your code, dependencies, and runtime into one portable image that runs the same everywhere.

### 🔍 In this repo
- `Dockerfile` — starts from `python:3.13-slim`, installs deps, **trains the model during build**, exposes port 6000, and runs Gunicorn.
- `.dockerignore` — keeps the venv, git history, and docs out of the image.

```bash
docker build -t intent-classifier .
docker run --rm -p 6000:6000 intent-classifier
curl -X POST http://127.0.0.1:6000/predict -H "Content-Type: application/json" -d '{"text":"hello"}'
```

### 🧪 Exercise
- Run `docker images intent-classifier` and note the size.
- Read why the `Dockerfile` removes `gcc`/`libc-dev` after installing — that's image-size hygiene.

---

## Stage 5 — Continuous Integration ⚙️

### 🎓 Concept
CI runs your build and tests automatically on every change, so bugs are caught in minutes — not after they reach users. Green checkmarks become the gate for merging.

### 🔍 In this repo
- `.github/workflows/ci.yml` — two jobs: **test** (install → train → pytest) and **docker** (build the image), with `docker` depending on `test`.

### 🧪 Exercise
1. Push this repo to your own GitHub account.
2. Open the **Actions** tab and watch the workflow run.
3. Open a PR with a failing test and confirm the check goes red and blocks merge.

> 🚀 **Next level (CD):** extend the workflow to push the image to a registry (Docker Hub / ECR) and trigger a deploy when `main` is green.

---

## Stage 6 — Deployment 🚀

### 🎓 Concept
Production servers need the app to **start on boot, restart on crash, and sit behind a proper web server**. The classic Linux recipe: Gunicorn (WSGI server) managed by systemd, with Nginx as the public-facing reverse proxy.

### 🔍 In this repo
- `userdata.sh` — paste into an EC2 instance's *user data* (or run on any fresh Ubuntu box). It installs packages, clones the repo, trains the model, registers a `systemd` service for Gunicorn, and configures Nginx on port 80.

```
🌍 Internet  →  Nginx :80  →  Gunicorn :6000  →  Flask (wsgi:app)
```

### 🧪 Exercise
- Launch a free-tier EC2 Ubuntu instance, paste `userdata.sh` as user data, and open port 80 in the security group.
- Hit `http://<public-ip>/` with your prediction payload.
- On the box, inspect the service: `systemctl status intent_gunicorn` and `journalctl -u intent_gunicorn`.

---

## 🎓 You're done — what you built

You took a model from a CSV all the way to a running server, with tests and CI guarding every change. That end-to-end loop **is** MLops. From here, pick one tool from the README's "Where to go next" section (MLflow, DVC, Kubernetes, monitoring) and bolt it onto the stage it extends.

Happy shipping! 🚀
