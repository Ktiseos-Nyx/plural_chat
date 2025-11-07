# 🤖 AI Characters Guide

Add AI-powered characters to your chat! Create chatbots, roleplay partners, writing assistants, or just someone to talk to.

## 🚀 Quick Start

```bash
# Create an AI assistant with Gemini (FREE!)
/ai create Assistant gemini YOUR_API_KEY "You are a helpful assistant"

# Chat with them
@Assistant what's the capital of France?

# Or just mention them
Assistant: how are you today?
```

That's it! Your AI character will respond automatically!

---

## 📋 Supported LLM Providers

| Provider | Cost | Best For | Model Options |
|----------|------|----------|---------------|
| **Google Gemini** | FREE tier! | General use, roleplay | `gemini-pro`, `gemini-1.5-flash` |
| **Ollama** | 100% FREE | Privacy, local | `llama2`, `mistral`, `codellama` |
| **OpenAI** | $0.03/1k tokens | Quality responses | `gpt-3.5-turbo`, `gpt-4` |
| **Anthropic Claude** | $0.25/M tokens | Writing, analysis | `claude-3-haiku`, `claude-3-sonnet` |

---

## 🎯 Commands

### Create AI Character

```bash
/ai create <name> <provider> <api_key> [personality]
```

**Examples:**

```bash
# Helpful assistant
/ai create Helper gemini sk-xxx "You are a friendly coding assistant"

# Roleplay character
/ai create Luna gemini sk-xxx "You are Luna, a wise elven wizard who speaks poetically"

# Writing partner
/ai create Writer openai sk-xxx "You help develop character backstories and plot ideas"

# Local AI (no API key needed!)
/ai create LocalBot ollama none "You are a helpful assistant"
```

### Configure AI Character

```bash
# Change personality
/ai configure Luna personality "You are Luna, now a chaotic goblin wizard"

# Change model
/ai configure Helper model gemini-1.5-flash

# Update API key
/ai configure Helper apikey sk-new-key-here
```

### Control AI

```bash
# Toggle AI on/off
/ai toggle Helper

# Test AI response
/ai test Helper explain quantum physics
```

### Get Help

```bash
/ai
# Shows all available commands
```

---

## 💬 Chatting with AI Characters

### Method 1: Mention with @

```
You: @Assistant what's the weather like today?
Assistant: I don't have access to real-time weather...

You: @Luna what do you see in the crystal ball?
Luna: *gazes into the swirling mists* I see... potential, young one...
```

### Method 2: Start message with name

```
You: Assistant: help me debug this code
Assistant: I'd be happy to help! What's the issue...

You: Luna what spell should I use?
Luna: Ah, for such a task, I would recommend...
```

Both work! AI responds automatically when mentioned.

---

## 🎨 Use Cases

### 1. Helpful Assistant

```bash
/ai create Assistant gemini YOUR_KEY "You are a helpful AI assistant"
```

**Use for:**
- Code help
- General questions
- Brainstorming
- Fact-checking

**Example chat:**
```
You: @Assistant how do I deploy this to Railway?
Assistant: Here's how to deploy to Railway:
1. Install Railway CLI
2. Run `railway init`
3. ...
```

### 2. Roleplay Partner

```bash
/ai create Bartender gemini YOUR_KEY "You are a gruff tavern bartender in a fantasy world. You speak plainly and know all the town gossip."
```

**Example chat:**
```
Luna (you): *enters the tavern* What's the news?
Bartender: *wipes down a mug* News? Hah. Dragon's been spotted near the old ruins again...
```

### 3. Character Development Helper

```bash
/ai create CharacterBot gemini YOUR_KEY "You help writers develop characters by asking probing questions about their motivations, backstory, and relationships."
```

**Example:**
```
You: I'm working on a character named Riley
CharacterBot: Tell me about Riley! What drives them? What are they afraid of?
```

### 4. Different Personalities

Create multiple AI characters with different vibes:

```bash
# Professional
/ai create Professional gemini KEY "You are formal and business-like"

# Chaotic
/ai create Chaos gemini KEY "You are chaotic and unpredictable, often giving wild ideas"

# Supportive
/ai create Cheerleader gemini KEY "You are super supportive and always encouraging"
```

### 5. Local & Private

Use Ollama for 100% private AI:

