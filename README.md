# 🍃 Mineleaf Network Discord Bot

A multi-purpose, feature-rich Discord bot built using `discord.py` to seamlessly handle ticketing, server moderation, interactive store listings, staff applications, automated text moderation, and live Minecraft server status tracking for the Mineleaf Network.

---

## 🔥 Key Features

### 🎫 Advanced Interactive Ticketing System
* **Categorized Tickets:** Users can create tickets through an interactive dropdown select menu covering **General Support**, **Ban/Unban Reports**, **Store**, **Staff Applications**, and **Reporting Players**.
* **Role Integration:** Dynamically assigns permission overwrites to designated support roles based on the specific category chosen.
* **Staff Control Panel:** Interactive claim buttons (`✋`) and lock/close buttons (`🔒`) built into the ticket channels to streamline staff actions.
* **Auto Transcripts:** Automatically generates a text file backup of the channel's message history and sends an embed to the user upon ticket closure.
* **Duplication Prevention:** Restricts users from cluttering the server by enforcing a strict one-active-ticket-at-a-time rule.

### 🛡️ Robust Moderation Engine (Slash Commands)
* `/ban`: Ban malicious members with real-time role hierarchy checks to secure administrative safety.
* `/unban`: Revoke permanent bans safely utilizing distinct numeric user IDs.
* `/mute`: Temporarily timeout users for a customizable duration using Discord's modern native integration.
* `/unmute`: Lift active timeouts effortlessly.
* **Central Log Mapping:** All moderation protocols compile structured log profiles inside your specific staff monitoring logs channel.

### 🛒 Dynamic Shop Interface & Assets
* Features a visually optimized embed layout showcasing ranks (e.g., *MLOP+*, *Titan*, *Phoenix*) with integrated region pricing across INR and NPR currencies.
* Interactive `🎟️ Ticket` interface button attached to the store configuration for quick purchase routing.

### 📋 Interactive Staff Recruitment System
* Modern `discord.ui.Modal` application structure prompts candidates for credentials securely (Age, Region, Professional Background, and Motivation Statement).
* Routes completed profiles straight to separate private channel queues for the Human Resources division to assess.

### 🧹 Automated Chat Protection & Filters
* **Automated Word Guard:** Listens for blacklisted profanities or slurs and checks message context filters.
* **Link Filter Monitoring:** Powered by regex compile protocols targeting dynamic `discord.gg` links or raw web domain invites.

### 📈 Automatic Live Server Monitoring
* Built on top of `discord.ext.tasks`, a repeating background thread tracks your physical Minecraft server host address (`play.mineleaf.fun`), keeping community counters informed.

---

## 🛠️ Configuration & Environment Setup

The bot depends on safe environment parameters to hide secure tokens and custom category IDs. Create a `.env` file in your root folder:

```env
DISCORD_TOKEN=your_secure_bot_token_here
