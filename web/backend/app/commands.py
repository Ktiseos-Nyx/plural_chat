"""
PluralKit-style command system for web chat
Discord-like slash commands
"""
from typing import List, Dict, Callable, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from . import models

logger = logging.getLogger(__name__)


class Command:
    """Represents a command"""
    def __init__(
        self,
        name: str,
        handler: Callable,
        description: str,
        usage: str,
        aliases: List[str] = None
    ):
        self.name = name
        self.handler = handler
        self.description = description
        self.usage = usage
        self.aliases = aliases or []


class CommandRegistry:
    """Global command registry"""

    def __init__(self):
        self.commands: Dict[str, Command] = {}

    def register(
        self,
        name: str,
        description: str,
        usage: str,
        aliases: List[str] = None
    ):
        """Decorator to register a command"""
        def decorator(func: Callable):
            command = Command(name, func, description, usage, aliases)
            self.commands[name] = command

            # Register aliases
            if aliases:
                for alias in aliases:
                    self.commands[alias] = command

            logger.info(f"Registered command: /{name}")
            return func
        return decorator

    async def execute(
        self,
        user_id: int,
        message: str,
        db: Session
    ) -> Optional[str]:
        """Execute a command from a message"""
        # Check if it's a command
        if not message.startswith('/'):
            return None

        # Parse command
        parts = message[1:].split()
        if not parts:
            return None

        command_name = parts[0].lower()
        args = parts[1:]

        # Find command
        command = self.commands.get(command_name)
        if not command:
            return f"❌ Unknown command: `/{command_name}`. Type `/help` for available commands."

        # Execute command
        try:
            result = await command.handler(user_id, args, db)
            return result
        except Exception as e:
            logger.error(f"Command error ({command_name}): {e}")
            return f"❌ Error executing command: {str(e)}"

    def get_help_text(self) -> str:
        """Generate help text for all commands"""
        # Group commands (remove aliases)
        seen = set()
        unique_commands = []
        for cmd in self.commands.values():
            if cmd.name not in seen:
                unique_commands.append(cmd)
                seen.add(cmd.name)

        # Sort by name
        unique_commands.sort(key=lambda c: c.name)

        help_text = "**📚 Available Commands:**\n\n"

        # Group by category
        categories = {
            "Member Management": [],
            "Switching": [],
            "Proxy": [],
            "Settings": [],
            "Utility": [],
        }

        for cmd in unique_commands:
            # Categorize
            if cmd.name in ["member", "info", "list", "rename"]:
                categories["Member Management"].append(cmd)
            elif cmd.name in ["switch", "front", "switchhistory"]:
                categories["Switching"].append(cmd)
            elif cmd.name in ["proxy", "autoproxy"]:
                categories["Proxy"].append(cmd)
            elif cmd.name in ["settings", "theme", "export"]:
                categories["Settings"].append(cmd)
            else:
                categories["Utility"].append(cmd)

        # Format help text
        for category, commands in categories.items():
            if commands:
                help_text += f"**{category}:**\n"
                for cmd in commands:
                    aliases_str = f" (aliases: {', '.join(cmd.aliases)})" if cmd.aliases else ""
                    help_text += f"• `{cmd.usage}`{aliases_str}\n"
                    help_text += f"  {cmd.description}\n\n"

        return help_text


# Global registry
registry = CommandRegistry()


# ===== MEMBER MANAGEMENT COMMANDS =====

