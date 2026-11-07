#!/usr/bin/env bash
# deploy.sh
# Deploy all Online Safety Companion agents and tools to IBM watsonx Orchestrate.
# Run from the repo root: bash scripts/deploy.sh

set -euo pipefail

# ---------------------------------------------------------------------------
# Load environment
# ---------------------------------------------------------------------------
if [ -f ".env" ]; then
  echo "Loading .env ..."
  export $(grep -v '^#' .env | xargs)
fi

if [ -z "${WATSONX_URL:-}" ] || [ -z "${WATSONX_APIKEY:-}" ]; then
  echo "ERROR: WATSONX_URL and WATSONX_APIKEY must be set in your .env or environment."
  exit 1
fi

# ---------------------------------------------------------------------------
# Authenticate
# ---------------------------------------------------------------------------
echo ""
echo "==> Authenticating with watsonx Orchestrate ..."
wxo-cli env activate \
  --url "$WATSONX_URL" \
  --api-key "$WATSONX_APIKEY"

# ---------------------------------------------------------------------------
# Import the risk_scorer tool
# ---------------------------------------------------------------------------
echo ""
echo "==> Importing risk_scorer tool ..."
wxo-cli tools import \
  --file tools/risk_scorer.py \
  --name risk_scorer

echo "    Done: risk_scorer"

# ---------------------------------------------------------------------------
# Import knowledge base documents
# ---------------------------------------------------------------------------
echo ""
echo "==> Importing knowledge base ..."
for doc in knowledge/grooming_warning_signs.md \
           knowledge/scam_patterns.md \
           knowledge/what_to_do_next.md; do
  echo "    Importing $doc ..."
  wxo-cli knowledge import --file "$doc"
done
echo "    Done: knowledge base"

# ---------------------------------------------------------------------------
# Import collaborator agents first (they must exist before the orchestrator)
# ---------------------------------------------------------------------------
echo ""
echo "==> Importing safety_agent ..."
wxo-cli agents import --file agents/safety_agent.yaml
echo "    Done: safety_agent"

echo ""
echo "==> Importing support_agent ..."
wxo-cli agents import --file agents/support_agent.yaml
echo "    Done: support_agent"

# ---------------------------------------------------------------------------
# Import the orchestrator agent last
# ---------------------------------------------------------------------------
echo ""
echo "==> Importing online_safety_companion (orchestrator) ..."
wxo-cli agents import --file agents/online_safety_companion.yaml
echo "    Done: online_safety_companion"

# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------
echo ""
echo "==> Listing deployed agents ..."
wxo-cli agents list

echo ""
echo "==> Listing deployed tools ..."
wxo-cli tools list

echo ""
echo "Deployment complete."
echo "Open your watsonx Orchestrate instance and start a conversation"
echo "with 'Online Safety Companion'."
