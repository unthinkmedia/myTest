# Fluent Icon Reference for Command Bar

Icon names in `argOverrides.icon` are mapped to `@fluentui/react-icons` as `{Name}20Regular`.
For example, `"icon": "ArrowSync"` becomes `import { ArrowSync20Regular } from '@fluentui/react-icons'`.

## CRITICAL RULE: Never Invent Icon Names

Fluent icon names are **compound** and rarely match simple English words. Before using an icon name:

1. **Check this reference** for common Azure Portal icons
2. **If not listed**, run `python pipeline.py <schema> --validate-only` to verify — the pipeline checks against the actual installed `@fluentui/react-icons` package
3. **Never guess** — names like `Preview`, `Feedback`, `Refresh`, `Close`, `Monitor`, `Metrics`, `Logs`, `Deploy`, `Dashboard`, `Activity`, `Endpoint`, `Identity`, `Access`, `Policy`, `Container`, `Network`, `Compute`, `Tags` do NOT exist as standalone icon names

## Common Icon Name Mistakes

| Wrong (does NOT exist)   | Correct (use this instead)      | Notes                                |
|--------------------------|---------------------------------|--------------------------------------|
| `Preview`                | `PreviewLink`                   | No standalone "Preview" icon         |
| `Feedback`               | `PersonFeedback`                | No standalone "Feedback" icon        |
| `Refresh`                | `ArrowSync`                     | "Refresh" doesn't exist; use sync    |
| `Close`                  | `Dismiss`                       | "Close" doesn't exist in Fluent      |
| `Back`                   | `ArrowLeft`                     | No standalone "Back" icon            |
| `Help`                   | `QuestionCircle`                | No standalone "Help" icon            |
| `Lock`                   | `LockClosed`                    | "Lock" alone doesn't exist           |
| `Logs`                   | `DocumentText`                  | No standalone "Logs" icon            |
| `Monitor`                | `DesktopPulse`                  | No standalone "Monitor" icon         |
| `Metrics`                | `ChartMultiple`                 | No standalone "Metrics" icon         |
| `Dashboard`              | `Board`                         | No standalone "Dashboard" icon       |
| `Deploy`                 | `Rocket`                        | No standalone "Deploy" icon          |
| `Activity`               | `Pulse`                         | No standalone "Activity" icon        |
| `Support`                | `PersonSupport`                 | No standalone "Support" icon         |
| `Cost`                   | `Money`                         | No standalone "Cost" icon            |
| `Diagnose`               | `Stethoscope`                   | No standalone "Diagnose" icon        |
| `Properties`             | `SlideTextSparkle` or `Options` | No standalone "Properties" icon      |
| `Endpoint`               | `PlugConnected`                 | No standalone "Endpoint" icon        |
| `Identity`               | `PersonAccounts`                | No standalone "Identity" icon        |
| `Access`                 | `KeyMultiple`                   | No standalone "Access" icon          |
| `Security`               | `ShieldCheckmark`               | No standalone "Security" icon        |
| `Policy`                 | `ShieldTask`                    | No standalone "Policy" icon          |
| `Governance`             | `Gavel`                         | No standalone "Governance" icon      |
| `Container`              | `Cube`                          | No standalone "Container" icon       |
| `Network`                | `NetworkCheck`                  | No standalone "Network" icon         |
| `Compute`                | `Server`                        | No standalone "Compute" icon         |
| `Tags`                   | `Tag`                           | Plural "Tags" doesn't exist          |
| `Alerts`                 | `Alert`                         | Plural "Alerts" doesn't exist        |
| `Resource`               | `PuzzleCube`                    | No standalone "Resource" icon        |
| `Subscription`           | `Receipt`                       | No standalone "Subscription" icon    |
| `Management`             | `Wrench`                        | No standalone "Management" icon      |
| `Automation`             | `Bot`                           | No standalone "Automation" icon      |
| `Compliance`             | `Certificate`                   | No standalone "Compliance" icon      |
| `Forward`                | `ArrowRight`                    | No standalone "Forward" icon         |

## Verified Azure Portal Icons (argOverrides.icon)

These icon base names are confirmed to exist in `@fluentui/react-icons`:

### Actions
| Base Name          | Full Import Name          | Use For                    |
|--------------------|---------------------------|----------------------------|
| `Add`              | `Add20Regular`            | Create / New               |
| `Delete`           | `Delete20Regular`         | Delete / Remove            |
| `Edit`             | `Edit20Regular`           | Edit / Modify              |
| `Save`             | `Save20Regular`           | Save                       |
| `Dismiss`          | `Dismiss20Regular`        | Close / Cancel / Discard   |
| `ArrowSync`        | `ArrowSync20Regular`      | Refresh / Sync             |
| `ArrowDown`        | `ArrowDown20Regular`      | Download / Move down       |
| `ArrowUp`          | `ArrowUp20Regular`        | Upload / Move up           |
| `ArrowLeft`        | `ArrowLeft20Regular`      | Back / Previous            |
| `ArrowRight`       | `ArrowRight20Regular`     | Forward / Next             |
| `Copy`             | `Copy20Regular`           | Copy to clipboard          |
| `Share`            | `Share20Regular`          | Share                      |
| `Open`             | `Open20Regular`           | Open in new window         |
| `Search`           | `Search20Regular`         | Search                     |
| `Filter`           | `Filter20Regular`         | Filter                     |
| `MoreHorizontal`   | `MoreHorizontal20Regular` | Overflow / More actions    |
| `Play`             | `Play20Regular`           | Start / Run                |
| `Pause`            | `Pause20Regular`          | Pause                      |
| `Stop`             | `Stop20Regular`           | Stop                       |

