# 🍃 Mineleaf Network Discord Bot

An enterprise-grade, high-performance, asynchronous Discord application crafted using `discord.py` (v2.0+) and Python 3.10+. This specialized system offers a fully unified solution tailored for Minecraft communities, combining an interactive multi-category ticket engine, dynamic staff recruitment applications, robust server moderation commands, automatic profanity scrubbing, visual payment-gateway embedded storefront interfaces, and live real-time server tracking loops.

---

## 📑 Table of Contents
1. [Core Architectural Overview](#-core-architectural-overview)
2. [Detailed Feature Breakdown](#-detailed-feature-breakdown)
   - [Advanced Ticketing & Transcripts](#1-advanced-ticketing--transcripts)
   - [Staff Recruitment Pipeline](#2-staff-recruitment-pipeline)
   - [Automated Chat Moderation & Filtering](#3-automated-chat-moderation--filtering)
   - [Server Status Tracking Engine](#4-server-status-tracking-engine)
   - [Branded Store Layout & Gateway Routing](#5-branded-store-layout--gateway-routing)
3. [🔥 New Features Added](#-new-features-added)
4. [🛠️ Source Code Configuration Map (Line-by-Line Guide)](#%EF%B8%8F-source-code-configuration-map-line-by-line-guide)
5. [⚙️ Administrative Commands & Runtime Modifiers](#%EF%B8%8F-administrative-commands--runtime-modifiers)
6. [🔒 Environment & Security Requirements](#-environment--security-requirements)
7. [🚀 Step-by-Step Installation & Boot Guide](#-step-by-step-installation--boot-guide)
8. [💾 Database & Memory States Lifecycle](#-database--memory-states-lifecycle)
9. [🔍 Troubleshooting Common Runtime Issues](#-troubleshooting-common-runtime-issues)
10. [📄 Licensing & Contribution Agreements](#-licensing--contribution-agreements)

---

## 🏛️ Core Architectural Overview

The Mineleaf Bot structure leverages completely asynchronous event cycles coupled with stateful `discord.ui` components (persistent views, buttons, modals, and select dropdowns). Running on an optimized non-blocking framework, the bot is split conceptually into operational layers: 
                  ┌───────────────────────────────────────┐
                  │        Discord Gateway API            │
                  └──────────────────┬────────────────────┘
                                     │
                                     ▼
                  ┌───────────────────────────────────────┐
                  │    Asyncio Main Event Loop Handler    │
                  └─────┬───────────────────────────┬─────┘
                        │                           │
                        ▼                           ▼
          ┌───────────────────────────┐ ┌───────────────────────────┐
          │   Text/Slash Interaction  │ │   Aiohttp Heartbeat Task  │
          └─────────────┬─────────────┘ └─────────────┬─────────────┘
                        │                             │
                        ▼                             ▼
          ┌───────────────────────────┐ ┌───────────────────────────┐
          │ Modals / Tickets / Action │ │          Status   
          └───────────────────────────┘ └───────────────────────────┘


---

## 🔮 Detailed Feature Breakdown

### 1. Advanced Ticketing & Transcripts
* **Dynamic Node Allocation:** When a user selects a configuration category via the `TicketCategorySelect` menu, the bot maps strict permission overrides preventing general visibility across the guild while keeping `@everyone` locked out.
* **Staff Panel Injections:** Open tickets instantly initialize a `TicketControlView` which exposes persistent tracking controls for claiming operations (`✋`) or hard thread closures (`🔒`).
* **Automated Data Backup Hooks:** Upon initiating thread execution deletion routines, an exhaustive data payload parses the historical logs up to 200 text messages deep, formatting a secure download `.txt` log file pushed directly to the user's direct messages.
* **Duplication Prevention:** Restricts users from cluttering the server by enforcing a strict one-active-ticket-at-a-time rule.

### 2. Staff Recruitment Pipeline
* **Native Modals:** Moving completely away from primitive message parsing, candidates run through a rich graphic modal UI capture window (`StaffApplicationModal`) reducing platform frictions.
* **Rigorous Metric Mapping:** Forms validate length limits, tracking specific keys:
  * Minecraft Username (Max 16 Chars)
  * Real-world age bounds
  * Operational Timezone matrix
  * Comprehensive history detailing historical positions held
  * Direct structural motivation responses
* **Automated Log Processing:** Converts validation metrics instantly into structured hex embeds sent straight to tracking teams.

### 3. Automated Chat Moderation & Filtering
* **Instant RegEx Detection:** A highly targeted, compiled Regular Expression checks for pattern match variations involving web standard links, malicious file distribution locations, or unauthorized community discord invite endpoints.
* **Banned Phrasing Arrays:** Intercepts real-time incoming communication profiles, automatically filtering matching terms from the core block collection (`BAD_WORDS`).

### 4. Server Status Tracking Engine
* **Non-Blocking Background Workers:** Built around the robust `discord.ext.tasks` scheduling loop framework, an isolated network thread spins continuously alongside standard user interactions.
* **Automated Live Node Testing:** Pulls telemetry from the defined target string (`SERVER_IP`), keeping community counters informed.

### 5. Branded Store Layout & Gateway Routing
* **Optimized Emojis:** Integrates custom animation references mapping out tiered store profiles alongside functional local pricing values spanning across NPR and INR currencies (e.g., *MLOP+*, *Titan*, *Phoenix*, *Mirage*, *Ember*).
* **One-Click Support Routing:** Embeds custom action buttons (`StoreTicketView`) allowing consumers to jump into buying interfaces instantly.

---

## 🔥 New Features Added

### 📝 Integrated Staff Application Dropdown Option
* Fully integrated the **"Staff Application"** choice into the master utility ticketing menu selection structure. 
* Launches the input form modal, captures standard player variables, and embeds candidate details safely within a secure administrative evaluation workflow room.

### 🌐 Global IP Fast-Responder System
* Listens across all synchronized structural guild text layout environments. Typing `ip` or executing the `!ip` alternative commands will immediately dispatch an interactive server informational anchor window.
* Embedded directly with your custom server identity graphic asset for polished layout display formatting.

### 🖼️ Ticket Case Thumbnails
* Active instances launched via client support processes automatically feature the initialized image URL string mapping (`TICKET_THUMBNAIL_URL`) targeted inside the upper-right layout boundaries for a seamless UI wrapper.

---

## 🛠️ Source Code Configuration Map (Line-by-Line Guide)

When tailoring the primary script code execution profile to match your environment, you must audit and update these key code locations:

* **Line 26 (`SERVER_IP`):** Reconfigure the network core address variable string (`"play.mineleaf.fun"`) to target your server node's physical entry hostname.
* **Line 34 (`STATUS_CHANNEL_ID`):** Define the numeric target channel ID where the automated status task dumps its data updates.
* **Line 901 - 903 (Message Event Processing Block):** Inside the primary text-parsing logic checking message triggers, configure the automated keyword patterns (`ip`, `!ip`) to deploy your server's customized parameters.
* **Line 1024 (Branding Utilities Embed):** Personalize the design assets inside your help pagination or system outputs by substituting global footer icons and information URLs.
* **Line 1094 (Telemetry Update Function):** Locate the runtime network ping query engine mapping within the asynchronous task loop. Replace default validation routes with your active domain check metrics.

---

## ⚙️ Administrative Commands & Runtime Modifiers

You no longer have to hardcode changes into the file structure when tweaking live network fields. High-level staff commands can adjust system paths dynamically on the fly:

| Invocation Syntax | Targeted Payload | Action Profile | Default State |
| :--- | :--- | :--- | :--- |
| `!setip` | `<ip>` | Overwrites core reference address models globally. | `play.mineleaf.com` |
| `!setservericon` | `<image_url>` | Repoints background graphic resources used for public embeds. | Hardcoded Default Asset |
| `!setticketicon` | `<image_url>` | Rewrites corner graphic URLs for active support embeds. | Hardcoded Default Asset |
| `!setstaffrole` | `<role_id>` | Binds application ping actions to designated HR roles. | `None` |
| `!status` | None | Triggers an immediate, forced status check on the server network. | Real-time Execution |

---

## 🔒 Environment & Security Requirements

To operate safely without exposing private API credentials inside your source control, the system reads critical runtime tokens via an isolated ecosystem file. 

Create a file named precisely `.env` in the root execution directory:
```env
DISCORD_TOKEN=your_actual_discord_bot_token_here