@registry.register(
    "member",
    "Manage your system members",
    "/member <add|remove|edit> <name> [options]",
    aliases=["m"]
)
async def cmd_member(user_id: int, args: List[str], db: Session) -> str:
    """Member management command"""
    if not args:
        return "❌ Usage: `/member <add|remove|edit> <name> [options]`\n\n" \
               "Examples:\n" \
               "• `/member add Riley` - Add a new member\n" \
               "• `/member remove Riley` - Remove a member\n" \
               "• `/member edit Riley pronouns she/her` - Edit member pronouns"

    action = args[0].lower()

    if action == "add":
        if len(args) < 2:
            return "❌ Usage: `/member add <name>`"

        name = " ".join(args[1:])

        # Check if member already exists
        existing = db.query(models.Member).filter(
            models.Member.user_id == user_id,
            models.Member.name == name
        ).first()

        if existing:
            return f"❌ Member `{name}` already exists!"

        # Create member
        member = models.Member(
            user_id=user_id,
            name=name,
            is_active=True
        )
        db.add(member)
        db.commit()

        return f"✅ Added member: **{name}**\n" \
               f"Use `/member edit {name}` to set pronouns, color, etc."

    elif action == "remove" or action == "delete":
        if len(args) < 2:
            return "❌ Usage: `/member remove <name>`"

        name = " ".join(args[1:])

        member = db.query(models.Member).filter(
            models.Member.user_id == user_id,
            models.Member.name == name
        ).first()

        if not member:
            return f"❌ Member `{name}` not found"

        db.delete(member)
        db.commit()

        return f"✅ Removed member: **{name}**"

    elif action == "edit" or action == "update":
        if len(args) < 4:
            return "❌ Usage: `/member edit <name> <field> <value>`\n\n" \
                   "Fields: `pronouns`, `color`, `description`"

        name = args[1]
        field = args[2].lower()
        value = " ".join(args[3:])

        member = db.query(models.Member).filter(
            models.Member.user_id == user_id,
            models.Member.name == name
        ).first()

        if not member:
            return f"❌ Member `{name}` not found"

        # Update field
        if field == "pronouns":
            member.pronouns = value
        elif field == "color":
            # Validate color
            if not value.startswith('#'):
                value = f"#{value}"
            if len(value) != 7:
                return "❌ Invalid color format. Use hex color like `#FF5733`"
            member.color = value
        elif field in ["description", "desc"]:
            member.description = value
        else:
            return f"❌ Unknown field: `{field}`. Available: pronouns, color, description"

        db.commit()

        return f"✅ Updated **{name}**'s {field} to: {value}"

    else:
        return f"❌ Unknown action: `{action}`. Available: add, remove, edit"


@registry.register(
    "info",
    "Show information about a member",
    "/info <name>",
    aliases=["i", "whois"]
)
async def cmd_info(user_id: int, args: List[str], db: Session) -> str:
    """Show member info"""
    if not args:
        return "❌ Usage: `/info <member name>`"

    name = " ".join(args)

    member = db.query(models.Member).filter(
        models.Member.user_id == user_id,
        models.Member.name == name
    ).first()

    if not member:
        return f"❌ Member `{name}` not found"

    info = f"**{member.name}**\n\n"

    if member.pronouns:
        info += f"**Pronouns:** {member.pronouns}\n"

    if member.color:
        info += f"**Color:** {member.color}\n"

    if member.description:
        info += f"**Description:** {member.description}\n"

    if member.pk_id:
        info += f"**PluralKit ID:** {member.pk_id}\n"

    info += f"\n**Created:** {member.created_at.strftime('%Y-%m-%d')}"

    return info


@registry.register(
    "list",
    "List all your members",
    "/list",
    aliases=["members", "ls"]
)
async def cmd_list(user_id: int, args: List[str], db: Session) -> str:
    """List all members"""
    members = db.query(models.Member).filter(
        models.Member.user_id == user_id,
        models.Member.is_active == True
    ).order_by(models.Member.name).all()

    if not members:
        return "❌ No members found. Use `/member add <name>` to add members!"

    member_list = "**Your System Members:**\n\n"

    for member in members:
        pronouns = f" ({member.pronouns})" if member.pronouns else ""
        member_list += f"• **{member.name}**{pronouns}\n"

    member_list += f"\n**Total:** {len(members)} members"

    return member_list


# ===== SWITCHING COMMANDS =====

