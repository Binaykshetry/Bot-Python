import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import View, Button, Select, Modal, TextInput
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime, timedelta
import re
import aiohttp

load_dotenv()
                    
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix=['!', ';', ':'], intents=intents, help_command=None)

TICKET_CATEGORY_ID = None
SUPPORT_ROLE_ID = None
LOG_CHANNEL_ID = None
GENERAL_ROLE_ID = None
BAN_UNBAN_ROLE_ID = None
STORE_ROLE_ID = None
REPORT_ROLE_ID = None
STAFF_APP_ROLE_ID = None
SERVER_IP = "play.mineleaf.fun"
SERVER_ICON_URL = "https://i.imgur.com/vH9Z9Y7.png" 
TICKET_THUMBNAIL_URL = "https://i.imgur.com/vH9Z9Y7.png"
STATUS_CHANNEL_ID = 1379023940370042970

# === Store / Vote config — edit these ===
STORE_THUMBNAIL_URL = SERVER_ICON_URL  # swap for the ML logo image used in the store screenshot if different
VOTE_URL = "https://your-voting-site-link-here.com"  # TODO: put your real voting site URL here
VOTE_EMOJI = "<:mineleaf_vote:000000000000000000>"  # TODO: replace with your server's real vote emoji ID

_DIVIDER_LINE = " ".join(["<a:divider1:1446022422754099347>"] * 18)

STORE_LINES = [
    "**Mineleaf Store <:cart:1469961107413139558>**",
    "",
    _DIVIDER_LINE,
    "",
    "**__<a:rank:1446023946205003827> Ranks <a:rank:1446023946205003827>__**",
    "",
    "<a:ranks:1447196150447997019> MLOP+ Rank - NPR 999 / INR 624 <:money:1446024834541948941>",
    "<a:ranks:1447196150447997019> Titan Rank - NPR 799 / INR 499 <:money:1446024834541948941>",
    "<a:ranks:1447196150447997019> Phoenix Rank - NPR 499 / INR 312 <:money:1446024834541948941>",
    "<a:ranks:1447196150447997019> Mirage Rank - NPR 259 / INR 162 <:money:1446024834541948941>",
    "<a:ranks:1447196150447997019> Ember Rank - NPR 99 / INR 62 <:money:1446024834541948941>",
    "",
    _DIVIDER_LINE,
    "",
    "**__<:Coins:1446024317283602545> COINS <:Coins:1446024317283602545>__**",
    "",
    "<:money:1446024834541948941> Rs50 INR / Rs80 NPR - 300 Coins <a:Coin:1445997718769238117>",
    "<:money:1446024834541948941> Rs100 INR / Rs160 NPR - 600 Coins <a:Coin:1445997718769238117>",
    "<:money:1446024834541948941> Rs200 INR / Rs320 NPR - 1200 Coins <a:Coin:1445997718769238117>",
    "<:money:1446024834541948941> Rs300 INR / Rs480 NPR - 1800 Coins <a:Coin:1445997718769238117>",
    "<:money:1446024834541948941> Rs400 INR / Rs640 NPR - 5600 Coins <a:Coin:1445997718769238117>",
    "<:money:1446024834541948941> Rs500 INR / Rs800 NPR - 9999 Coins <a:Coin:1445997718769238117>",
    "",
    "**__CRATES__**",
    "",
    "Yeti Crate - Rs 30 per key",
    "Lali Gurash Crate - Rs 30 per key",
    "Key Crate - Rs 30 per key",
    "Kukuri Crate - Rs 30 per key",
    "Leaf Crate - Rs 30 per key",
    "",
    _DIVIDER_LINE,
    "",
    "Payment Methods:",
    "<:esewa:1446031546841694219> eSewa",
    "<:Khalti:1446031408870195232> Khalti",
    "<:upi:1446031462787973250> Upi",
    "<:crypto:1477626200494047443> Crypto",
    "<:bank:1446031759740506175> Bank Transfer",
    "",
    "<a:A_arrow_arrow:1446032921990266903> Create A Ticket For Purchase",
    "",
    "Regards,",
    "<:mineleaflogo:1476523951785250866> Mineleaf Team!",
]

STORE_DESCRIPTION = "\n".join(STORE_LINES)

tickets = {}
muted_users = {}
staff_application_enabled = True

BAD_WORDS = ['randi', 'muzi', 'madarchod', 'fuck', 'bitch', 'lado', 'puti', 'ash']
URL_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+|www\.[a-zA-Z0-9-]+\.[a-zA-Z]+|discord\.gg/[a-zA-Z0-9]+')


