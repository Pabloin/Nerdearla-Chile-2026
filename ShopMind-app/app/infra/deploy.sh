#!/bin/bash
# deploy.sh — ShopMind full deploy to AWS
# Usage: bash deploy.sh
set -e

# AWS profile and common tags
export AWS_PROFILE=chile

TAGS="Project=ShopMind ProjectOwner=Pablo\ Ezequiel\ Inchausti ProjectEvent=Nerdearla\ Chile\ AWS\ Booth"
TAG_SPEC_S3='TagSet=[{Key=Project,Value=ShopMind},{Key=ProjectOwner,Value="Pablo Ezequiel Inchausti"},{Key=ProjectEvent,Value="Nerdearla Chile AWS Booth"}]'

echo "🛒 Deploying ShopMind to Amazon Bedrock AgentCore (profile: ${AWS_PROFILE})..."
echo ""

# ── 1. Deploy MCP Servers ──────────────────────────────────────────────────────
echo "📦 Step 1/4 — Deploying MCP Servers..."

for server in mcp_search_review_servers mcp_price_server; do
  echo "  → Deploying ${server}..."
  agentcore configure -e "mcp_servers/${server}.py" \
    --protocol MCP \
    --name "shopmind-${server//_/-}"
  agentcore launch
  echo "  ✅ ${server} deployed"
done

echo ""
echo "⏳ Waiting for MCP servers to be ready..."
sleep 10

# ── 2. Setup Gateway ───────────────────────────────────────────────────────────
echo ""
echo "🌐 Step 2/4 — Setting up AgentCore Gateway..."
python infra/setup_gateway.py

# ── 3. Deploy Supervisor Agent ─────────────────────────────────────────────────
echo ""
echo "🧠 Step 3/4 — Deploying Supervisor Agent..."
agentcore configure -e agents/supervisor_agent.py \
  --name shopmind-supervisor
agentcore launch
echo "✅ Supervisor agent deployed"

# ── 4. Deploy Frontend ─────────────────────────────────────────────────────────
echo ""
echo "⚛️  Step 4/4 — Deploying Frontend..."
cd frontend
npm install --silent
npm run build

BUCKET="shopmind-demo-chile"
aws s3 mb "s3://${BUCKET}" --profile chile 2>/dev/null || true
aws s3api put-bucket-tagging \
  --bucket "${BUCKET}" \
  --profile chile \
  --tagging "${TAG_SPEC_S3}"
aws s3 sync dist/ "s3://${BUCKET}/" --delete --profile chile

# CloudFront (optional - comment out if not needed for demo)
if [ -n "$CF_DIST_ID" ]; then
  aws cloudfront create-invalidation \
    --distribution-id "$CF_DIST_ID" \
    --paths "/*" \
    --profile chile > /dev/null
fi

echo ""
echo "════════════════════════════════════════"
echo "🎉 ShopMind deployed successfully!"
echo ""
echo "   Local dev:  http://localhost:5173"
echo "   Production: https://${BUCKET}.s3-website.amazonaws.com"
echo ""
echo "   Next: set AGENTCORE_GATEWAY_URL in frontend/.env"
echo "════════════════════════════════════════"