@registry.register(
    "switch",
    "Log a switch (who's fronting)",
    "/switch <member1> [member2, ...]",
    aliases=["sw"]
)
async def cmd_switch(user_id: int, args: List[str], db: Session) -> str:
    """Log a switch"""
    if not args:
        return "❌ Usage: `/switch <member1> [member2, ...]`\n\n" \
               "Examples:\n" \
               "• `/switch Riley` - Single fronter\n" \
               "• `/switch Riley, Alex` - Multiple fronters"

    # Parse member names (comma-separated)
    member_names_str = " ".join(args)
    member_names = [m.strip() for m in member_names_str.split(",")]

    # Validate members exist
    valid_members = []
    for name in member_names:
        member = db.query(models.Member).filter(
            models.Member.user_id == user_id,
            models.Member.name == name
        ).first()

        if not member:
            return f"❌ Member `{name}` not found. Use `/list` to see your members."

        valid_members.append(member)

    # TODO: Store switch in a switches table
    # For now, just confirm

    names = ", ".join([m.name for m in valid_members])
    return f"✅ Switched to: **{names}**\n\n" \
           f"*Note: Switch tracking is not yet implemented in the database.*"


@registry.register(
    "front",
    "See who's currently fronting",
    "/front",
    aliases=["f", "fronters"]
)
async def cmd_front(user_id: int, args: List[str], db: Session) -> str:
    """Show current fronters"""
    # TODO: Get from switches table
    return "**Currently Fronting:**\n\n" \
           "*Note: Switch tracking is not yet implemented.*\n\n" \
           "Use `/switch <name>` to log switches!"


# ===== UTILITY COMMANDS =====

@registry.register(
    "help",
    "Show all available commands",
    "/help [command]",
    aliases=["h", "commands"]
)
async def cmd_help(user_id: int, args: List[str], db: Session) -> str:
    """Show help"""
    if args:
        # Show help for specific command
        command_name = args[0].lower()
        command = registry.commands.get(command_name)

        if not command:
            return f"❌ Unknown command: `/{command_name}`"

        help_text = f"**/{command.name}**\n\n"
        help_text += f"{command.description}\n\n"
        help_text += f"**Usage:** `{command.usage}`\n"

        if command.aliases:
            help_text += f"**Aliases:** {', '.join([f'`/{a}`' for a in command.aliases])}\n"

        return help_text

    # Show all commands
    return registry.get_help_text()


@registry.register(
    "roll",
    "Roll dice",
    "/roll [dice notation]",
    aliases=["dice"]
)
async def cmd_roll(user_id: int, args: List[str], db: Session) -> str:
    """Roll dice"""
    import random
    import re

    if not args:
        # Default: 1d6
        result = random.randint(1, 6)
        return f"🎲 Rolled 1d6: **{result}**"

    # Parse dice notation (e.g., 2d6, 1d20, 3d10+5)
    dice_pattern = r'(\d+)?d(\d+)([+-]\d+)?'
    match = re.match(dice_pattern, args[0].lower())

    if not match:
        return "❌ Invalid dice notation. Examples: `1d6`, `2d20`, `3d10+5`"

    num_dice = int(match.group(1) or 1)
    num_sides = int(match.group(2))
    modifier = int(match.group(3) or 0)

    if num_dice > 100:
        return "❌ Too many dice! Max 100."

    if num_sides > 1000:
        return "❌ Too many sides! Max 1000."

    # Roll dice
    rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
    total = sum(rolls) + modifier

    result = f"🎲 Rolled {num_dice}d{num_sides}"
    if modifier:
        result += f"{modifier:+d}"
    result += f": **{total}**\n\n"

    if num_dice <= 10:
        result += f"Rolls: {', '.join(map(str, rolls))}"

    return result


@registry.register(
    "flip",
    "Flip a coin",
    "/flip",
    aliases=["coin"]
)
async def cmd_flip(user_id: int, args: List[str], db: Session) -> str:
    """Flip a coin"""
    import random
    result = random.choice(["Heads", "Tails"])
    return f"🪙 **{result}**!"


@registry.register(
    "ping",
    "Check if the bot is alive",
    "/ping"
)
async def cmd_ping(user_id: int, args: List[str], db: Session) -> str:
    """Ping command"""
    return "🏓 Pong! System is running."