class StaffApplicationModal(Modal, title="Staff Application Form"):
    minecraft_name = TextInput(
        label="Minecraft Username",
        placeholder="Enter your Minecraft username",
        style=discord.TextStyle.short,
        required=True,
        max_length=16
    )
    
    age = TextInput(
        label="Age",
        placeholder="Enter your age",
        style=discord.TextStyle.short,
        required=True,
        max_length=3
    )
    
    timezone = TextInput(
        label="Timezone",
        placeholder="Enter your timezone (e.g., EST, PST, GMT)",
        style=discord.TextStyle.short,
        required=True,
        max_length=50
    )
    
    experience = TextInput(
        label="Previous Staff Experience",
        placeholder="Describe your previous staff experience",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )
    
    why_staff = TextInput(
        label="Why do you want to be staff?",
        placeholder="Tell us why you want to join our staff team",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        category_channel = None
        if TICKET_CATEGORY_ID:
            category_channel = guild.get_channel(TICKET_CATEGORY_ID)

        ticket_number = len(tickets) + 1
        channel_name = f"staff-app-{user.name}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        if SUPPORT_ROLE_ID:
            support_role = guild.get_role(SUPPORT_ROLE_ID)
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        if STAFF_APP_ROLE_ID:
            staff_role = guild.get_role(STAFF_APP_ROLE_ID)
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category_channel,
            overwrites=overwrites
        )

        tickets[ticket_channel.id] = {
            'user_id': user.id,
            'category': 'Staff Application',
            'created_at': datetime.utcnow(),
            'claimed_by': None
        }

        embed = discord.Embed(
            title="<:ml_logo:1446021531603046410>  **OFFICIAL STAFF APPLICATION**",
            description=(
                f"A new application has been submitted to the **Mineleaf Talent Pipeline**.\n"
                f"### 📋 CANDIDATE PROFILE\n"
                f"> **Applicant:** {user.mention}\n"
                f"> **Submission Time:** <t:{int(datetime.utcnow().timestamp())}:F>"
            ),
            color=0xf1c40f, # Gold
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="🆔 Minecraft Username", value=f"```\n{self.minecraft_name}\n```", inline=True)
        embed.add_field(name="🎂 Candidate Age", value=f"```\n{self.age}\n```", inline=True)
        embed.add_field(name="🌍 Region/Timezone", value=f"```\n{self.timezone}\n```", inline=True)
        embed.add_field(name="🎓 Professional Experience", value=f"```\n{self.experience}\n```", inline=False)
        embed.add_field(name="❓ Motivation Statement", value=f"```\n{self.why_staff}\n```", inline=False)
        
        icon_url = bot.user.display_avatar.url
        embed.set_footer(text=f"Mineleaf HR System • Application ID: #{ticket_number}", icon_url=icon_url)
        embed.set_thumbnail(url=user.display_avatar.url)

        ping_message = f"{user.mention}"
        if SUPPORT_ROLE_ID:
            support_role = guild.get_role(SUPPORT_ROLE_ID)
            if support_role:
                ping_message += f" {support_role.mention}"
        
        if STAFF_APP_ROLE_ID:
            staff_role = guild.get_role(STAFF_APP_ROLE_ID)
            if staff_role:
                ping_message += f" {staff_role.mention}"

        await ticket_channel.send(ping_message, embed=embed, view=TicketControlView())

        await interaction.response.send_message(
            f"✅ Staff application submitted successfully! {ticket_channel.mention}",
            ephemeral=True
        )

        if LOG_CHANNEL_ID:
            log_channel = guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                log_embed = discord.Embed(
                    title="📳 New Staff Application",
                    color=discord.Color.gold(),
                    timestamp=datetime.utcnow()
                )
                log_embed.add_field(name="Channel", value=ticket_channel.mention, inline=True)
                log_embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=True)
                log_embed.add_field(name="Minecraft Username", value=str(self.minecraft_name), inline=True)
                
                await log_channel.send(embed=log_embed)


class TicketModal(Modal, title="Please answer the question below."):
    reason = TextInput(
        label="Why are you creating this ticket",
        placeholder="Type response here",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    def __init__(self, category: str):
        super().__init__()
        self.category = category

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket(interaction, self.category, str(self.reason))


class TicketCategorySelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="General Support",
                description="General inquiries, questions, and assistance",
                emoji="🛠️"
            ),
            discord.SelectOption(
                label="Ban/Unban Report",
                description="Appeal bans or report ban-related issues",
                emoji="🔨"
            ),
            discord.SelectOption(
                label="Store",
                description="Purchases, donations, ranks, and store support",
                emoji="💰"
            ),
            discord.SelectOption(
                label="Report Staff or Member",
                description="Report staff members or players for misconduct",
                emoji="🚨"
            ),
            discord.SelectOption(
                label="Staff Application",
                description="Apply for a staff position on MineLeaf",
                emoji="📝"
            )
        ]
        super().__init__(
            placeholder="Select a type below",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_category_select"
        )

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        
        if category == "Staff Application":
            if not staff_application_enabled and not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ **Staff Applications are currently closed.** Please watch announcements for the next wave!",
                    ephemeral=True
                )
                return
            modal = StaffApplicationModal()
            await interaction.response.send_modal(modal)
        else:
            modal = TicketModal(category)
            await interaction.response.send_modal(modal)


class TicketMenuView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketCategorySelect())


