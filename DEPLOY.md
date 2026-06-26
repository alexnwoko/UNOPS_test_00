# Deployment & Submission Guide

Follow in order. Commands are copy-paste; replace ONLY the bracketed bits.
Everything below runs on **your** machine (your Google Cloud + GitHub accounts).

---

## ⚠️ Anonymity (read first — disqualification risk)
The assessment requires the repo, account, commit history and files to contain
**no real name**. Your repo `github.com/alexnwoko/UNOPS_test_00` contains your
name, so do **two** things:
1. Make the git commits use a **pseudonymous author** (commands below set this
   locally for this repo only).
2. Submit the **Anonymous GitHub** mirror link (https://anonymous.4open.science),
   NOT the github.com/alexnwoko link.

---

## Step 1 — Push the code to GitHub
From the project folder (the one containing `app.py`):

```bash
cd "disaster-api"

# pseudonymous identity for THIS repo only (keeps your name out of history)
git init
git config user.name "anon-candidate"
git config user.email "anon-candidate@users.noreply.github.com"

git add .
git commit -m "Disaster tweet classifier: API, UI, model, docs"
git branch -M main
git remote add origin https://github.com/alexnwoko/UNOPS_test_00.git
git push -u origin main
```

> `model.joblib` IS committed (so the container needs no training). `train.csv`
> is gitignored (public data, not needed to run).

## Step 2 — Create the Anonymous GitHub mirror
Go to https://anonymous.4open.science → "Anonymize a repository" →
paste `https://github.com/alexnwoko/UNOPS_test_00`. The Branch (`main`) and
Commit SHA fields will now populate (they were empty only because the repo had no
commits). Finish, and copy the anonymous URL — **this is the repo link you submit.**

---

## Step 3 — Deploy to Google Cloud Run

### 3a. One-time setup (if not done)
```bash
# install gcloud:  https://cloud.google.com/sdk/docs/install
gcloud auth login
gcloud config set project [YOUR_PROJECT_ID]      # create one at console.cloud.google.com if needed (billing must be enabled)
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```
> Cloud Run needs billing enabled even on free tier. New accounts get a $300 free trial.

### 3b. Deploy (source-based — Cloud Run builds the Docker image for you)
```bash
cd "disaster-api"
gcloud run deploy disaster-tweet-api \
  --source . \
  --region europe-north1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --cpu 1 --memory 512Mi \
  --port 8080
```
When it finishes it prints a **Service URL** like
`https://disaster-tweet-api-xxxx-ew.a.run.app`. That single URL serves:
- UI:   `https://.../`
- API:  `https://.../predict`  and  `https://.../health`

---

## Step 4 — Verify (do this before submitting)
```bash
URL="https://[YOUR-SERVICE-URL]"

curl "$URL/health"
# -> {"status":"ok"}

curl -X POST "$URL/predict" -H "Content-Type: application/json" \
  -d '{"text":"Forest fire near La Ronge Sask. Canada"}'
# -> {"label":1,"score":0.87...}
```
- Open `$URL/` in an **incognito** window → enter a tweet → confirm a prediction shows.
- **Screenshot** that incognito window with the address bar, sample input, and
  the label + confidence visible. Save as PNG/JPG.

---

## Step 5 — Assemble the ONE Word document to email back
Put all of this into a single .docx (the brief requires one Word document):
1. **Live URLs:** the UI URL and the `/predict` + `/health` URLs.
2. **Screenshot** of the hosted UI (incognito, address bar in shot).
3. **API sanity check:** paste the `curl` command from Step 4 and its JSON response.
4. **Anonymous repo link** (the anonymous.4open.science URL from Step 2).
5. **One-page write-up:** paste `WRITE-UP.md` (or attach as PDF).
6. **AI disclosure annex:** paste `AI-DISCLOSURE.md` (mandatory — review/adjust it).
7. Confirm the pre-submit checklist (health ok; predict returns label+score;
   min-instances=0, no GPU; service stays live ≥ 21 days; no real names in repo).

Email to **Winfredk@unops.org** before the deadline (2:00 PM New York time).
Keep the Cloud Run service live for at least 21 days for grading.

---

## Cost / cleanup
Free-tier settings (scale-to-zero, 512 MiB, no GPU) keep this at ~$0. After the
14–21 day grading window you can delete it:
```bash
gcloud run services delete disaster-tweet-api --region europe-north1
```
