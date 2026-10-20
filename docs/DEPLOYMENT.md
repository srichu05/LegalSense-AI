# LegalSense — Deployment & Desktop Launch Guide

## 1. Deployment Goal

Deploy only the lightweight Python Flask API to a Render web service. The JavaFX desktop client runs locally on the user's machine and connects to this API over HTTP. Groq inference is remote. No transformer models or heavy weights are downloaded or loaded on Render.

## 2. Pre-Deployment Status

- [x] Local Flask API runs (`wsgi.py`).
- [x] All 142 Python unit and API tests pass (`pytest -v`).
- [x] All 22 JavaFX client unit and live integration tests pass (`.\mvnw.cmd test`).
- [x] `requirements.txt` contains pinned, compatible packages with lightweight PyMuPDF 1.24.x and Gunicorn.
- [x] WordNet data installation is reproducible via `scripts/setup_nlp_resources.py`.
- [x] Zero transformer weights required.
- [x] `GET /health` responds with HTTP 200 and readiness status.
- [x] Groq is optional; core WSD, ingestion, and search function with `GROQ_API_KEY` absent.
- [x] Upload limits (default 5 MB) and timeouts (6.0s) enforced.
- [x] App binds to platform `$PORT` via `wsgi.py`.
- [x] Uploaded files are processed in-memory without persistent disk dependence.

## 3. Render Web Service Configuration

- **Environment:** `Python 3.13`
- **Build Command:**
  ```bash
  pip install -r requirements.txt && python scripts/setup_nlp_resources.py
  ```
- **Start Command:**
  ```bash
  gunicorn wsgi:app
  ```

## 4. Environment Variables on Render

| Variable | Required? | Default / Purpose |
|---|---|---|
| `PORT` | Auto-set by Render | Port the WSGI server binds to |
| `LEGAL_SENSE_MAX_UPLOAD_MB` | No | `5` (Maximum document upload size in MB) |
| `LEGAL_SENSE_ENABLE_LLM` | No | `false` (Enable/disable Groq LLM assistance) |
| `GROQ_API_KEY` | No | Optional API key for remote LLM assistance |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` |

Never commit real keys to Git. Enter secrets only in Render's web dashboard environment settings.

## 5. Ephemeral Filesystem Boundaries

Render's free filesystem is ephemeral. In LegalSense:
- Document uploads (`/api/v1/documents/analyze`) are parsed directly from memory streams during the request lifecycle.
- Bundled demonstration corpus documents reside in `data/sample_documents/` and are packaged with the codebase.
- No user-uploaded documents are permanently stored on Render.

## 6. Verification Steps (Post-Deployment)

1. `GET /health` -> verify `"status": "ok"`, `"wsd_ready": true`.
2. `POST /api/v1/analyze` -> submit test sentence and verify candidate senses and evidence.
3. `POST /api/v1/search` -> search bundled corpus and verify ranked passages.
4. Verify graceful behavior with `GROQ_API_KEY` unconfigured.

## 7. Local Desktop Client Launch & Backend Integration

The JavaFX desktop application runs locally on the user's workstation and connects to either the local Flask server or the deployed Render instance:

### Step 1: Start Backend (Local or Remote)
```powershell
# For local testing:
python wsgi.py
```
*(Server listens on `http://127.0.0.1:5000`).*

### Step 2: Launch Desktop Client
```powershell
# Run using the Maven wrapper
.\mvnw.cmd javafx:run

# Or via exec plugin
.\mvnw.cmd exec:java
```

### Step 3: Configure Endpoint in Settings
- By default, the application connects to `http://127.0.0.1:5000`.
- To connect to a deployed Render service, open the **Settings** view in the desktop client, enter `https://<your-service>.onrender.com`, and click **Test Connection** followed by **Save & Apply**.
- Alternatively, set the environment variable before launching:
  ```powershell
  $env:LEGALSENSE_API_URL="https://<your-service>.onrender.com"
  .\mvnw.cmd javafx:run
  ```
- The status pill in the top header will immediately update to indicate online readiness.

## 8. Phase 4 Deployment Verification & Free-Tier Characteristics

### Verified Readiness State
- **WSGI Entrypoint:** `wsgi.py` exposes `app = create_app()`, which binds properly to `$PORT` via `gunicorn wsgi:app` and `python wsgi.py`.
- **Zero Local Model Footprint:** The application requires zero local PyTorch/transformers weights or GPU dependencies, ensuring lightweight container startup (< 50 MB RAM at idle).
- **Automated Resource Provisioning:** `scripts/setup_nlp_resources.py` installs required NLTK corpora (`wordnet`, `punkt_tab`, `averaged_perceptron_tagger_eng`, `stopwords`) deterministically during the build step.
- **Graceful Cloud Fallback:** `GET /health` returns `wsd_ready: true` and `llm_enabled: false` when `GROQ_API_KEY` is not supplied, confirming core functionality without external API tokens.

### Render Free-Tier Operational Constraints
1. **Cold Starts:** When inactive for 15 minutes, Render free-tier web services spin down to zero instances. The first incoming request triggers a container wake-up requiring approximately 30–50 seconds.
2. **Ephemeral Disk:** Uploaded documents are parsed strictly from memory streams. No state is persisted to disk, perfectly fitting Render's ephemeral filesystem.
3. **Outbound Internet:** Standard free web services can make outbound calls to Groq API over HTTPS without firewall restriction.

### Exact User Steps to Complete Render Hosting
Because third-party Render dashboard access requires interactive GitHub/Render OAuth authorization, the repository is fully prepared for one-click deployment:
1. Push this repository to GitHub:
   ```bash
   git push origin main
   ```
2. Log into the [Render Dashboard](https://dashboard.render.com/) and click **New > Web Service**.
3. Connect your GitHub repository.
4. Set **Build Command:** `pip install -r requirements.txt && python scripts/setup_nlp_resources.py`
5. Set **Start Command:** `gunicorn wsgi:app`
6. Under **Environment Variables**, optionally set `GROQ_API_KEY` (if remote LLM assistance is desired).
7. Click **Deploy Web Service**. Once healthy, copy the assigned URL (e.g. `https://legalsense-api.onrender.com`) and paste it into the JavaFX Desktop Client **Settings** screen.