class TicketControlView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        if interaction.channel.id not in tickets:
            await interaction.response.send_message("❌ This is not a ticket channel!", ephemeral=True)
            return

        ticket_data = tickets[interaction.channel.id]

        # Permission check
        has_permission = False
        if interaction.user.guild_permissions.administrator:
            has_permission = True
        else:
            # Check for Main Support Role
            if SUPPORT_ROLE_ID:
                support_role = interaction.guild.get_role(SUPPORT_ROLE_ID)
                if support_role and support_role in interaction.user.roles:
                    has_permission = True
            
            # Check for Category-Specific Role
            role_map = {
                "General Support": GENERAL_ROLE_ID,
                "Ban/Unban Report": BAN_UNBAN_ROLE_ID,
                "Store": STORE_ROLE_ID,
                "Report Staff or Member": REPORT_ROLE_ID,
                "Staff Application": STAFF_APP_ROLE_ID
            }
            
            category_role_id = role_map.get(ticket_data['category'])
            if not has_permission and category_role_id:
                category_role = interaction.guild.get_role(category_role_id)
                if category_role and category_role in interaction.user.roles:
                    has_permission = True

        if not has_permission:
            await interaction.response.send_message("❌ Only staff members can close tickets!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🔒 Ticket Closed",
            description=f"This ticket has been closed by {interaction.user.mention}",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        await interaction.response.send_message(embed=embed)
        
        if LOG_CHANNEL_ID:
            log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                user = await bot.fetch_user(ticket_data['user_id'])
                claimed_info = "Not claimed"
                if ticket_data.get('claimed_by'):
                    claimed_user = await bot.fetch_user(ticket_data['claimed_by'])
                    claimed_info = claimed_user.mention
                
                log_embed = discord.Embed(
                    title="📳 Ticket Closed",
                    color=discord.Color.red(),
                    timestamp=datetime.utcnow()
                )
                log_embed.add_field(name="Ticket", value=interaction.channel.name, inline=True)
                log_embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=True)
                log_embed.add_field(name="Type", value=ticket_data['category'], inline=True)
                log_embed.add_field(name="Closed By", value=interaction.user.mention, inline=True)
                log_embed.add_field(name="Claimed By", value=claimed_info, inline=True)
                log_embed.add_field(name="Created At", value=f"<t:{int(ticket_data['created_at'].timestamp())}:R>", inline=True)
                
                await log_channel.send(embed=log_embed)
        
        await asyncio.sleep(3)
        
        transcript = await create_transcript(interaction.channel)
        
        try:
            user = await bot.fetch_user(ticket_data['user_id'])
            transcript_embed = discord.Embed(
                title="📝 Ticket Transcript",
                description=f"Your ticket **{interaction.channel.name}** has been closed.",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            transcript_embed.add_field(name="Type", value=ticket_data['category'], inline=True)
            transcript_embed.add_field(name="Closed By", value=interaction.user.mention, inline=True)
            
            if transcript:
                await user.send(embed=transcript_embed, file=transcript)
            else:
                await user.send(embed=transcript_embed)
        except:
            pass
        
        del tickets[interaction.channel.id]
        await interaction.channel.delete()

    @discord.ui.button(label="Claim Ticket", style=discord.ButtonStyle.green, emoji="✋", custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: Button):
        if interaction.channel.id not in tickets:
            await interaction.response.send_message("❌ This is not a ticket channel!", ephemeral=True)
            return

        ticket_data = tickets[interaction.channel.id]

        # Permission check
        has_permission = False
        if interaction.user.guild_permissions.administrator:
            has_permission = True
        else:
            # Check for Main Support Role
            if SUPPORT_ROLE_ID:
                support_role = interaction.guild.get_role(SUPPORT_ROLE_ID)
                if support_role and support_role in interaction.user.roles:
                    has_permission = True
            
            # Check for Category-Specific Role
            role_map = {
                "General Support": GENERAL_ROLE_ID,
                "Ban/Unban Report": BAN_UNBAN_ROLE_ID,
                "Store": STORE_ROLE_ID,
                "Report Staff or Member": REPORT_ROLE_ID,
                "Staff Application": STAFF_APP_ROLE_ID
            }
            
            category_role_id = role_map.get(ticket_data['category'])
            if not has_permission and category_role_id:
                category_role = interaction.guild.get_role(category_role_id)
                if category_role and category_role in interaction.user.roles:
                    has_permission = True

        if not has_permission:
            await interaction.response.send_message("❌ Only staff members can claim tickets!", ephemeral=True)
            return

        if ticket_data.get('claimed_by'):
            claimed_user = await bot.fetch_user(ticket_data['claimed_by'])
            await interaction.response.send_message(f"❌ This ticket has already been claimed by {claimed_user.mention}!", ephemeral=True)
            return

        tickets[interaction.channel.id]['claimed_by'] = interaction.user.id

        embed = discord.Embed(
            title="✋ Ticket Claimed",
            description=f"This ticket has been claimed by {interaction.user.mention}",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        await interaction.response.send_message(embed=embed)


class StoreTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket", emoji="🎟️", style=discord.ButtonStyle.green, custom_id="store_ticket_button")
    async def open_store_ticket(self, interaction: discord.Interaction, button: Button):
        modal = TicketModal("Store")
        await interaction.response.send_modal(modal)


async def create_transcript(channel):
    try:
        messages = []
        async for message in channel.history(limit=200, oldest_first=True):
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            messages.append(f"[{timestamp}] {message.author.name}: {message.content}")
        
        if messages:
            transcript_text = "\n".join(messages)
            from io import BytesIO
            transcript_file = discord.File(
                fp=BytesIO(transcript_text.encode('utf-8')),
                filename=f"transcript-{channel.name}.txt"
            )
            return transcript_file
        return None
    except:
        return None


async def create_ticket(interaction: discord.Interaction, category: str, reason: str, target_user: discord.Member = None):
    guild = interaction.guild
    user = target_user if target_user else interaction.user

    existing_ticket = None
    for channel_id, ticket_data in tickets.items():
        if ticket_data['user_id'] == user.id:
            channel = guild.get_channel(channel_id)
            if channel:
                existing_ticket = channel
                break

    if existing_ticket:
        await interaction.response.send_message(
            f"❌ {user.mention} already has an open ticket: {existing_ticket.mention}",
            ephemeral=True
        )
        return

    category_channel = None
    if TICKET_CATEGORY_ID:
        category_channel = guild.get_channel(TICKET_CATEGORY_ID)

    ticket_number = len(tickets) + 1
    channel_name = f"ticket-{user.name}-{ticket_number}"

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    if SUPPORT_ROLE_ID:
        support_role = guild.get_role(SUPPORT_ROLE_ID)
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    role_map = {
        "General Support": GENERAL_ROLE_ID,
        "Ban/Unban Report": BAN_UNBAN_ROLE_ID,
        "Store": STORE_ROLE_ID,
        "Report Staff or Member": REPORT_ROLE_ID
    }

    specific_role_id = role_map.get(category)
    if specific_role_id:
        specific_role = guild.get_role(specific_role_id)
        if specific_role:
            overwrites[specific_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    ticket_channel = await guild.create_text_channel(
        name=channel_name,
        category=category_channel,
        overwrites=overwrites
    )

    tickets[ticket_channel.id] = {
        'user_id': user.id,
        'category': category,
        'created_at': datetime.utcnow(),
        'claimed_by': None
    }

    embed = discord.Embed(
        title=f"🎫 NEW SUPPORT CHANNEL • {category.upper()}",
        description=(
            f"### 👋 Welcome to Support, {user.mention}!\n"
            "An administrator has been notified of your request. While you wait, please provide relevant details below.\n\n"
            "**📋 CASE INFORMATION**\n"
            f"> **Subject:** {category}\n"
            f"> **Ticket ID:** `#{ticket_number}`\n"
            f"> **Status:** 🟠 Pending Review\n\n"
            "**📝 INITIAL INQUIRY:**\n"
            f"```\n{reason}\n```"
        ),
        color=0x3498db,
        timestamp=datetime.utcnow()
    )
    icon_url = bot.user.display_avatar.url
    embed.set_footer(text=f"MineLeaf Network • System Automated", icon_url=icon_url)
    if TICKET_THUMBNAIL_URL:
        embed.set_thumbnail(url=TICKET_THUMBNAIL_URL)

    ping_message = f"{user.mention}"
    if SUPPORT_ROLE_ID:
        support_role = guild.get_role(SUPPORT_ROLE_ID)
        if support_role:
            ping_message += f" {support_role.mention}"
    
    if specific_role_id:
        specific_role = guild.get_role(specific_role_id)
        if specific_role:
            ping_message += f" {specific_role.mention}"

    await ticket_channel.send(ping_message, embed=embed, view=TicketControlView())

    await interaction.response.send_message(
        f"✅ Ticket created successfully for {user.mention}! {ticket_channel.mention}",
        ephemeral=True
    )

    if LOG_CHANNEL_ID:
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="📳 New Ticket Created",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            log_embed.add_field(name="Ticket", value=ticket_channel.mention, inline=True)
            log_embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=True)
            log_embed.add_field(name="Type", value=category, inline=True)
            log_embed.add_field(name="Reason", value=reason, inline=False)
            if target_user:
                log_embed.add_field(name="Created By", value=interaction.user.mention, inline=True)
            
            await log_channel.send(embed=log_embed)


@bot.event
async def on_ready():
    print(f'Bot is online and ready!')
    print(f'Logged in as: {bot.user.name}')
    print(f'Bot ID: {bot.user.id}')
    
    bot.add_view(TicketMenuView())
    bot.add_view(TicketControlView())
    bot.add_view(StoreTicketView())

    if not update_server_status.is_running():
        update_server_status.start()

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    try:
        await bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="tickets | /help"
            ),
            status=discord.Status.online
        )
    except Exception as e:
        print(f'Failed to set status: {e}')


