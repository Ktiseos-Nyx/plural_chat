# 🎨 AI Image Generation Integration Guide

## "HOLD YOUR VIRTUAL BEER" - This is ACTUALLY Genius!

Integration of Stable Diffusion APIs (Automatic1111, Forge UI, ComfyUI) for ephemeral image generation in chat.

**Perfect for:**
- Renting a GPU for 1 hour
- Generating system member art
- Sharing AI generations temporarily
- No permanent storage needed (auto-deletes after 24hrs)
- Multiple systems using the same rented GPU instance

---

## 🚀 Quick Start

### 1. Rent a GPU (or use local)

**Cloud Options:**
- [RunPod](https://runpod.io) - $0.2-0.5/hour
- [Vast.ai](https://vast.ai) - $0.1-0.3/hour
- [Paperspace](https://paperspace.com) - Various pricing
- **Local** - Your own GPU

### 2. Connect to Plural Chat

```
/sdconnect a1111 http://your-gpu-url:7860
```

### 3. Generate Images

```
/generate a portrait of a space explorer
/generate cute anime cat girl --size 768x512 --steps 30
/generate cyberpunk cityscape --negative blurry, ugly
```

### 4. Images Auto-Post to Chat

Generated images are:
- Cached for 24 hours
- Displayed in chat automatically
- Shared with everyone in the instance
- Auto-deleted after 24hrs (ephemeral!)

---

## 📚 Commands Reference

### Connection Management

#### `/sdconnect <api_type> <url> [api_key]`
**Aliases:** `/sdlink`

Connect to your SD API instance.

**API Types:**
- `a1111` or `automatic1111` - Automatic1111 WebUI
- `forge` - Forge WebUI (same API as A1111)
- `comfyui` - ComfyUI (coming soon)

**Examples:**
```
# Local A1111
/sdconnect a1111 http://localhost:7860

# RunPod instance
/sdconnect forge https://abc123-7860.proxy.runpod.net

# With API key
/sdconnect a1111 http://mygpu.com:7860 my-secret-key
```

#### `/sdtest`
Test your SD API connection.

```
/sdtest
```

**Response:**
```
✅ Connection OK!

**API Type:** automatic1111
**URL:** http://localhost:7860

Ready to generate! Try `/generate <prompt>`
```

#### `/sddisconnect`
Disconnect from SD API.

```
/sddisconnect
```

### Model Management

#### `/sdmodels`
**Aliases:** `/models`

List available models on your SD instance.

```
/sdmodels
```

**Response:**
```
📦 Available Models:

1. realisticVisionV51.safetensors
2. dreamshaper_8.safetensors
3. anythingV5_v5.safetensors
```

### Image Generation

#### `/generate <prompt> [options]`
**Aliases:** `/gen`, `/img`

Generate an AI image!

**Options:**
- `--negative <prompt>` - Negative prompt (what to avoid)
- `--size WxH` - Image size (default: 512x512)
- `--steps N` - Generation steps (default: 20)

**Size must be multiples of 64. No hard limit - choose based on your GPU!**
- 512x512: Fast, works on most GPUs (4GB+ VRAM)
- 768x768: Good quality, requires 6GB+ VRAM
- 1024x1024: High quality, requires 8GB+ VRAM
- 1536x1536: Very high quality, requires 12GB+ VRAM
- Higher: Possible but slower, requires 16GB+ VRAM

**Examples:**

```
# Simple generation
/generate a cute cat

# With negative prompt
/generate portrait of Riley --negative ugly, blurry, distorted

# Custom size and steps
/generate cyberpunk cityscape --size 768x512 --steps 30

# Complex prompt
/generate highly detailed portrait of a system member, purple hair, kind eyes, soft lighting --negative deformed, bad anatomy --size 640x640 --steps 25
```

**Generation Process:**
1. Command returns "Generating..." message
2. Background task generates image (30-120 seconds)
3. Image posted to chat automatically when ready
4. Image cached for 24 hours
5. Auto-deleted after 24 hours

---

## 🎯 Use Cases

### 1. System Member Portraits

Generate art for your system members!

```
/generate portrait of Riley, purple hair, green eyes, kind smile, digital art
/generate portrait of Alex, short black hair, confident expression, cyberpunk style
/generate portrait of Sam, blonde curly hair, soft features, watercolor painting
```

### 2. Headspace Visualization

```
/generate cozy headspace interior, warm lighting, comfortable furniture, safe space
/generate dreamlike landscape with floating islands, surreal, peaceful
```

### 3. Shared World Building

```
/generate fantasy tavern interior, warm fireplace, wooden tables
/generate alien planet landscape, purple sky, bioluminescent plants
```

### 4. Memes & Fun

```
/generate a cat wearing a wizard hat, magical, glowing
/generate retro 80s synthwave sunset over ocean
```

---

## 🏗️ Technical Details

### Architecture

```
┌──────────────────┐
│   Your Chat      │
│   (Browser)      │
└────────┬─────────┘
         │ /generate command
         ▼
┌──────────────────┐
│  Plural Chat     │
│  Backend         │
└────────┬─────────┘
         │ API call
         ▼
┌──────────────────┐     ┌──────────────────┐
│  Your GPU        │────▶│  Ephemeral       │
│  (Rented/Local)  │     │  Cache (24hrs)   │
└──────────────────┘     └──────────────────┘
   A1111/Forge                   ▼
                          Displayed in Chat
```

### Ephemeral Storage

**Why ephemeral?**
- GPU rentals are temporary (1 hour sessions)
- Generated images don't need permanent storage
- Saves disk space
- Perfect for experimentation

**How it works:**
1. Image generated via SD API
2. Saved to `media_cache/` directory
3. Served via `/api/media/{id}`
4. Auto-deleted after 24 hours
5. Periodic cleanup task removes expired files

**Storage estimates:**
- Average image: ~500KB (WebP compressed)
- 10 generations: ~5MB
- 100 generations: ~50MB
- All auto-deleted after 24hrs!

### Security

**URL Validation:**
- HTTPS required for external URLs
- File extension validation
- Domain whitelist (optional)
- Size limits (10MB max)

**API Connection:**
- User-specific connections
- Optional API key support
- Connection test before use
- Error handling

### Supported APIs

#### Automatic1111 / Forge UI

**Features:**
- Text-to-image ✅
- Image-to-image ✅ (future)
- Model listing ✅
- Model switching ⏳ (future)

**API Endpoints Used:**
- `GET /sdapi/v1/sd-models` - List models
- `POST /sdapi/v1/txt2img` - Generate image
- `POST /sdapi/v1/img2img` - Image-to-image

#### ComfyUI

**Status:** Coming soon!

**Features:**
- Workflow-based generation
- More advanced control
- Node-based interface

---

## 📖 Setup Guides

### Local Automatic1111 Setup

1. **Install A1111:**
```bash
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui
# Follow installation instructions for your OS
```

2. **Start with API enabled:**
```bash
./webui.sh --api --listen
# Windows: webui-user.bat --api --listen
```

3. **Connect from Plural Chat:**
```
/sdconnect a1111 http://localhost:7860
```

### RunPod Setup (Detailed)

**RunPod is perfect for this!** They have pre-configured Stable Diffusion templates.

1. **Sign up at [RunPod.io](https://runpod.io)**
   - Create account (credit card required)
   - Add credits ($10 minimum, gets you 20-50 hours depending on GPU)

2. **Deploy a Stable Diffusion Pod:**
   - Click "Deploy" or "Pods" → "Deploy Pod"
   - Search for templates: "Stable Diffusion" or "AUTOMATIC1111"
   - Recommended templates:
     - "Stable Diffusion WebUI" (official)
     - "Stable Diffusion Auto1111" (popular)
     - "Forge WebUI" (faster, same API)

3. **Choose Your GPU:**
   - **RTX 3090** - $0.34/hr - Best value, 24GB VRAM (recommended!)
   - **RTX 4090** - $0.69/hr - Fastest, 24GB VRAM
   - **A4000** - $0.29/hr - Good for portraits, 16GB VRAM
   - **RTX 3080** - $0.24/hr - Budget option, 10-12GB VRAM
   - **RTX 4080** - $0.59/hr - Fast, 16GB VRAM

4. **Deploy and Wait:**
   - Click "Deploy On-Demand" (or "Deploy Spot" for cheaper but less reliable)
   - Wait 1-3 minutes for pod to start
   - Status will change to "Running"

5. **Get Your Connection URL:**
   - Click "Connect" → Copy the HTTP URL
   - It looks like: `https://abc123xyz-7860.proxy.runpod.net`
   - **Important:** Use the URL with port 7860 in it!

6. **Connect from Plural Chat:**
```bash
/sdconnect a1111 https://abc123xyz-7860.proxy.runpod.net
/sdtest  # Test connection
/sdmodels  # See available models
```

7. **Generate Images:**
```bash
/generate portrait of a system member, digital art
/generate cyberpunk cityscape --size 768x512 --steps 30
```

8. **When Done:**
   - **IMPORTANT:** Click "Stop" or "Terminate" pod to stop charges!
   - RunPod charges by the minute
   - Forgetting to stop = wasted money

**Pro Tips:**
- Use On-Demand for reliability (Spot is cheaper but can get interrupted)
- RTX 3090 is the sweet spot for price/performance
- Generate multiple images per session to maximize your rental
- Check RunPod Community Cloud for cheaper GPUs from community hosts

---

### Vast.ai Setup (Detailed)

**Vast.ai is great for budget rentals!** Prices can be as low as $0.10/hr.

1. **Sign up at [Vast.ai](https://vast.ai)**
   - Create account
   - Add credits via crypto or credit card ($10 minimum)

2. **Search for GPU Instance:**
   - Go to "Console" → "Create"
   - Or click "Search Offers"

3. **Filter for Stable Diffusion:**
   - **Template:** Select "automatic1111/stable-diffusion-webui" or search "a1111"
   - **GPU:** Choose based on VRAM needs:
     - RTX 3060 (12GB) - $0.10-0.20/hr
     - RTX 3080 (10-12GB) - $0.15-0.30/hr
     - RTX 3090 (24GB) - $0.20-0.40/hr
     - RTX 4090 (24GB) - $0.40-0.70/hr
   - **Disk Space:** At least 30GB for models
   - **Sort by:** Price (cheapest first) or DLPerf (fastest)

4. **Select an Offer:**
   - Click "Rent" on an offer that fits your budget
   - Check "Reliability" score (90%+ recommended)
   - Review specs and price

5. **Configure Instance:**
   - **Template:** Select "Stable Diffusion Auto1111"
   - **Image:** Choose latest WebUI image
   - **On-start script:** (optional)
     ```bash
     # Automatically start with API enabled
     cd /workspace/stable-diffusion-webui
     python launch.py --api --listen --xformers
     ```

6. **Launch Instance:**
   - Click "Create" or "Rent"
   - Wait 2-5 minutes for instance to start
   - Instance will show "running" status

7. **Get Connection Details:**
   - Click on your instance
   - Find "Open" button next to port 7860
   - Or copy the direct URL (looks like `http://12.34.56.78:7860`)

8. **Access the WebUI (Optional):**
   - Click the URL to open WebUI in browser
   - Verify it's working
   - Check Settings → API → Ensure API is enabled

9. **Connect from Plural Chat:**
   ```bash
   # Use the instance's public IP and port
   /sdconnect a1111 http://12.34.56.78:7860

   # Or if using SSH tunnel:
   /sdconnect a1111 http://localhost:7860

   # Test connection
   /sdtest

   # List models
   /sdmodels
   ```

10. **Generate Images:**
```bash
/generate cute anime cat girl, colorful, high quality
/generate system member portrait --size 768x768 --steps 25
```

11. **When Finished:**
   - **IMPORTANT:** Click "Destroy Instance" to stop charges!
   - Vast.ai charges by the minute
   - You can "Stop" instance to pause (still charges for storage)
   - "Destroy" completely removes it (no charges)

**Pro Tips:**
- Sort by "DLPerf" for fastest GPUs
- Check "Verification" status (green = reliable host)
- Community hosts are cheaper than data centers
- Some hosts have models pre-downloaded (faster startup)
- Use SSH for more control (advanced)

**Troubleshooting:**
- **Can't connect?** Make sure port 7860 is exposed
- **WebUI not loading?** Check on-start script ran successfully
- **API errors?** Enable API in WebUI Settings
- **Slow generation?** Choose GPU with higher DLPerf score

---

### Comparison: RunPod vs Vast.ai

| Feature | RunPod | Vast.ai |
|---------|--------|---------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ Very easy | ⭐⭐⭐ Moderate |
| **Price** | $0.24-0.69/hr | $0.10-0.50/hr |
| **Reliability** | Very reliable | Variable (check host rating) |
| **Setup Time** | 1-3 minutes | 2-5 minutes |
| **Pre-configured** | Yes, official templates | Yes, community templates |
| **Support** | Good | Community-based |
| **Best For** | Beginners, reliability | Power users, budget |

**Recommendation:**
- **New to GPU rentals?** Start with RunPod (easier, more reliable)
- **Want cheapest option?** Use Vast.ai (can be 50% cheaper)
- **Need it to "just work"?** RunPod
- **Comfortable with tech?** Vast.ai offers better deals

---

## 🎨 Prompting Tips

### Good Prompts

```
✅ portrait of Riley, purple hair, green eyes, kind smile, digital art, high quality
✅ cyberpunk cityscape at night, neon lights, rain, detailed, 8k
✅ cozy fantasy tavern interior, warm fireplace, wooden furniture, ambient lighting
```

### Avoid

```
❌ riley (too vague)
❌ a person (not specific enough)
❌ something cool (no details)
```

### Negative Prompts

Help avoid unwanted elements:

```
--negative ugly, deformed, blurry, bad anatomy, low quality, distorted
--negative multiple heads, extra limbs, text, watermark
--negative nsfw, gore, violence
```

### Sizes

**Common aspect ratios:**
- `512x512` - Square (default)
- `512x768` - Portrait
- `768x512` - Landscape
- `640x640` - Square (larger)
- `768x768` - Square (large)

**Remember:** Must be multiples of 64!

### Steps

**Recommended:**
- `15-20` - Fast, good quality
- `25-30` - Better quality, slower
- `40-50` - High quality, slow
- `100+` - Diminishing returns, very slow

---

## 🔥 Cool Examples

### System Member Portraits

```
/generate portrait of a kind system host, warm brown eyes, gentle smile, soft lighting, digital painting --size 512x768 --steps 25

/generate portrait of a protective system protector, strong features, determined expression, cool blue lighting --negative weak, soft --size 512x768

/generate portrait of a playful system little, big expressive eyes, bright colors, cheerful, anime style --size 512x512
```

### Headspace Scenes

```
/generate cozy library headspace, bookshelves, reading nook, warm lamps, peaceful atmosphere --size 768x512 --steps 30

/generate dreamlike headspace with floating crystals, soft pastel colors, ethereal, safe and comfortable --size 768x512

/generate futuristic headspace interior, holographic displays, comfortable seating, high tech but cozy --size 768x512
```

### Aesthetic Vibes

```
/generate vaporwave sunset over ocean, palm trees, retro 80s aesthetic, neon pink and purple --size 768x512

/generate cottagecore garden, flowers, butterflies, soft sunlight, peaceful and natural --size 640x640

/generate dark academia library, old books, candlelight, mysterious atmosphere --size 768x512
```

---

## ⚙️ Advanced Features (Future)

### Coming Soon:

- **Image-to-image** - Modify existing images
- **Inpainting** - Edit parts of images
- **ControlNet** - Pose/depth control
- **LoRA support** - Style/character models
- **Upscaling** - Enhance resolution
- **Batch generation** - Multiple variations
- **Gallery** - Browse generated images
- **Favorites** - Save favorite generations

---

## 💡 Pro Tips

1. **Use descriptive prompts** - More details = better results

2. **Experiment with styles:**
   - "digital art"
   - "oil painting"
   - "anime style"
   - "photorealistic"
   - "watercolor"

3. **Adjust steps based on complexity:**
   - Simple: 15-20 steps
   - Detailed: 25-35 steps
   - Very detailed: 40+ steps

4. **Try different sizes:**
   - Portrait subjects: 512x768
   - Landscapes: 768x512
   - Characters: 640x640

5. **Use negative prompts!**
   - Always include: "blurry, low quality"
   - Add specific things to avoid

6. **GPU rental tips:**
   - Start with shorter prompts (faster)
   - Test connection first (`/sdtest`)
   - Generate multiple images per session
   - Stop instance when done to save money

---

## 🐛 Troubleshooting

### "No SD API connected"

**Solution:**
```
/sdconnect a1111 http://your-url:7860
```

### "Connection failed"

**Check:**
- Is the SD WebUI running?
- Is `--api` flag enabled?
- Is `--listen` flag enabled (for remote)?
- Is the URL correct?
- Firewall blocking connection?

**Test manually:**
```bash
curl http://your-url:7860/sdapi/v1/sd-models
```

### "Generation timed out"

**Causes:**
- GPU too slow
- Too many steps
- Too large resolution

**Solutions:**
- Reduce steps (try 20)
- Reduce size (try 512x512)
- Use faster GPU

### Images not appearing

**Check:**
- Generation may still be running (wait 30-120 seconds)
- Check backend logs for errors
- Try simpler prompt first

---

## 📊 Performance Benchmarks

**RTX 3090** (24GB VRAM):
- 512x512, 20 steps: ~5 seconds
- 768x768, 30 steps: ~15 seconds
- 1024x1024, 50 steps: ~45 seconds

**RTX 3060** (12GB VRAM):
- 512x512, 20 steps: ~10 seconds
- 768x768, 30 steps: ~30 seconds
- 1024x1024: May run out of VRAM

**A4000** (16GB VRAM):
- 512x512, 20 steps: ~7 seconds
- 768x768, 30 steps: ~20 seconds
- 1024x1024, 50 steps: ~60 seconds

---

## 🎉 This is Perfect For

- **Temporary GPU rentals** - Pay per hour, images auto-delete
- **System member art** - Generate portraits of your system
- **Shared creativity** - Multiple systems using one GPU
- **Experimentation** - Try different styles without permanent storage
- **Fun in chat** - Share AI art with friends

---

## 🚀 Future Ideas

- `/style` command - Apply specific art styles
- `/remix` command - Variations of an image
- `/upscale` command - Enhance resolution
- `/blend` command - Mix two images
- Gallery view in web UI
- Favorite/save system
- Batch generation
- ControlNet integration
- LoRA model loading

---

**This feature is absolutely genius for ephemeral GPU rental sessions!** 🎨✨

**"Hold your virtual beer" indeed** - this is actually the perfect use case for temporary storage and GPU rentals. Generate system art, share in chat, no permanent storage bloat. Chef's kiss! 👨‍🍳💋