```bash
# Install Ollama first: https://ollama.ai
ollama serve
ollama pull llama2

# Create local AI character
/ai create PrivateBot ollama none "You are a helpful local assistant"

# Everything stays on your machine!
@PrivateBot help me with this sensitive topic
```

---

## 🔑 Getting API Keys

### Google Gemini (Recommended - FREE!)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Copy your key
4. Use it: `/ai create Helper gemini YOUR_KEY_HERE "helpful assistant"`

**Free Tier:**
- 60 requests/minute
- 1500 requests/day
- Perfect for personal use!

### OpenAI

1. Go to [OpenAI API](https://platform.openai.com/api-keys)
2. Create account, add payment method
3. Create API key
4. Use it: `/ai create Helper openai sk-YOUR_KEY "helpful assistant"`

**Cost:** ~$0.50-2/month for moderate use

### Anthropic Claude

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create account, add payment
3. Create API key
4. Use it: `/ai create Helper claude sk-ant-YOUR_KEY "helpful assistant"`

**Cost:** ~$1-3/month for Claude Haiku (cheapest)

### Ollama (Local - FREE!)

1. Install Ollama: [ollama.ai](https://ollama.ai)
2. Run `ollama serve`
3. Pull a model: `ollama pull llama2`
4. Create character: `/ai create LocalBot ollama none "assistant"`

**No API key needed! Runs on your machine!**

---

## ⚙️ Advanced Configuration

### Personality Prompts

The personality is the "system prompt" that defines character behavior:

**Short & Simple:**
```
"You are a helpful assistant"
```

**Detailed Character:**
```
"You are Zyx, an ancient wizard from the Obsidian Tower.
You speak in riddles and archaic language. You're wise but
mischievous, often giving cryptic advice. You love wordplay."
```

**Roleplay Character:**
```
"You are Riley Chen, a 28-year-old detective in a noir setting.
You're cynical but caring, speak in short sentences, and
always looking for the truth. You have a dark sense of humor."
```

**The more detailed, the better the character stays in role!**

### Model Selection

Different models for different needs:

**Gemini:**
- `gemini-pro` - Default, good all-around
- `gemini-1.5-flash` - Faster, cheaper, still great

**OpenAI:**
- `gpt-3.5-turbo` - Fast, cheap ($0.002/1k tokens)
- `gpt-4` - Smartest, expensive ($0.03/1k tokens)
- `gpt-4-turbo` - Balance of speed and quality

**Claude:**
- `claude-3-haiku` - Cheapest, fast
- `claude-3-sonnet` - Balanced
- `claude-3-opus` - Smartest (expensive)

**Ollama:**
- `llama2` - General purpose
- `mistral` - Fast and capable
- `codellama` - Code-focused
- `neural-chat` - Conversational

Change model:
```bash
/ai configure MyBot model gpt-4
```

---

## 🎭 Example AI Characters

### The Wise Mentor

```bash
/ai create Mentor gemini KEY "You are a wise mentor who guides through questions rather than direct answers. You speak calmly and encourage self-discovery."
```

### The Enthusiastic Hype Person

```bash
/ai create Hype gemini KEY "You are SUPER EXCITED about EVERYTHING!!! You use lots of exclamation marks!!! You believe in people!!!"
```

### The Grumpy Critic

```bash
/ai create Critic gemini KEY "You are a grumpy literary critic who finds fault in everything but occasionally admits something is 'not terrible'."
```

### The Mysterious Oracle

```bash
/ai create Oracle gemini KEY "You are an oracle who speaks only in cryptic prophecies and vague warnings. You never give straight answers."
```

### The Coding Buddy

```bash
/ai create CodeBuddy gemini KEY "You are a friendly coding assistant. You explain things clearly, provide code examples, and debug issues. You love teaching."
```

---

## 💰 Cost Management

### How Much Does This Cost?

**Gemini (FREE tier):**
- 0-100 messages/day: $0
- 100-1500 messages/day: $0
- Over 1500 messages/day: Need paid tier (~$5/mo)

**OpenAI (gpt-3.5-turbo):**
- 100 messages: ~$0.10
- 1000 messages: ~$1.00
- 10,000 messages: ~$10.00

**Claude (haiku):**
- Similar to GPT-3.5 turbo

**Ollama:**
- Infinite messages: $0 (runs locally!)

### Tips to Save Money:

1. **Use Gemini free tier** - Perfect for personal use
2. **Use Ollama** - 100% free, runs on your machine
3. **Shorter personalities** - Less tokens used
4. **Disable when not needed** - `/ai toggle BotName`
5. **Use cheaper models** - `gpt-3.5-turbo` vs `gpt-4`

---

## 🔒 Security & Privacy

### API Keys are Encrypted

Your API keys are encrypted in the database using Fernet encryption. They're never stored in plain text.

### Per-Character Keys

Each AI character can have its own API key:
- Use work API key for work bots
- Use personal API key for personal bots
- Share bot with friends? They use their own key

### Privacy Options

**Want maximum privacy?**
- Use **Ollama** (runs locally, no internet)
- Everything stays on your machine
- No data sent to any company

---

## 🐛 Troubleshooting

### "AI character needs API key configured"

**Solution:**
```bash
/ai configure BotName apikey YOUR_API_KEY
```

### "AI character failed to respond"

**Possible causes:**
1. Invalid API key
2. Out of API credits
3. Rate limit hit
4. API is down

**Check:**
```bash
/ai test BotName hello
```

### "Ollama is not running"

**Solution:**
```bash
# Start Ollama in terminal
ollama serve

# In another terminal
ollama pull llama2

# Now try again
@LocalBot hello!
```

### AI Responds Too Slowly

**Solutions:**
1. Use faster model (`gemini-1.5-flash`, `gpt-3.5-turbo`)
2. Use Ollama locally (if you have good hardware)
3. Shorter personality prompts

### AI Doesn't Stay in Character

**Solution:** Make personality more detailed:

**Before:**
```
"You are a wizard"
```

**After:**
```
"You are Gandalf-style wizard. ALWAYS speak in archaic English.
Use 'thee' and 'thou'. Reference ancient magic. Never break character.
If asked modern questions, relate them to magic."
```

---

## 💡 Creative Ideas

### 1. Character Interview

Create AI version of your character to interview them:

```bash
/ai create RileyAI gemini KEY "You are Riley Chen from my novel. Answer as Riley would."
```

```
You: Riley, what motivates you?
RileyAI: *leans back* Truth. Always the truth, even when it hurts...
```

### 2. Devil's Advocate

```bash
/ai create DevilsAdvocate gemini KEY "You always argue the opposite position to help test ideas."
```

### 3. Rubber Duck Debugging

```bash
/ai create RubberDuck gemini KEY "You are a rubber duck. You help people debug by asking clarifying questions about their code."
```

### 4. Random Idea Generator

```bash
/ai create IdeaBot gemini KEY "You generate wild, creative ideas. Nothing is too weird. Go crazy."
```

### 5. Multiple Perspectives

Create 3 AI characters with different viewpoints:
- Optimist
- Pessimist
- Realist

Ask them all the same question and compare!

---

## 📊 Comparison: AI vs Regular Characters

| Feature | Regular Character | AI Character |
|---------|------------------|--------------|
| **You control** | ✅ Yes | ❌ No (AI does) |
| **Always available** | ❌ Only when you type | ✅ Responds automatically |
| **Costs money** | ✅ Free | Depends (Ollama free) |
| **Consistent personality** | ✅ You decide | ⚠️ Mostly (varies) |
| **Creative responses** | ⚠️ Limited by you | ✅ Very creative |
| **Privacy** | ✅ 100% private | ⚠️ Depends (Ollama = private) |

**Best use:** Mix both! Regular characters for you, AI characters for assistants/NPCs!

---

## 🎓 Next Steps

**Ready to try it?**

1. Get a free Gemini API key
2. Create your first AI character
3. Chat with them!
4. Create more characters for different purposes
5. Have fun!

**Ideas:**
- Create a personal assistant
- Make an AI writing buddy
- Build NPC characters for roleplay
- Test out different personalities
- Mix AI and regular characters in conversation

---

## 🔗 Resources

- [Google AI Studio](https://makersuite.google.com/app/apikey) - Free Gemini API keys
- [Ollama](https://ollama.ai) - Free local AI
- [OpenAI Platform](https://platform.openai.com/) - GPT API
- [Anthropic Console](https://console.anthropic.com/) - Claude API

---

**Happy chatting with your AI characters!** 🤖✨

*Remember: AI characters are tools for creativity and fun. They work best when you have clear personalities and use cases in mind!*