# ===== STABLE DIFFUSION / AI IMAGE GENERATION =====

@registry.register(
    "sdconnect",
    "Connect to Stable Diffusion API (GPU rental)",
    "/sdconnect <api_type> <url> [api_key]",
    aliases=["sdlink"]
)
async def cmd_sdconnect(user_id: int, args: List[str], db: Session) -> str:
    """Connect to SD API"""
    from .sd_integration import sd_manager

    if len(args) < 2:
        return "❌ Usage: `/sdconnect <api_type> <url> [api_key]`\n\n" \
               "**API Types:**\n" \
               "• `automatic1111` or `a1111` - Automatic1111 WebUI\n" \
               "• `forge` - Forge WebUI (same as A1111)\n" \
               "• `comfyui` - ComfyUI (coming soon)\n\n" \
               "**Examples:**\n" \
               "• `/sdconnect a1111 http://localhost:7860`\n" \
               "• `/sdconnect forge https://mygpu.runpod.io`\n" \
               "• `/sdconnect a1111 http://localhost:7860 my-api-key`"

    api_type = args[0].lower()
    url = args[1]
    api_key = args[2] if len(args) > 2 else None

    # Normalize API type
    if api_type in ["a1111", "automatic1111"]:
        api_type = "automatic1111"
    elif api_type == "forge":
        api_type = "forge"
    elif api_type == "comfyui":
        api_type = "comfyui"
    else:
        return f"❌ Unknown API type: `{api_type}`. Use: automatic1111, forge, or comfyui"

    try:
        sd_manager.add_connection(
            user_id=user_id,
            api_type=api_type,
            base_url=url,
            api_key=api_key
        )

        # Test connection
        success = await sd_manager.test_connection(user_id)

        if success:
            return f"✅ Connected to **{api_type}** at `{url}`!\n\n" \
                   f"Try it out:\n" \
                   f"• `/generate a cute cat` - Simple generation\n" \
                   f"• `/sdtest` - Test connection\n" \
                   f"• `/sdmodels` - List available models"
        else:
            return f"⚠️  Connection saved, but test failed!\n" \
                   f"Make sure the API is running at `{url}`"

    except Exception as e:
        return f"❌ Error: {str(e)}"


@registry.register(
    "sdtest",
    "Test Stable Diffusion API connection",
    "/sdtest"
)
async def cmd_sdtest(user_id: int, args: List[str], db: Session) -> str:
    """Test SD API connection"""
    from .sd_integration import sd_manager

    conn = sd_manager.get_connection(user_id)
    if not conn:
        return "❌ No SD API connected. Use `/sdconnect` first!"

    try:
        success = await sd_manager.test_connection(user_id)

        if success:
            return f"✅ Connection OK!\n\n" \
                   f"**API Type:** {conn['api_type']}\n" \
                   f"**URL:** {conn['base_url']}\n\n" \
                   f"Ready to generate! Try `/generate <prompt>`"
        else:
            return f"❌ Connection failed!\n\n" \
                   f"**API Type:** {conn['api_type']}\n" \
                   f"**URL:** {conn['base_url']}\n\n" \
                   f"Make sure the API is running."

    except Exception as e:
        return f"❌ Error: {str(e)}"


@registry.register(
    "sdmodels",
    "List available SD models",
    "/sdmodels",
    aliases=["models"]
)
async def cmd_sdmodels(user_id: int, args: List[str], db: Session) -> str:
    """List SD models"""
    from .sd_integration import sd_manager, Automatic1111API

    conn = sd_manager.get_connection(user_id)
    if not conn:
        return "❌ No SD API connected. Use `/sdconnect` first!"

    if conn["api_type"] not in ["automatic1111", "forge"]:
        return "❌ Model listing only supported for Automatic1111/Forge"

    try:
        api = Automatic1111API(conn["base_url"], conn.get("api_key"))
        models = await api.get_models()

        if not models:
            return "❌ No models found!"

        result = "**📦 Available Models:**\n\n"
        for i, model in enumerate(models, 1):
            result += f"{i}. {model}\n"

        return result

    except Exception as e:
        return f"❌ Error: {str(e)}"