### Navigation & UI
| Base Name          | Full Import Name            | Use For                  |
|--------------------|-----------------------------|--------------------------|
| `ChevronDown`      | `ChevronDown20Regular`      | Expand                   |
| `ChevronRight`     | `ChevronRight20Regular`     | Navigate / Expand right  |
| `ChevronUp`        | `ChevronUp20Regular`        | Collapse                 |
| `ChevronLeft`      | `ChevronLeft20Regular`      | Navigate back            |
| `Info`             | `Info20Regular`             | Information              |
| `Warning`          | `Warning20Regular`          | Warning / Caution        |
| `CheckmarkCircle`  | `CheckmarkCircle20Regular`  | Success / Verified       |
| `ErrorCircle`      | `ErrorCircle20Regular`      | Error / Failed           |
| `QuestionCircle`   | `QuestionCircle20Regular`   | Help                     |

### Azure Portal Concepts
| Base Name              | Full Import Name                | Use For                     |
|------------------------|---------------------------------|-----------------------------|
| `Globe`                | `Globe20Regular`                | Region / Global             |
| `Key`                  | `Key20Regular`                  | Keys / Secrets              |
| `LockClosed`           | `LockClosed20Regular`           | Locked / Security           |
| `LockOpen`             | `LockOpen20Regular`             | Unlocked                    |
| `Shield`               | `Shield20Regular`               | Security / Protection       |
| `ShieldCheckmark`      | `ShieldCheckmark20Regular`      | Verified security           |
| `People`               | `People20Regular`               | Users                       |
| `Person`               | `Person20Regular`               | User / Identity             |
| `PersonAccounts`       | `PersonAccounts20Regular`       | Identity / Accounts         |
| `PersonFeedback`       | `PersonFeedback20Regular`       | Feedback                    |
| `PersonSupport`        | `PersonSupport20Regular`        | Support                     |
| `Group`                | `Group20Regular`                | Groups                      |
| `Document`             | `Document20Regular`             | Documents / Files           |
| `Folder`               | `Folder20Regular`               | Folders                     |
| `Server`               | `Server20Regular`               | Server / Compute            |
| `Database`             | `Database20Regular`             | Database                    |
| `Cloud`                | `Cloud20Regular`                | Cloud services              |
| `Storage`              | `Storage20Regular`              | Storage                     |
| `Settings`             | `Settings20Regular`             | Settings / Config           |
| `Wrench`               | `Wrench20Regular`               | Tools / Management          |
| `Link`                 | `Link20Regular`                 | Links / URLs                |
| `Tag`                  | `Tag20Regular`                  | Tags / Labels               |
| `Star`                 | `Star20Regular`                 | Favorites                   |
| `Eye`                  | `Eye20Regular`                  | Preview / View              |
| `Rocket`               | `Rocket20Regular`               | Deploy                      |
| `Cube`                 | `Cube20Regular`                 | Container / Resource        |
| `Certificate`          | `Certificate20Regular`          | Certificates / Compliance   |
| `Stethoscope`          | `Stethoscope20Regular`          | Diagnose                    |
| `Gavel`                | `Gavel20Regular`                | Governance                  |
| `Bot`                  | `Bot20Regular`                  | Automation                  |
| `Receipt`              | `Receipt20Regular`              | Subscription / Billing      |
| `Money`                | `Money20Regular`                | Cost / Pricing              |
| `NetworkCheck`         | `NetworkCheck20Regular`         | Network                     |
| `PlugConnected`        | `PlugConnected20Regular`        | Endpoints / Connections     |
| `Board`                | `Board20Regular`                | Dashboard                   |
| `PreviewLink`          | `PreviewLink20Regular`          | Preview features            |
| `Pulse`                | `Pulse20Regular`                | Activity / Health           |
| `Alert`                | `Alert20Regular`                | Alerts / Notifications      |
| `Laptop`               | `Laptop20Regular`               | Devices                     |
| `Apps`                 | `Apps20Regular`                 | Applications                |
| `Grid`                 | `Grid20Regular`                 | Grid view                   |

## How Validation Works

The pipeline (`python pipeline.py schema.json`) automatically validates icon names:

1. It calls `node` to introspect `@fluentui/react-icons` exports
2. For each `argOverrides.icon` value, it checks that `{value}20Regular` exists
3. If any icon is invalid, codegen is **blocked** — you must fix the schema first
4. Run `python pipeline.py schema.json --validate-only` to check without generating code

## Note: Side Nav & Title Icons Are Different

The `icon` field in `sideNav.entries` and `title` uses `AzureServiceIcon` names — a completely different system from Fluent icons. Those names (like `"Info"`, `"People"`, `"Shield"`) are Azure service icon identifiers, NOT `@fluentui/react-icons` names. Only command bar `argOverrides.icon` values are Fluent icon base names.
