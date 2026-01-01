# Google Sheets Template

## Sheet Setup

Create a Google Sheet named: **"CTO Sidekick - Projects"**

Create a worksheet named: **"Projects"**

## Column Headers (Row 1)

| A | B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|---|
| Project | Priority | Status | Agent | Last Update | Next Action | Deadline | GPU? | Model |

## Example Data (Rows 2+)

| Project | Priority | Status | Agent | Last Update | Next Action | Deadline | GPU? | Model |
|---------|----------|--------|-------|-------------|-------------|----------|------|-------|
| Antenna ML Pipeline | 1 | Queued | | | Implement batch processing for image classification | 2026-01-15 | Yes | Sonnet 4 |
| APRS Audio Tools | 2 | Pending | | | Create CLI wrapper for audio decoder | 2026-01-10 | No | Qwen |
| eButterfly Export | 3 | Blocked | | | Waiting for API access | 2026-02-01 | No | |
| Pipecat Voice | 4 | Pending | | | Research VAD frameworks | 2026-01-20 | Yes | Gemini 2.0 |

## Field Descriptions

### Project (Column A)
- **Required:** Yes
- **Format:** Text
- **Description:** Name of the project. Must match a key in `config.yaml` `projects` section.
- **Example:** `Antenna ML Pipeline`

### Priority (Column B)
- **Required:** Yes
- **Format:** Number (1-999)
- **Description:** Lower number = higher priority. Orchestrator picks lowest number first.
- **Example:** `1`

### Status (Column C)
- **Required:** Yes
- **Format:** Text (specific values)
- **Valid Values:**
  - `Pending` - Ready to start
  - `Queued` - Waiting in queue
  - `In Progress` - Currently being worked on (set by orchestrator)
  - `Paused` - Paused for higher priority work
  - `Blocked` - Can't proceed due to blocker
  - `Completed` - Done
- **Note:** Orchestrator will update this field

### Agent (Column D)
- **Required:** No
- **Format:** Text
- **Description:** Which agent is currently working (set by orchestrator)
- **Example:** `Claude`, `Qwen`, `Gemini`
- **Note:** Orchestrator updates this field

### Last Update (Column E)
- **Required:** No
- **Format:** ISO 8601 timestamp or human-readable date
- **Description:** When status was last updated
- **Example:** `2026-01-01T14:30:00`
- **Note:** Orchestrator updates this field

### Next Action (Column F)
- **Required:** Yes (for Pending/Queued projects)
- **Format:** Text
- **Description:** What the agent should work on. This becomes the prompt.
- **Example:** `Implement batch processing pipeline for insect image classification`
- **Note:** Be specific - this is the instruction Claude will receive

### Deadline (Column G)
- **Required:** No
- **Format:** Date (YYYY-MM-DD or natural format)
- **Description:** Target completion date
- **Example:** `2026-01-15`

### GPU? (Column H)
- **Required:** No
- **Format:** Text (`Yes` or `No`)
- **Description:** Whether this task requires GPU (for future routing)
- **Example:** `Yes`

### Model (Column I)
- **Required:** No
- **Format:** Text
- **Description:** Preferred model for this work (for future routing)
- **Valid Values:** `Sonnet 4`, `Qwen`, `Gemini 2.0`, etc.
- **Example:** `Sonnet 4`

## Sharing the Sheet

**IMPORTANT:** After creating the sheet, you must share it with your service account:

1. Open the `credentials/sheets-api.json` file
2. Find the `client_email` field (looks like `xxx@xxx.iam.gserviceaccount.com`)
3. In Google Sheets, click "Share"
4. Add that email address with "Editor" permissions
5. Click "Send"

## Tips

- Start with 2-3 projects to test the system
- Use clear, specific "Next Action" descriptions
- Lower priority numbers run first (1 before 2, 2 before 3)
- The orchestrator checks the sheet every 60 seconds (configurable)
- You can manually update priorities anytime - orchestrator will adapt
- Set status to `Blocked` for projects you want to skip temporarily
- Set status to `Completed` when done manually

## Testing Your Setup

After creating the sheet:

```bash
# This will attempt to read your sheet
python src/test_basic.py
```

If it can't connect, double-check:
1. Sheet name matches `config.yaml`
2. Worksheet is named "Projects"
3. Credentials file path is correct
4. Sheet is shared with service account email
