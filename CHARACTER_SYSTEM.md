# 🎭 Character System Guide

**TL;DR: Create as many characters/personas as you want! No PluralKit required!**

---

## 🌟 What Is This?

Plural Chat lets you create **multiple chat personas** - like having different accounts, but in one app!

**Perfect for:**
- 🎭 **Roleplayers** - Different characters for different stories
- ✍️ **Writers** - Develop characters through conversation
- 🎮 **Gamers** - Different personas for different games
- 👥 **Plural Systems** - System members (with optional PluralKit sync)
- 🎨 **Anyone** - Just want multiple chat profiles!

**Think of it like:**
- Old MSN Messenger with multiple accounts
- Forum roleplay with character sheets
- Discord but each "member" is a profile you control

---

## 🚀 Quick Start - Create Your First Character

### Method 1: Via API (For Developers)

```bash
POST /members
{
  "name": "Alex the Wizard",
  "pronouns": "he/him",
  "description": "A wise wizard from the northern mountains",
  "color": "#4A90E2",
  "avatar_path": "/avatars/alex_wizard.png"
}
```

### Method 2: Via Commands (In Chat)

```
/member create Alex the Wizard
/member edit Alex pronouns he/him
/member edit Alex color #4A90E2
/member edit Alex description "A wise wizard from the northern mountains"
```

### Method 3: Via Frontend (Coming Soon!)

The Lobe UI frontend will have a character creation form!

---

## 📋 Character Profile Fields

Every character can have:

| Field | Description | Required | Example |
|-------|-------------|----------|---------|
| **name** | Character name | ✅ Yes | "Alex the Wizard" |
| **pronouns** | Pronouns | ❌ No | "he/him", "she/her", "they/them" |
| **description** | Bio/backstory | ❌ No | "A wise wizard from..." |
| **color** | Hex color for messages | ❌ No | "#4A90E2" (blue) |
| **avatar_path** | Profile picture | ❌ No | "/avatars/alex.png" |
| **proxy_tags** | Auto-switch triggers | ❌ No | "alex:", "a:" |

**All fields are optional except name!** Start simple, add details later.

---

## 🎨 Example Character Profiles

### Roleplayer Example

```json
{
  "name": "Luna Starweaver",
  "pronouns": "she/her",
  "description": "Elven mage, specializes in astral magic. Age 847.",
  "color": "#9B59B6",
  "proxy_tags": "luna:"
}
```

```json
{
  "name": "Grunk Ironfist",
  "pronouns": "he/him",
  "description": "Dwarf warrior, loves ale and axes. Not very bright.",
  "color": "#E67E22",
  "proxy_tags": "grunk:"
}
```

### Writer Example

```json
{
  "name": "Detective Sarah Chen",
  "pronouns": "she/her",
  "description": "Hard-boiled detective with a secret past",
  "color": "#34495E"
}
```

```json
{
  "name": "The Mysterious Stranger",
  "pronouns": "they/them",
  "description": "No one knows their true identity...",
  "color": "#2C3E50"
}
```

### Solo User Example

```json
{
  "name": "Work Me",
  "pronouns": "she/her",
  "description": "Professional mode engaged",
  "color": "#3498DB"
}
```

```json
{
  "name": "Chaos Goblin Me",
  "pronouns": "they/them",
  "description": "3am thoughts only",
  "color": "#E74C3C"
}
```

---

## 🔄 Switching Between Characters

### In Chat

```
/switch Luna Starweaver
→ Now chatting as Luna!

/switch Grunk
→ Now chatting as Grunk Ironfist!
```

### With Proxy Tags (Auto-Switch)

If you set proxy tags, just type them:

```
luna: Hello there!
→ Auto-switches to Luna and sends "Hello there!"

grunk: GRUNK SMASH!
→ Auto-switches to Grunk and sends "GRUNK SMASH!"
```

### Via Frontend

Click character avatar → Instant switch!

---

## 📚 Managing Your Characters

### List All Characters

```
/member list
→ Shows all your characters

GET /members
→ Returns JSON array of all characters
```

### View Character Details

```
/member info Luna
→ Shows Luna's full profile

GET /members/{id}
→ Returns character JSON
```

### Update Character

```
/member edit Luna color #FF69B4
/member edit Luna description "Now she's REALLY magical"

PATCH /members/{id}
{
  "color": "#FF69B4",
  "description": "Now she's REALLY magical"
}
```

### Delete Character

```
/member delete Luna
→ ⚠️ Permanent! Are you sure?

DELETE /members/{id}
→ Permanently removes character
```

---

## 🔗 Optional: Import from PluralKit

**Have a PluralKit system? Import it!**

### Via API

```bash
POST /pluralkit/sync
{
  "pk_token": "your_pk_token_here"
}
```

### What Gets Imported

✅ All system members
✅ Names, pronouns, descriptions
✅ Colors
✅ Avatar URLs
✅ Proxy tags

### After Import

You can:
- Edit imported characters
- Add new characters manually
- Delete characters you don't want
- Keep PluralKit and Plural Chat in sync OR manage separately

**PluralKit is 100% optional!** You never need to use it if you don't want to.

---

## 💡 Creative Use Cases

### 1. Character Development (Writers)

Create characters and have conversations between them:

```
/switch Sarah Chen
sarah: I know you're hiding something.

/switch The Stranger
stranger: Everyone has secrets, detective.

sarah: Not like this. What happened that night?
```

