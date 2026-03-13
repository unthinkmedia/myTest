---
name: experiment-helper
description: >
  Manage experiment variations in the playground repo. Handles creating new variations from main,
  deleting variations, and promoting a variation to main. Use this skill when the user says
  "make a variation", "create a variation", "delete a variation", "remove a variation",
  "promote variation", "make X the main", "swap main", or any task involving managing
  experiment versions. Also triggers on: "new variant", "try a different version", "branch this".
---

# Experiment Helper Skill

Manage the experiment structure: create variations from main, delete variations, and promote a variation to become the new main.

## Repo Structure

Each repo is a **single experiment**. The structure is:

```
experiment.json                 ← { "name": "...", "description": "..." }
src/
  shell/
    App.tsx                     ← auto-discovers main + variations, renders picker
  main/
    index.tsx                   ← canonical version (single screen)
    <ScreenName>.tsx            ← additional screens for multi-screen flows
    flow.json                   ← optional: screen ordering for flows
  variations/
    <variation-name>/
      meta.json                 ← { "description": "..." }
      index.tsx                 ← variation's version (single screen)
      <ScreenName>.tsx          ← additional screens (multi-screen flows)
      flow.json                 ← optional: screen ordering
```

### Key Rules

- **`src/main/`** is always the canonical version. There is exactly one.
- **`src/variations/<name>/`** holds alternatives. Each must have a `meta.json`.
- **Single-screen experiments** have only `index.tsx` in their folder.
- **Multi-screen flows** have named `.tsx` files + a `flow.json` listing screen order.
- **Auto-discovery**: The shell uses `import.meta.glob` — no manual registration needed.
- **Variation names** use kebab-case (e.g., `compact-table`, `dark-toolbar`).

## Operations

There are exactly three operations. Follow each procedure precisely.

---

### Operation 1: Create a Variation

**Trigger phrases:** "make a variation that ___", "create a variation", "try a different version that ___", "new variant"

**Procedure:**

1. **Determine the variation name.** Derive a short kebab-case name from the user's description.
   - "Make a variation that uses cards instead of a table" → `card-layout`
   - "Try a version with a compact toolbar" → `compact-toolbar`

2. **Copy `src/main/` → `src/variations/<name>/`.**
   Copy all files from `src/main/` into the new variation folder.

3. **Create `src/variations/<name>/meta.json`:**
   ```json
   {
     "description": "User's description of what this variation changes"
   }
   ```

4. **Apply the requested changes** to the files in the variation folder. The main folder stays untouched.

5. **Confirm to the user:** State the variation name, what was changed, and how to view it (the shell picker will auto-discover it).

**Important:**
- NEVER modify files in `src/main/` when creating a variation.
- The variation is a full standalone copy — no imports from main, no shared state.
- If main has a `flow.json`, copy that too.

---

### Operation 2: Delete a Variation

**Trigger phrases:** "delete the ___ variation", "remove ___", "drop ___"

**Procedure:**

1. **Identify the variation folder** under `src/variations/`.
2. **Confirm with the user** before deleting: "Delete variation `<name>`? This removes the entire folder."
3. **Remove the folder:** `rm -rf src/variations/<name>/`
4. **Confirm deletion.** The shell auto-discovers, so no cleanup needed.

**Important:**
- NEVER delete `src/main/`. If the user asks to delete main, explain that main can be replaced (via promotion) but not deleted.

---

### Operation 3: Promote a Variation to Main

**Trigger phrases:** "make ___ the main", "promote ___", "swap main with ___"

**Procedure:**

1. **Identify the variation** to promote under `src/variations/`.
2. **Confirm with the user:** "This will swap `main` with `<name>`. The current main becomes a variation called `previous-main`. Proceed?"
3. **Perform the swap:**
   ```
   mv src/main src/variations/previous-main
   mv src/variations/<name> src/main
   ```
4. **Create `src/variations/previous-main/meta.json`:**
   ```json
   {
     "description": "Former main version, replaced by <name>"
   }
   ```
5. **Remove `meta.json` from the new `src/main/`** (main doesn't need one).
6. **Confirm:** "Done. `<name>` is now the main version. The previous main is preserved as variation `previous-main`."

**Important:**
- If `src/variations/previous-main/` already exists from a prior promotion, ask the user what to do: overwrite it, rename it (e.g., `previous-main-2`), or delete it first.
- The swap must be atomic — use a temp directory if needed to avoid overwriting:
  ```
  mv src/main src/_tmp_main
  mv src/variations/<name> src/main
  mv src/_tmp_main src/variations/previous-main
  ```

---

## Multi-Screen Flows

When the experiment is a multi-screen flow:

- Each screen is a separate `.tsx` file with a descriptive name (e.g., `Overview.tsx`, `Create.tsx`, `Review.tsx`).
- **`flow.json`** defines the screen order:
  ```json
  ["Overview", "Create", "Review"]
  ```
  Values are filenames without the `.tsx` extension.
- The shell reads `flow.json` and renders step navigation (tabs or breadcrumbs).
- If no `flow.json` exists, the folder is treated as single-screen (`index.tsx`).

When creating a variation of a multi-screen flow:
- Copy ALL screens and `flow.json`.
- The variation can modify any subset of screens, add new screens, remove screens, or reorder `flow.json`.

---

## Listing Variations

When the user asks "what variations exist" or "show me the variants":

1. List all folders under `src/variations/`.
2. Read each `meta.json` and display a table:

| Variation | Description |
|-----------|-------------|
| main | *(canonical version)* |
| compact-toolbar | Uses a compact single-row toolbar |
| card-layout | Replaces table with card grid |

---

## Shell Integration

The shell (`src/shell/App.tsx`) handles variation discovery automatically:

- Uses `import.meta.glob` to discover `../main/index.tsx` and `../variations/*/index.tsx`.
- Renders a dropdown/tab picker: **Main** + variation names (derived from folder names, formatted as title case).
- If the active version has `flow.json`, renders step navigation below the picker.
- No manual registration is ever needed.

Do NOT modify the shell when creating, deleting, or promoting variations.
