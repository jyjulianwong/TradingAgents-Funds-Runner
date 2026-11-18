# TradingAgents-Funds Runner

A local Docker-based runner that executes [TradingAgents-Funds](https://github.com/jyjulianwong/TradingAgents-Funds) for a configurable list of symbols sequentially, converts each Markdown report to PDF, and uploads the result to a public AWS S3 bucket.

## How it works

1. You edit `config.py` to set the symbols and analysis date.
2. `scripts/run.sh` builds the Docker image and starts the container.
3. Inside the container, the runner calls `TradingAgentsGraph` for each symbol in order.
4. Each completed report (`complete_report.md`) is rendered to PDF via WeasyPrint and uploaded to S3 at the path `reports/{YYYY-MM-DD}/{buy|hold|sell}/{SYMBOL}/final_report.pdf`. The subfolder is derived from the Portfolio Manager's 5-tier rating: `Buy`/`Overweight` → `buy`, `Hold` → `hold`, `Underweight`/`Sell` → `sell`.
5. Reports are also written to a local `reports/` directory via a volume mount.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Terraform](https://developer.hashicorp.com/terraform/install) ≥ 1.6 (for the one-time S3 bucket setup)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (for regenerating the lockfile when upgrading dependencies)
- AWS credentials with `s3:PutObject` permission on the reports bucket

## Repository layout

```
config.py                  # Edit this: symbols, date, analysts
Dockerfile                 # Self-contained image
pyproject.toml             # Python deps; TradingAgents-Funds pinned to a commit SHA
uv.lock                    # Committed lockfile for reproducible builds
.env.example               # Template for secrets and settings
runner/
  main.py                  # Orchestrates the symbol loop → convert → upload
  convert.py               # Markdown → PDF via WeasyPrint
  uploaders/
    base.py                # BaseUploader ABC (adapter interface for future sinks)
    s3.py                  # AWS S3 implementation
.github/
  workflows/
    deploy-terraform.yml   # Plan on PR, apply on push to main
scripts/
  run.sh                   # docker build + docker run convenience wrapper
terraform/
  bootstrap/main.tf        # State bucket, lock table and CI OIDC role (scripts/bootstrap.sh)
  backend.tf               # Remote state config (bucket/table supplied at init time)
  main.tf                  # S3 reports bucket (public-read)
  variables.tf
  outputs.tf
```

---

## Setup

### 1. Bootstrap the account

Requires `jyjulianwong/Infrastructure-GitHub`'s bootstrap to have run in the same
account first — it owns the account-wide GitHub Actions OIDC provider. Then, with
admin credentials for the target account (e.g. after `aws sso login`) and an
authenticated `gh` CLI:

```bash
scripts/bootstrap.sh
```

It shows the plan and asks before applying anything, and is safe to re-run. It
applies `terraform/bootstrap` — the Terraform state bucket
(`<ACCOUNT_ID>-jyjulianwong-tafr-terraform-state`), lock table
(`jyjulianwong-tafr-terraform-lock`), and the IAM role CI assumes through GitHub's
OIDC provider (trusted for this repo's `main` branch and pull requests only — there
are no static AWS keys) — then moves its own state into the state bucket and sets
the `AWS_ACCOUNT_ID` and `AWS_ROLE_ARN` Actions secrets.

### 2. Deploy the reports bucket

Push to `main` (or re-run the latest `Deploy Infrastructure` workflow): CI applies
`terraform/`, creating the public-read reports bucket
(`<ACCOUNT_ID>-jyjulianwong-tafr-reports`).

### 3. Configure secrets

```bash
cp .env.example .env
```

Open `.env` and fill in at minimum:

| Variable | Description |
|---|---|
| `OPENAI_API_KEY` (or other provider key) | LLM API key used by TradingAgents |
| `TRADINGAGENTS_LLM_PROVIDER` | Provider name, e.g. `openai`, `anthropic`, `google` |
| `TRADINGAGENTS_DEEP_THINK_LLM` | Model for deep-thinking agents, e.g. `gpt-4o` |
| `TRADINGAGENTS_QUICK_THINK_LLM` | Model for fast agents, e.g. `gpt-4o-mini` |
| `AWS_DEFAULT_REGION` | Must match the region used in Terraform |

No AWS keys go in `.env`: `scripts/run.sh` passes the container short-lived
credentials from your active AWS CLI session (`aws sso login` before running), and
defaults `AWS_S3_REPORTS_BUCKET_NAME` to that account's reports bucket — set it in
`.env` only to override.

### 4. Configure the run

Edit `config.py`:

```python
SYMBOLS: dict[str, str] = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
    "IE00B4L5Y983": "iShares Core MSCI World UCITS ETF",  # ISINs are also supported
}

ANALYSIS_DATE: str | None = None  # None = today; or "2026-07-18"

ANALYSTS: list[str] = ["market", "social", "news", "fundamentals"]
```

---

## Running

```bash
./scripts/run.sh
```

This builds the Docker image and starts the container. The first build takes a few minutes because it installs all dependencies (including TradingAgents-Funds from GitHub). Subsequent runs with `--no-build` skip the build step:

```bash
./scripts/run.sh --no-build
```

Reports are written locally to `reports/{YYYY-MM-DD}/{SYMBOL}/` and uploaded to S3 at `reports/{YYYY-MM-DD}/{buy|hold|sell}/{SYMBOL}/final_report.pdf`.

To run the equivalent `docker` commands directly:

```bash
docker build -t jyjulianwong-tradingagents-funds-runner .

docker run --rm \
  --env-file .env \
  -v "$(pwd)/config.py:/app/config.py:ro" \
  -v "$(pwd)/reports:/app/reports" \
  jyjulianwong-tradingagents-funds-runner
```

---

## Upgrading TradingAgents-Funds

The dependency is pinned to a specific commit SHA in `pyproject.toml`:

```toml
"tradingagents @ git+https://github.com/jyjulianwong/TradingAgents-Funds.git@<SHA>"
```

To upgrade:

1. Find the target commit SHA or pushed tag in the TradingAgents-Funds repository.
2. Update the SHA (or tag reference) in `pyproject.toml`.
3. Regenerate the lockfile:
   ```bash
   uv lock
   ```
4. Commit both `pyproject.toml` and `uv.lock`.
5. The next `./scripts/run.sh` call rebuilds the image with the new version.

---

## Adding a new upload destination

The upload step uses an adapter pattern. To add a destination (e.g. Google Cloud Storage, Azure Blob):

1. Create a new file in `runner/uploaders/`, e.g. `gcs.py`.
2. Subclass `BaseUploader` and implement `upload()`:
   ```python
   from runner.uploaders.base import BaseUploader

   class GCSUploader(BaseUploader):
       def upload(self, local_path, remote_key) -> str:
           # ... upload logic ...
           return f"https://storage.googleapis.com/{self.bucket}/{remote_key}"
   ```
3. Wire it up in `runner/main.py:_build_uploader()`.

---

## Terraform reference

| Command | Purpose |
|---|---|
| `terraform -chdir=terraform/bootstrap init` then `terraform -chdir=terraform/bootstrap apply` | One-time: create remote state storage |
| `terraform -chdir=terraform init` | Initialise the main stack (pass `-backend-config` args) |
| `terraform -chdir=terraform plan -var="aws_account_id=<ID>"` | Preview changes |
| `terraform -chdir=terraform apply -var="aws_account_id=<ID>"` | Apply changes |
| `terraform -chdir=terraform output` | Print bucket name and URL after apply |