**Perfect for:**
- Testing dialogue
- Developing character voices
- Exploring relationships
- Writing exercises

### 2. Mood-Based Personas

Different you's for different moods:

```json
[
  {"name": "Morning Me", "color": "#FFD700"},
  {"name": "Productive Me", "color": "#2ECC71"},
  {"name": "Tired Me", "color": "#95A5A6"},
  {"name": "Chaotic Me", "color": "#E74C3C"}
]
```

### 3. Role-Based Profiles

Different roles you play:

```json
[
  {"name": "Professional [Your Name]", "description": "Work mode"},
  {"name": "Casual [Your Name]", "description": "Friend mode"},
  {"name": "Creative [Your Name]", "description": "Art mode"}
]
```

### 4. Tabletop RPG Characters

All your D&D characters in one place:

```json
[
  {"name": "Thorn Shadowstep", "description": "Rogue, Campaign 1"},
  {"name": "Brother Aldric", "description": "Cleric, Campaign 2"},
  {"name": "Zyx the Unknowable", "description": "Warlock, One-shot"}
]
```

### 5. Fictional Universe Building

Characters from your universe:

```json
[
  {"name": "Captain Rivera", "description": "Starship commander"},
  {"name": "Dr. Okonkwo", "description": "Chief medical officer"},
  {"name": "Ensign Park", "description": "Communications"}
]
```

---

## 🎯 Best Practices

### Naming

✅ **Good names:**
- Clear and recognizable
- Unique within your profiles
- Match the character vibe

❌ **Avoid:**
- Names too similar (Luna/Lunar/Lunara gets confusing)
- Just numbers (Character1, Character2)
- Super long names (hard to type in commands)

### Colors

**Pick distinct colors** so messages are easy to tell apart!

**Good color combos:**
- Blue (#3498DB) and Orange (#E67E22)
- Purple (#9B59B6) and Green (#2ECC71)
- Red (#E74C3C) and Cyan (#1ABC9C)

**Avoid:**
- Similar colors (#3498DB and #5DADE2 - too close!)
- Pure black/white (hard to read)

### Proxy Tags

**Keep them short and memorable:**

✅ Good: `luna:`, `l:`, `🌙:`
❌ Bad: `lunathewizard:`, `character1:`

**Make them unique:**
- Don't overlap (if one is `l:`, another can't be `lu:`)

### Organization

**Name your characters consistently:**

**By Universe:**
- `[SW] Luke Skywalker`
- `[SW] Darth Vader`
- `[ST] Captain Kirk`

**By Type:**
- `RP: Luna Starweaver`
- `OC: Detective Chen`
- `Me: Professional`

---

## ❓ FAQ

**Q: Do I need PluralKit to use this?**
A: **NO!** PluralKit is 100% optional. Create characters manually!

**Q: How many characters can I have?**
A: As many as you want! No limits.

**Q: Can I use this for roleplay?**
A: Absolutely! That's a perfect use case!

**Q: Can I share characters with friends?**
A: Not yet, but character export/import is planned!

**Q: Can I have different characters for different chats?**
A: Currently all characters are global to your account. Per-chat characters may come later!

**Q: Do characters work with AI image generation?**
A: Yes! Generate character portraits with `/generate portrait of [character name]`

**Q: Can I import from Tupperbox/other bots?**
A: Not yet, but if there's demand we can add it!

**Q: Is this like Discord's PluralKit bot?**
A: Similar concept, but **you own your data** and **no Discord required**!

---

## 🔧 Technical Details

### Database Schema

```python
class Member(Base):
    id: int                          # Unique ID
    user_id: int                     # Your account ID
    name: str                        # Character name
    pronouns: Optional[str]          # Pronouns
    color: Optional[str]             # Hex color
    avatar_path: Optional[str]       # Avatar image
    description: Optional[str]       # Bio/description
    pk_id: Optional[str]             # PK member ID (if imported)
    proxy_tags: Optional[str]        # JSON: [{"prefix": "luna:", "suffix": ""}]
    is_active: bool                  # Active/archived
    created_at: datetime             # Creation timestamp
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /members | List all your characters |
| POST | /members | Create new character |
| GET | /members/{id} | Get character details |
| PATCH | /members/{id} | Update character |
| DELETE | /members/{id} | Delete character |

### Commands

| Command | Description |
|---------|-------------|
| `/member list` | List all characters |
| `/member info <name>` | Character details |
| `/member create <name>` | Create character |
| `/member edit <name> <field> <value>` | Update character |
| `/member delete <name>` | Delete character |
| `/switch <name>` | Switch to character |

---

## 🎨 Coming Soon

**Planned features:**
- [ ] Visual character creation form in frontend
- [ ] Character portraits / avatar upload
- [ ] Export/import character profiles (JSON)
- [ ] Character templates (quick create from template)
- [ ] Character groups/categories
- [ ] Per-chat character selection
- [ ] Character statistics (message count, etc.)
- [ ] Import from Tupperbox, SimplyPlural, etc.

---

## 💬 Community Ideas

**Want to share cool character setups?**

Post in [GitHub Discussions](https://github.com/Ktiseos-Nyx/plural_chat/discussions) with:
- Character themes
- Creative use cases
- Color schemes
- Proxy tag ideas

---

*Remember: There's no "right way" to use this! Make it yours!* 🌈

**Next Steps:**
1. Create your first character
2. Chat as them!
3. Add more characters
4. Have fun!