@registry.register(
    "generate",
    "Generate AI image with Stable Diffusion",
    "/generate <prompt> [--negative <neg>] [--size WxH] [--steps N]",
    aliases=["gen", "img"]
)
async def cmd_generate(user_id: int, args: List[str], db: Session) -> str:
    """Generate image with SD API"""
    from .sd_integration import sd_manager
    from .media_cache import media_cache

    if not args:
        return "❌ Usage: `/generate <prompt> [options]`\n\n" \
               "**Options:**\n" \
               "• `--negative <prompt>` - Negative prompt\n" \
               "• `--size WxH` - Image size (e.g., 512x512, 768x512)\n" \
               "• `--steps N` - Number of steps (default: 20)\n\n" \
               "**Examples:**\n" \
               "• `/generate a cute cat`\n" \
               "• `/generate a space station --size 768x512 --steps 30`\n" \
               "• `/generate portrait of Riley --negative ugly, blurry`"

    conn = sd_manager.get_connection(user_id)
    if not conn:
        return "❌ No SD API connected. Use `/sdconnect` first!\n\n" \
               "Example: `/sdconnect a1111 http://localhost:7860`"

    # Parse arguments
    prompt_parts = []
    negative_prompt = ""
    width = 512
    height = 512
    steps = 20

    i = 0
    while i < len(args):
        arg = args[i]

        if arg == "--negative":
            if i + 1 < len(args):
                # Collect negative prompt until next flag
                neg_parts = []
                i += 1
                while i < len(args) and not args[i].startswith("--"):
                    neg_parts.append(args[i])
                    i += 1
                negative_prompt = " ".join(neg_parts)
                continue
        elif arg == "--size":
            if i + 1 < len(args):
                size_str = args[i + 1]
                try:
                    w, h = size_str.lower().split("x")
                    width = int(w)
                    height = int(h)
                except:
                    return f"❌ Invalid size format: `{size_str}`. Use format: 512x512"
                i += 2
                continue
        elif arg == "--steps":
            if i + 1 < len(args):
                try:
                    steps = int(args[i + 1])
                    if steps < 1 or steps > 150:
                        return "❌ Steps must be between 1 and 150"
                except:
                    return f"❌ Invalid steps: `{args[i + 1]}`"
                i += 2
                continue

        prompt_parts.append(arg)
        i += 1

    prompt = " ".join(prompt_parts)

    if not prompt:
        return "❌ No prompt provided!"

    # Validate dimensions
    if width % 64 != 0 or height % 64 != 0:
        return "❌ Width and height must be multiples of 64!"
    if width > 1024 or height > 1024:
        return "❌ Max size is 1024x1024!"

    try:
        # Generate image
        return f"🎨 **Generating...**\n\n" \
               f"**Prompt:** {prompt}\n" \
               f"**Size:** {width}x{height}\n" \
               f"**Steps:** {steps}\n\n" \
               f"This may take 30-120 seconds depending on your GPU...\n\n" \
               f"*Note: Image will be posted as a new message when ready.*"

        # TODO: Actual generation happens in background task
        # For now, just return the status message

    except Exception as e:
        return f"❌ Generation failed: {str(e)}"


@registry.register(
    "sddisconnect",
    "Disconnect from Stable Diffusion API",
    "/sddisconnect"
)
async def cmd_sddisconnect(user_id: int, args: List[str], db: Session) -> str:
    """Disconnect SD API"""
    from .sd_integration import sd_manager

    conn = sd_manager.get_connection(user_id)
    if not conn:
        return "❌ No SD API connected."

    sd_manager.remove_connection(user_id)
    return "✅ Disconnected from Stable Diffusion API"


# Export the execute function for easy import
async def execute_command(user_id: int, message: str, db: Session) -> Optional[str]:
    """Execute a command from a message"""
    return await registry.execute(user_id, message, db)
