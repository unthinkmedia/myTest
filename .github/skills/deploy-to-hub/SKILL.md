---
name: deploy-to-hub
description: >
  Deploy, share, or send the current experiment to Azure Builder Hub.
  Triggers when the user says "deploy this", "deploy to hub", "share this",
  "send this", "send to hub", "publish this", "push to hub", or similar phrases.
---

# Deploy to Hub Skill

Deploy the current experiment from the Playground sandbox to Azure Builder Hub so it appears in the gallery for other Microsoft employees.

**Zero-config** — authenticates via your existing `az login` session. No keys, secrets, or `.env` files needed.

## When to Use

This skill triggers on any of these user intents:
- "Deploy this" / "Deploy to hub" / "Deploy my experiment"
- "Share this" / "Share to hub"
- "Send this" / "Send to hub"
- "Publish this to hub"
- "Push to hub"

## Prerequisites

The user must be logged in to Azure CLI (`az login`). If they haven't, the deploy script will print clear instructions. No keys or secrets are needed — just a Microsoft account.

## Step-by-Step Workflow

### Step 1: Pre-Flight Check

1. Check that `experiment.json` has been updated from default values. If it still says `"My Experiment"` / `"A playground for rapid prototyping"`, infer a name and description from the user's work, then update it.
2. Run `npm install` if `node_modules/` doesn't exist.
3. Check `az account show` works. If not, tell the user to run `az login` first.

### Step 2: Deploy

Run the deploy script:

```bash
npm run deploy
```

If the user wants to skip thumbnail generation (faster deploy), use:

```bash
npm run deploy:quick
```

### Step 3: Report

After the script completes, extract the output and tell the user:

- The project ID
- The version number
- The Hub URL where they can view it
- The preview URL

The deploy script automatically:
- Takes a Playwright screenshot and resizes it to a 400×210 card thumbnail
- Writes `previewUrl` and `thumbnailUrl` back into `experiment.json`
- Uploads the updated `experiment.json` and `thumbnail.png` alongside the built files

Example output:
> "Your experiment has been deployed to Hub as project `abc123` (version 2).
> View it at: https://victorious-ocean-0ea8ca710.5.azurestaticapps.net/project/abc123
> Preview: https://victorious-ocean-0ea8ca710.5.azurestaticapps.net/api/projects/abc123/preview/
> Thumbnail: https://victorious-ocean-0ea8ca710.5.azurestaticapps.net/api/projects/abc123/preview/thumbnail.png"

## Flags

| Flag | Effect |
|------|--------|
| `--skip-thumbnail` | Skip Playwright thumbnail generation (faster) |
| `--skip-build` | Skip `npm run build` (use existing dist/) |

## Troubleshooting

| Error | Fix |
|-------|-----|
| `deploy.config.json not found` | You must be in the project root |
| `Not logged in to Azure` | Run `az login` then try again |
| `experiment.json not found` | You must be in the project root |
| `Hub registration failed (401)` | Your Azure account may not be in the allowed tenant. Verify with `az account show`. |
| `Thumbnail generation failed` | Use `--skip-thumbnail` or install Playwright: `npx playwright install chromium` |
