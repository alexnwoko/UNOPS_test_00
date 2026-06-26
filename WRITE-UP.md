# One-Page Write-Up — Disaster Tweet Classifier

## What I built and why this approach
A binary classifier that flags whether a short text describes a real disaster,
exposed as a public REST API (`POST /predict`, `GET /health`) with a small web UI,
all served by a single Google Cloud Run service.

The model is **TF-IDF + calibrated Logistic Regression** (scikit-learn): word
1–2 grams and character 3–5 grams feed an L2 logistic regression with balanced
class weights, wrapped in probability calibration so the returned `score` is a
real probability. I chose this over a transformer deliberately. The brief
rewards "working code and sensible choices, not state-of-the-art F1," sets a
0.70 F1 floor, a 2-second p95 latency ceiling, and free-tier/no-GPU constraints.
A linear bag-of-words model trains in seconds, yields a ~3.4 MB artifact that
cold-starts quickly, runs entirely on CPU in-container (no external LLM calls at
inference, as required), and clears the bar: **held-out F1 = 0.781**, 5-fold CV
F1 = 0.768 ± 0.010. Measured single-request latency is p95 ≈ 3 ms locally — the
network round trip, not the model, dominates in production.

## UI and hosting decisions
One Cloud Run service hosts everything: FastAPI serves the API and also returns
the static `index.html` at `/`. This means one deploy, one URL, and the UI calls
its own same-origin `/predict` (no CORS, nothing hardcoded). Cloud Run is set to
`min-instances = 0`, 1 vCPU, 512 MiB, no GPU — free-tier friendly and
scale-to-zero. The UI accepts text, calls the API, and clearly shows the label
and calibrated confidence with a colour-coded bar. It handles empty input
(client-side guard), network failure, server errors, and slow responses (a 10-second
abort timeout), and surfaces loading state. It is reachable at a public URL with
no login.

## AI tools used and what I validated or changed
I used an AI coding assistant (see `AI-DISCLOSURE.md` for the tool/model and full
prompt log) to scaffold the training script, FastAPI app, Dockerfile, and UI, and
to draft this documentation. I validated everything rather than trusting it: I ran
the training and confirmed the F1 numbers on a stratified hold-out and via 5-fold
cross-validation; I booted the API locally and tested `/health`, `/predict` (real
disaster, non-disaster, and empty-input → 422), and measured latency; and I
verified the model artifact unpickles correctly by moving the shared `clean()`
preprocessor into its own importable module (a bug the first pass would have hit
under uvicorn). The numbers and behaviour reported here are from those runs.

## Limitations and what I'd improve with more time
TF-IDF ignores word order and context, so figurative language ("this party is on
fire"), sarcasm, and unfamiliar event types are weak spots. The 0.5 threshold is
untuned against the grader's class balance. With more time I would: fine-tune a
compact transformer (e.g. DistilBERT) behind the identical API contract and
compare F1/latency/cost; tune the decision threshold; add input validation and
basic rate limiting; add language detection; and wire up a tiny CI check that
fails the build if F1 drops below 0.70.