@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(member="The member to ban", reason="Reason for the ban")
@app_commands.checks.has_permissions(administrator=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ You cannot ban this member due to role hierarchy!", ephemeral=True)
        return
    
    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You cannot ban yourself!", ephemeral=True)
        return
    
    try:
        await member.ban(reason=f"{reason} | Banned by {interaction.user}")
        
        embed = discord.Embed(
            title="🔨 Member Banned",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Member", value=f"{member.mention} ({member.name})", inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        
        await interaction.response.send_message(embed=embed)
        
        if LOG_CHANNEL_ID:
            log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to ban member: {str(e)}", ephemeral=True)


@bot.tree.command(name="unban", description="Unban a user from the server")
@app_commands.describe(user_id="The ID of the user to unban", reason="Reason for the unban")
@app_commands.checks.has_permissions(administrator=True)
async def unban(interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
    try:
        user_id_int = int(user_id)
        user = await bot.fetch_user(user_id_int)
        
        await interaction.guild.unban(user, reason=f"{reason} | Unbanned by {interaction.user}")
        
        embed = discord.Embed(
            title="✅ User Unbanned",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="User", value=f"{user.mention} ({user.name})", inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        
        await interaction.response.send_message(embed=embed)
        
        if LOG_CHANNEL_ID:
            log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(embed=embed)
    except ValueError:
        await interaction.response.send_message("❌ Invalid user ID! Please provide a valid numeric user ID.", ephemeral=True)
    except discord.NotFound:
        await interaction.response.send_message("❌ This user is not banned!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to unban user: {str(e)}", ephemeral=True)


@bot.tree.command(name="mute", description="Mute a member in the server")
@app_commands.describe(member="The member to mute", duration="Duration in minutes", reason="Reason for the mute")
@app_commands.checks.has_permissions(administrator=True)
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "No reason provided"):
    if member.top_role >= interaction.user.top_role and interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ You cannot mute this member due to role hierarchy!", ephemeral=True)
        return
    
    if member.id == interaction.user.id:
        await interaction.response.send_message("❌ You cannot mute yourself!", ephemeral=True)
        return
    
    try:
        mute_duration = timedelta(minutes=duration)
        await member.timeout(mute_duration, reason=f"{reason} | Muted by {interaction.user}")
        
        muted_users[member.id] = {
            'muted_at': datetime.utcnow(),
            'duration': duration,
            'reason': reason,
            'moderator': interaction.user.id
        }
        
        embed = discord.Embed(
            title="🔇 Member Muted",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Member", value=f"{member.mention} ({member.name})", inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        
        await interaction.response.send_message(embed=embed)
        
        if LOG_CHANNEL_ID:
            log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to mute member: {str(e)}", ephemeral=True)


@bot.tree.command(name="unmute", description="Unmute a member in the server")
@app_commands.describe(member="The member to unmute", reason="Reason for the unmute")
@app_commands.checks.has_permissions(administrator=True)
async def unmute(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    try:
        await member.timeout(None, reason=f"{reason} | Unmuted by {interaction.user}")
        
        if member.id in muted_users:
            del muted_users[member.id]
        
        embed = discord.Embed(
            title="🔊 Member Unmuted",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Member", value=f"{member.mention} ({member.name})", inline=True)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        
        await interaction.response.send_message(embed=embed)
        
        if LOG_CHANNEL_ID:
            log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to unmute member: {str(e)}", ephemeral=True)


class HelpPaginationView(View):
    def __init__(self, user):
        super().__init__(timeout=60)
        self.user = user

    @discord.ui.button(label="🛡️ Moderation", style=discord.ButtonStyle.danger)
    async def moderation_btn(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ This menu is session-locked to the original requester.", ephemeral=True)
            
        embed = discord.Embed(
            title="🛡️ **ADMINISTRATIVE MODERATION SUITE**",
            description=(
                "Advanced tools for managing community safety and server integrity.\n"
                "──────────────────────────\n"
                "### 🔨 PUNISHMENT COMMANDS\n"
                "• `/ban <member> [reason]` - Permanent restriction\n"
                "• `/unban <id> [reason]` - Rescind server ban\n"
                "• `/mute <member> <min> <reason>` - Temporary timeout\n"
                "• `/unmute <member>` - Remove active timeout\n\n"
                "### 📑 MANAGEMENT\n"
                "• `/ticketuser add <user>` - Force-create support case\n"
                "──────────────────────────"
            ),
            color=0xe74c3c,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Requires Administrator Permissions", icon_url=bot.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⚙️ Setup", style=discord.ButtonStyle.primary)
    async def setup_btn(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ This menu is session-locked.", ephemeral=True)

        embed = discord.Embed(
            title="⚙️ **SYSTEM CONFIGURATION PANEL**",
            description=(
                "Configure the bot's internal routing and network connectivity.\n"
                "──────────────────────────\n"
                "### 🛰️ NETWORK TARGETING\n"
                "• `/config server_ip` - Minecraft status hook\n"
                "• `/config status_channel` - Live feed output\n\n"
                "### 📂 INTERNAL ROUTING\n"
                "• `/config ticket_category` - Ticket spawn point\n"
                "• `/config ticket_log` - Security audit trail\n"
                "• `/config main_support_role` - Global staff bypass\n"
                "──────────────────────────"
            ),
            color=0x3498db,
            timestamp=datetime.utcnow()
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="📡 Utilities", style=discord.ButtonStyle.success)
    async def info_btn(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message("❌ This menu is session-locked.", ephemeral=True)

        embed = discord.Embed(
            title="📡 **USER UTILITIES & DIAGNOSTICS**",
            description=(
                "General-purpose commands for network players and staff.\n"
                "──────────────────────────\n"
                "• `/ip` - View connection addresses\n"
                "• `/serverstatus` - Lookup external servers\n"
                "• `/ticket` - Contact official support\n"
                "• `/ping` - Latency diagnostics\n"
                "──────────────────────────"
            ),
            color=0x2ecc71,
            timestamp=datetime.utcnow()
        )
        await interaction.response.edit_message(embed=embed, view=self)


@bot.tree.command(name="ping", description="Check the bot's connection latency")
async def ping_slash(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="⚡ Connection Health",
        description=f"Bot Heartbeat: `{latency}ms`",
        color=0x2ecc71 if latency < 100 else 0xf1c40f
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="help", description="Access the Mineleaf Command Hub")
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title="<:ml_logo:1446021531603046410> MINELEAF COMMAND CENTER",
        description=(
            "Welcome to the **Mineleaf Network Command Hub**.\n"
            "Please use the buttons below to navigate between categories.\n\n"
            "**Network Support:** 👋 Open a /ticket\n"
            "**System Heartbeat:** Active and Running"
        ),
        color=0x2ecc71,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="Mineleaf Network • Pro Identity", icon_url=SERVER_ICON_URL)
    embed.set_thumbnail(url=SERVER_ICON_URL)
    
    await interaction.response.send_message(embed=embed, view=HelpPaginationView(interaction.user))


@bot.tree.command(name="ticketlog", description="Set the channel for ticket logs")
@app_commands.describe(channel="The log channel")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_log_shortcut(interaction: discord.Interaction, channel: discord.TextChannel):
    global LOG_CHANNEL_ID
    LOG_CHANNEL_ID = channel.id
    await interaction.response.send_message(f"✅ Ticket log channel set to {channel.mention}", ephemeral=True)


@bot.tree.command(name="ip", description="Shows the server IP address")
async def ip_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title="<:ml_logo:1446021531603046410> Mineleaf Network Connect",
        description=(
            "Join our amazing community on both Java and Bedrock additions!\n\n"
            "> <a:power:1391640355858022560> **Java Edition:** `play.mineleaf.fun`\n"
            "> <a:power:1391640355858022560> **Bedrock Edition:** `play.mineleaf.fun`\n"
            "> <a:power:1391640355858022560> **Bedrock Port:** `19137`\n\n"
            "💡 **Note:** Ensure you use the correct port for Bedrock!"
        ),
        color=0x2ecc71,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text="Mineleaf Network • Connect and Play", icon_url=SERVER_ICON_URL)
    embed.set_thumbnail(url=SERVER_ICON_URL)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="ticket", description="Create a ticket support panel")
@app_commands.checks.has_permissions(administrator=True)
async def ticket_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 MINELEAF TICKET SUPPORT",
        description=(
            "Welcome to MineLeaf Support Center!\n"
            "Please select a suitable type below according to your need 👇\n\n"
            "───────\n\n"
            "**Type:**\n\n"
            "🛠️ **General Support**\n"
            "General inquiries, questions, and assistance\n\n"
            "🔨 **Ban/Unban Report**\n"
            "Appeal bans or report ban-related issues\n\n"
            "💰 **Store**\n"
            "Purchases, donations, ranks, and store support\n\n"
            "🚨 **Report Staff or Member**\n"
            "Report staff members or players for misconduct\n\n"
            "📝 **Staff Application**\n"
            "Apply for a staff position on MineLeaf\n\n"
            "───────\n\n"
            "💙 MineLeaf Support • We're here to help you!\n\n"
            "Powered by Mineleaf"
        ),
        color=0x2B2D31
    )
    embed.set_footer(text="Powered by Mineleaf Infrastructure • Trusted Support", icon_url=SERVER_ICON_URL)
    
    await interaction.response.send_message(embed=embed, view=TicketMenuView())


@bot.tree.command(name="serverstatus", description="Check the status of any Minecraft server")
@app_commands.describe(ip="The server IP address", port="The server port (default 25565)")
async def server_status_slash(interaction: discord.Interaction, ip: str, port: int = 25565):
    await interaction.response.defer()
    
    full_address = f"{ip}:{port}" if port != 25565 else ip
    status_data = await get_minecraft_status(full_address)
    
    if status_data["online"]:
        embed = discord.Embed(
            title="🔍 Server Status Search",
            description=f"Results for **{ip}**",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Status", value="🟢 Online", inline=True)
        embed.add_field(name="Players", value=f"{status_data['players_online']}/{status_data['players_max']}", inline=True)
        embed.add_field(name="Version", value=status_data['version'], inline=True)
        embed.add_field(name="MOTD", value=f"```{status_data['motd']}```", inline=False)
        embed.set_footer(text=f"Latency: {status_data['latency']}ms")
        
        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send(f"❌ Could not reach the server at `{ip}:{port}`. Please verify the IP and Port.")


staff_app_group = app_commands.Group(name="staffapplication", description="Manage staff applications")

@staff_app_group.command(name="open", description="Enable staff applications")
@app_commands.checks.has_permissions(administrator=True)
async def staff_app_open(interaction: discord.Interaction):
    global staff_application_enabled
    staff_application_enabled = True
    
    embed = discord.Embed(
        title="✅ Staff Applications Enabled",
        description="Staff applications are now open! Players can apply for staff positions.",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    await interaction.response.send_message(embed=embed)
    
    if LOG_CHANNEL_ID:
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="📳 Staff Applications Opened",
                description=f"Staff applications have been enabled by {interaction.user.mention}",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            await log_channel.send(embed=log_embed)


@staff_app_group.command(name="off", description="Disable staff applications")
@app_commands.checks.has_permissions(administrator=True)
async def staff_app_off(interaction: discord.Interaction):
    global staff_application_enabled
    staff_application_enabled = False
    
    embed = discord.Embed(
        title="🔒 Staff Applications Disabled",
        description="Staff applications are now closed! Only administrators can open staff application tickets.",
        color=discord.Color.red(),
        timestamp=datetime.utcnow()
    )
    await interaction.response.send_message(embed=embed)
    
    if LOG_CHANNEL_ID:
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            log_embed = discord.Embed(
                title="📳 Staff Applications Closed",
                description=f"Staff applications have been disabled by {interaction.user.mention}",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            await log_channel.send(embed=log_embed)

bot.tree.add_command(staff_app_group)

config_group = app_commands.Group(name="config", description="Bot configuration and setup commands")

@config_group.command(name="ticket_category", description="Set the category for ticket channels")
@app_commands.describe(category="The category channel")
@app_commands.checks.has_permissions(administrator=True)
async def set_category_slash(interaction: discord.Interaction, category: discord.CategoryChannel):
    global TICKET_CATEGORY_ID
    TICKET_CATEGORY_ID = category.id
    await interaction.response.send_message(f"✅ Ticket category set to {category.mention}", ephemeral=True)

@config_group.command(name="main_support_role", description="Set the main support role for all tickets")
@app_commands.describe(role="The support role")
@app_commands.checks.has_permissions(administrator=True)
async def set_main_role_slash(interaction: discord.Interaction, role: discord.Role):
    global SUPPORT_ROLE_ID
    SUPPORT_ROLE_ID = role.id
    await interaction.response.send_message(f"✅ Main support role set to {role.mention}", ephemeral=True)

@config_group.command(name="ticket_log", description="Set the channel for ticket logs")
@app_commands.describe(channel="The log channel")
@app_commands.checks.has_permissions(administrator=True)
async def set_log_slash(interaction: discord.Interaction, channel: discord.TextChannel):
    global LOG_CHANNEL_ID
    LOG_CHANNEL_ID = channel.id
    await interaction.response.send_message(f"✅ Ticket log channel set to {channel.mention}", ephemeral=True)

@config_group.command(name="general_role", description="Set role for General Support tickets")
@app_commands.describe(role="The general support role")
@app_commands.checks.has_permissions(administrator=True)
async def set_general_role_slash(interaction: discord.Interaction, role: discord.Role):
    global GENERAL_ROLE_ID
    GENERAL_ROLE_ID = role.id
    await interaction.response.send_message(f"✅ General support role set to {role.mention}", ephemeral=True)

@config_group.command(name="ban_unban_role", description="Set role for Ban/Unban reports")
@app_commands.describe(role="The ban/unban role")
@app_commands.checks.has_permissions(administrator=True)
async def set_ban_role_slash(interaction: discord.Interaction, role: discord.Role):
    global BAN_UNBAN_ROLE_ID
    BAN_UNBAN_ROLE_ID = role.id
    await interaction.response.send_message(f"✅ Ban/Unban role set to {role.mention}", ephemeral=True)

@config_group.command(name="store_role", description="Set role for Store support")
@app_commands.describe(role="The store role")
@app_commands.checks.has_permissions(administrator=True)
async def set_store_role_slash(interaction: discord.Interaction, role: discord.Role):
    global STORE_ROLE_ID
    STORE_ROLE_ID = role.id
    await interaction.response.send_message(f"✅ Store role set to {role.mention}", ephemeral=True)

@config_group.command(name="report_role", description="Set role for Member/Staff reports")
@app_commands.describe(role="The report role")
@app_commands.checks.has_permissions(administrator=True)
async def set_report_role_slash(interaction: discord.Interaction, role: discord.Role):
    global REPORT_ROLE_ID
    REPORT_ROLE_ID = role.id
    await interaction.response.send_message(f"✅ Report role set to {role.mention}", ephemeral=True)

@config_group.command(name="staff_app_role", description="Set role for Staff Applications")
@app_commands.describe(role="The staff application role")
@app_commands.checks.has_permissions(administrator=True)
async def set_staff_app_role_slash(interaction: discord.Interaction, role: discord.Role):
    global STAFF_APP_ROLE_ID
    STAFF_APP_ROLE_ID = role.id
    await interaction.response.send_message(f"✅ Staff application role set to {role.mention}", ephemeral=True)

@config_group.command(name="server_ip", description="Set the Minecraft server IP for status checks")
@app_commands.describe(ip="The server IP (e.g. play.mineleaf.fun)")
@app_commands.checks.has_permissions(administrator=True)
async def set_ip_slash(interaction: discord.Interaction, ip: str):
    global SERVER_IP
    SERVER_IP = ip
    await interaction.response.send_message(f"✅ Server IP set to `{ip}`", ephemeral=True)

@config_group.command(name="status_channel", description="Set the channel for the auto-updating status embed")
@app_commands.describe(channel="The status channel")
@app_commands.checks.has_permissions(administrator=True)
async def set_status_channel_slash(interaction: discord.Interaction, channel: discord.TextChannel):
    global STATUS_CHANNEL_ID
    STATUS_CHANNEL_ID = channel.id
    await interaction.response.send_message(f"✅ Auto-status channel set to {channel.mention}", ephemeral=True)

@config_group.command(name="view", description="View current bot configuration")
@app_commands.checks.has_permissions(administrator=True)
async def config_view_slash(interaction: discord.Interaction):
    category = interaction.guild.get_channel(TICKET_CATEGORY_ID) if TICKET_CATEGORY_ID else None
    support_role = interaction.guild.get_role(SUPPORT_ROLE_ID) if SUPPORT_ROLE_ID else None
    log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID) if LOG_CHANNEL_ID else None
    status_channel = interaction.guild.get_channel(STATUS_CHANNEL_ID) if STATUS_CHANNEL_ID else None
    
    embed = discord.Embed(
        title="🖥️ SYSTEM CONFIGURATION DASHBOARD",
        description="Current active environment settings for the Mineleaf Network bot.",
        color=0x34495e,
        timestamp=datetime.utcnow()
    )
    
    config_details = (
        f"📂 **Ticket Home:** {category.mention if category else '`NOT SET`'}\n"
        f"📜 **Live Logs:** {log_channel.mention if log_channel else '`NOT SET`'}\n"
        f"📺 **Status Feed:** {status_channel.mention if status_channel else '`NOT SET`'}\n"
        f"🛡️ **Admin Role:** {support_role.mention if support_role else '`NOT SET`'}\n"
        f"🌐 **Server Target:** `{SERVER_IP}`"
    )
    
    embed.add_field(name="⚙️ CORE SETTINGS", value=config_details, inline=False)
    
    # Check permissions as well
    can_manage = interaction.guild.me.guild_permissions.administrator
    status_icon = "🟢" if can_manage else "🔴"
    embed.add_field(name="🛰️ SYSTEM HEALTH", value=f"{status_icon} **Perms:** Admin Access\n🟢 **Status:** Active", inline=True)
    
    embed.set_footer(text="Mineleaf Admin Panel", icon_url=SERVER_ICON_URL)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

bot.tree.add_command(config_group)


@bot.tree.command(name="ticketuser", description="Admin ticket management")
@app_commands.describe(user="The user to create a ticket for", category="Type of ticket", reason="Reason for the ticket")
@app_commands.choices(category=[
    app_commands.Choice(name="General Support", value="General Support"),
    app_commands.Choice(name="Ban/Unban Report", value="Ban/Unban Report"),
    app_commands.Choice(name="Store", value="Store"),
    app_commands.Choice(name="Report Staff or Member", value="Report Staff or Member")
])
@app_commands.checks.has_permissions(administrator=True)
async def ticket_user_add(interaction: discord.Interaction, user: discord.Member, category: app_commands.Choice[str], reason: str):
    await create_ticket(interaction, category.value, reason, target_user=user)


@bot.command(name="serverpanel", aliases=["Ticketpanel", "ticketpanel"])
@commands.has_permissions(administrator=True)
async def server_panel_cmd(ctx):
    embed = discord.Embed(
        title="🎫 MINELEAF TICKET SUPPORT",
        description=(
            "Welcome to MineLeaf Support Center!\n"
            "Please select a suitable type below according to your need 👇\n\n"
            "───────\n\n"
            "**Type:**\n\n"
            "🛠️ **General Support**\n"
            "General inquiries, questions, and assistance\n\n"
            "🔨 **Ban/Unban Report**\n"
            "Appeal bans or report ban-related issues\n\n"
            "💰 **Store**\n"
            "Purchases, donations, ranks, and store support\n\n"
            "🚨 **Report Staff or Member**\n"
            "Report staff members or players for misconduct\n\n"
            "📝 **Staff Application**\n"
            "Apply for a staff position on MineLeaf\n\n"
            "───────\n\n"
            "💙 MineLeaf Support • We're here to help you!\n\n"
            "Powered by Mineleaf"
        ),
        color=0x2B2D31
    )
    embed.set_footer(text="Powered by Mineleaf Infrastructure • Trusted Support", icon_url=SERVER_ICON_URL)
    
    await ctx.send(embed=embed, view=TicketMenuView())


@bot.command(name="serverdaily", aliases=["daily"])
async def server_daily_cmd(ctx):
    status = await get_minecraft_status(SERVER_IP)
    
    if status["online"]:
        embed = discord.Embed(
            title="<:ml_logo:1446021531603046410> Mineleaf Pro Status",
            description=(
                f"👤 **Total Players:** `{status['players_online']}`\n"
                f"📟 **Engine Version:** `{status['version']}`\n\n"
                f"📝 **MOTD:**\n```\n{status['motd']}\n```\n"
                f"🔗 **Server IP:** `play.mineleaf.fun`"
            ),
            color=0x2ecc71,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text="Mineleaf Network • Live Infrastructure", icon_url=SERVER_ICON_URL)
        embed.set_thumbnail(url=SERVER_ICON_URL)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title="<:ml_logo:1446021531603046410> Status Offline",
            description=f"❌ The server `{SERVER_IP}` is currently unreachable.",
            color=0xe74c3c,
            timestamp=datetime.utcnow()
        )
        await ctx.send(embed=embed)


@bot.command(name="store", aliases=["Store"])
async def store_cmd(ctx):
    embed = discord.Embed(
        description=STORE_DESCRIPTION,
        color=0x2ecc71
    )
    embed.set_thumbnail(url=STORE_THUMBNAIL_URL)

    await ctx.send(embed=embed, view=StoreTicketView())


@bot.command(name="vote", aliases=["Vote"])
async def vote_cmd(ctx):
    embed = discord.Embed(
        title=f"{VOTE_EMOJI} Mineleaf Vote",
        description=(
            "Help us grow the network — vote for **Mineleaf** every day!\n\n"
            "Click the button below to head to our official voting site."
        ),
        color=0x2ecc71,
        timestamp=datetime.utcnow()
    )
    embed.set_thumbnail(url=SERVER_ICON_URL)
    embed.set_footer(text="Mineleaf Network • Vote Daily!", icon_url=SERVER_ICON_URL)

    view = View()
    vote_button = Button(label="Vote Now", emoji="🗳️", style=discord.ButtonStyle.link, url=VOTE_URL)
    view.add_item(vote_button)

    await ctx.send(embed=embed, view=view)


@tasks.loop(seconds=30)
async def update_server_status():
    channel = bot.get_channel(STATUS_CHANNEL_ID)
    if not channel:
        return
    
    status = await get_minecraft_status(SERVER_IP)
    
    embed = discord.Embed(
        title="🟢 **NETWORK STATUS • ONLINE**" if status["online"] else "🔴 **NETWORK STATUS • OFFLINE**",
        color=0x2ecc71 if status["online"] else 0xe74c3c,
        timestamp=datetime.utcnow()
    )
    
    icon_url = bot.user.display_avatar.url

    if status["online"]:
        embed.description = (
            f"### {SERVER_IP}\n"
            f"> {status['motd']}\n\n"
            "**📡 REAL-TIME INFRASTRUCTURE**"
        )
        embed.add_field(name="👥 Population", value=f"`{status['players_online']} / {status['players_max']}`", inline=True)
        embed.add_field(name="🛠️ Engine", value=f"`{status['version']}`", inline=True)
        embed.add_field(name="🛰️ Latency", value="`STABLE`", inline=True)
        
        embed.set_footer(text="Live Sync: Active • 30s Heartbeat", icon_url=icon_url)
    else:
        embed.description = (
            f"### {SERVER_IP}\n"
            "❌ **Connectivity Lost**: The server is currently unreachable.\n"
            "Possible causes: *Scheduled Maintenance* or *Network Congestion*."
        )
        embed.set_footer(text="Monitoring: Active • Attempting Reconnection", icon_url=icon_url)

    embed.set_thumbnail(url=SERVER_ICON_URL)

    # Try to find last message to edit in the specified channel
    try:
        last_msg = None
        async for msg in channel.history(limit=100): # Increased limit to 100 to avoid duplicates
            if msg.author == bot.user and msg.embeds:
                # Be more inclusive with status searches
                if "NETWORK STATUS" in msg.embeds[0].title:
                    last_msg = msg
                    break
        
        if last_msg:
            await last_msg.edit(embed=embed)
        else:
            await channel.send(embed=embed)
    except Exception as e:
        print(f"Error updating status message: {e}")


# Minecraft Server Status Helper
async def get_minecraft_status(server_address: str):
    """
    Fetches the live status of a Minecraft server using mcsrvstat.us API.
    Returns a dictionary with status details or None if offline.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.mcsrvstat.us/2/{server_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("online"):
                        return {
                            "online": True,
                            "players_online": data["players"]["online"],
                            "players_max": data["players"]["max"],
                            "motd": " ".join(data["motd"]["clean"]) if "motd" in data else "No MOTD",
                            "version": data.get("version", "Unknown"),
                            "latency": "N/A" # API doesn't provide direct latency from bot to server
                        }
        return {"online": False}
    except Exception as e:
        print(f"Error fetching Minecraft status: {e}")
        return {"online": False}


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.author.guild_permissions.administrator:
        await bot.process_commands(message)
        return
    
    content_lower = message.content.lower()
    
    for bad_word in BAD_WORDS:
        if bad_word in content_lower:
            try:
                await message.delete()
                warning_msg = await message.channel.send(f"❌ {message.author.mention}, your message was deleted for containing inappropriate language!")
                await asyncio.sleep(5)
                await warning_msg.delete()
            except:
                pass
            return
    
    if URL_PATTERN.search(message.content):
        try:
            await message.delete()
            warning_msg = await message.channel.send(f"❌ {message.author.mention}, links are not allowed in this server!")
            await asyncio.sleep(5)
            await warning_msg.delete()
        except:
            pass 
        return
    
    await bot.process_commands(message)


bot.run(os.getenv('DISCORD_TOKEN'))
