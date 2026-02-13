# Installation Guide - World Labs ComfyUI Nodes

This guide will walk you through installing the World Labs custom nodes for ComfyUI.

## Prerequisites

Before installing, make sure you have:

1. ✅ **ComfyUI** installed and working
2. ✅ **Python 3.8+** (should already be installed with ComfyUI)
3. ✅ **Git** (for cloning the repository)
4. ✅ **World Labs API Key** - Sign up at [worldlabs.ai](https://worldlabs.ai)

## Installation Methods

### Method 1: Git Clone (Recommended)

This is the easiest method and allows for easy updates.

#### Step 1: Navigate to Custom Nodes Directory

**Windows:**
```bash
cd C:\path\to\ComfyUI\custom_nodes
```

**Linux/Mac:**
```bash
cd /path/to/ComfyUI/custom_nodes
```

#### Step 2: Clone the Repository

```bash
git clone https://github.com/yourusername/Worldlabs-Comfy.git
```

#### Step 3: Install Dependencies

```bash
cd Worldlabs-Comfy
pip install -r requirements.txt
```

Or if you're using a virtual environment:

```bash
cd Worldlabs-Comfy
path/to/comfyui/python_embeded/python.exe -m pip install -r requirements.txt
```

#### Step 4: Restart ComfyUI

Close and restart ComfyUI. You should see the World Labs nodes in the "WorldLabs" category.

---

### Method 2: Manual Download

If you don't have Git installed:

#### Step 1: Download the Repository

1. Go to https://github.com/yourusername/Worldlabs-Comfy
2. Click the green "Code" button
3. Select "Download ZIP"
4. Extract the ZIP file

#### Step 2: Copy to Custom Nodes

Copy the extracted `Worldlabs-Comfy` folder to your ComfyUI `custom_nodes` directory:

```
ComfyUI/
└── custom_nodes/
    └── Worldlabs-Comfy/
        ├── __init__.py
        ├── worldlabs_comfyui_nodes.py
        ├── worldlabs_viewer_node.py
        ├── requirements.txt
        └── ...
```

#### Step 3: Install Dependencies

Open a terminal/command prompt and run:

**Windows (Standard Python):**
```bash
cd C:\path\to\ComfyUI\custom_nodes\Worldlabs-Comfy
pip install -r requirements.txt
```

**Windows (Portable/Embedded Python):**
```bash
cd C:\path\to\ComfyUI\custom_nodes\Worldlabs-Comfy
..\..\python_embeded\python.exe -m pip install -r requirements.txt
```

**Linux/Mac:**
```bash
cd /path/to/ComfyUI/custom_nodes/Worldlabs-Comfy
pip install -r requirements.txt
```

#### Step 4: Restart ComfyUI

Restart ComfyUI to load the new nodes.

---

### Method 3: ComfyUI Manager (Coming Soon)

Once available in ComfyUI Manager, you'll be able to install with one click:

1. Open ComfyUI Manager
2. Search for "World Labs"
3. Click "Install"
4. Restart ComfyUI

---

## Setting Up Your API Key

After installation, you need to configure your World Labs API key.

### Option A: Environment Variable (Recommended for All Users)

This is the most secure method as your API key won't be visible in your workflows.

#### Windows

**Method 1: System Environment Variables (Persistent)**
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Go to "Advanced" tab → "Environment Variables"
3. Under "User variables", click "New"
4. Variable name: `WORLDLABS_API_KEY`
5. Variable value: `your_api_key_here`
6. Click OK, OK, OK
7. Restart your terminal/ComfyUI

**Method 2: Command Prompt (Session-Only)**
```cmd
set WORLDLABS_API_KEY=your_api_key_here
python main.py
```

**Method 3: PowerShell (Session-Only)**
```powershell
$env:WORLDLABS_API_KEY="your_api_key_here"
python main.py
```

**Method 4: Batch Script**
Create a file `start_comfyui.bat` in your ComfyUI directory:
```batch
@echo off
set WORLDLABS_API_KEY=your_api_key_here
python main.py
pause
```

#### Linux/Mac

**Method 1: Shell Profile (Persistent)**

Add to your `~/.bashrc`, `~/.zshrc`, or `~/.bash_profile`:
```bash
export WORLDLABS_API_KEY="your_api_key_here"
```

Then reload:
```bash
source ~/.bashrc  # or ~/.zshrc
```

**Method 2: Command Line (Session-Only)**
```bash
export WORLDLABS_API_KEY="your_api_key_here"
python main.py
```

**Method 3: Launch Script**
Create a file `start_comfyui.sh`:
```bash
#!/bin/bash
export WORLDLABS_API_KEY="your_api_key_here"
python main.py
```

Make it executable:
```bash
chmod +x start_comfyui.sh
./start_comfyui.sh
```

---

### Option B: Use WorldLabsAPIKey Node

1. Add a "World Labs API Key" node to your workflow
2. Enter your API key in the `api_key` field
3. Connect it to the "Generate World" node

**Note:** Your API key will be saved in the workflow JSON file, so be careful when sharing workflows.

---

### Option C: Direct Input

1. Add a "Generate World (World Labs)" node
2. Type your API key directly in the `api_key` field

**Note:** Same as Option B - key will be in the workflow file.

---

## Verification

To verify the installation:

### Step 1: Check Node Availability

1. Start ComfyUI
2. Right-click in the workflow editor
3. Navigate to "Add Node" → "WorldLabs"
4. You should see:
   - World Labs API Key
   - Generate World (World Labs)
   - World Info (World Labs)
   - Download Asset (World Labs)
   - 3D Viewer (World Labs)

### Step 2: Check Console Output

When ComfyUI starts, you should see:
```
============================================================
World Labs ComfyUI Nodes loaded successfully!
============================================================
Available nodes:
  • World Labs API Key
  • Generate World (World Labs)
  • World Info (World Labs)
  • Download Asset (World Labs)
  • 3D Viewer (World Labs)

Make sure to set your WORLDLABS_API_KEY environment variable
or enter it directly in the WorldLabsAPIKey node.
============================================================
```

### Step 3: Test with Example Workflow

1. In ComfyUI, click "Load" → "example_workflow.json"
2. Replace the image in the LoadImage node
3. If using environment variable, you're ready to run
4. If not, add your API key to the WorldLabsAPIKey node
5. Click "Queue Prompt"

---

## Updating

### If Installed via Git

```bash
cd ComfyUI/custom_nodes/Worldlabs-Comfy
git pull
pip install -r requirements.txt --upgrade
```

Then restart ComfyUI.

### If Installed Manually

1. Download the latest version
2. Replace the old `Worldlabs-Comfy` folder
3. Reinstall dependencies: `pip install -r requirements.txt --upgrade`
4. Restart ComfyUI

---

## Uninstalling

### Step 1: Remove the Folder

Delete the `Worldlabs-Comfy` folder from `ComfyUI/custom_nodes/`

### Step 2: (Optional) Remove Dependencies

If you want to remove the installed packages:

```bash
pip uninstall requests pillow numpy
```

**Warning:** Only do this if you're sure no other custom nodes need these packages!

### Step 3: Restart ComfyUI

---

## Troubleshooting

### Issue: Nodes Don't Appear in ComfyUI

**Solution:**
1. Check that the folder is in the correct location: `ComfyUI/custom_nodes/Worldlabs-Comfy`
2. Verify `__init__.py` exists in the folder
3. Check ComfyUI console for error messages
4. Try reinstalling dependencies: `pip install -r requirements.txt`

---

### Issue: "ModuleNotFoundError: No module named 'requests'"

**Solution:**

You need to install dependencies. Make sure you're using the correct Python:

**Standard Installation:**
```bash
pip install -r requirements.txt
```

**Portable/Embedded Python:**
```bash
path/to/python_embeded/python.exe -m pip install -r requirements.txt
```

---

### Issue: "No API key provided"

**Solution:**

Your API key is not configured. Use one of these methods:

1. Set `WORLDLABS_API_KEY` environment variable (recommended)
2. Use the WorldLabsAPIKey node
3. Enter key directly in Generate World node

See "Setting Up Your API Key" section above.

---

### Issue: Generation Fails Immediately

**Possible Causes & Solutions:**

1. **Invalid API Key**
   - Double-check your API key is correct
   - Verify it's active in your World Labs dashboard

2. **No API Credits**
   - Check your World Labs account for remaining credits

3. **Network Issues**
   - Check your internet connection
   - Try disabling VPN/proxy temporarily

4. **API Service Down**
   - Check World Labs status page
   - Try again later

---

### Issue: Import Error on Startup

**Error Example:**
```
Error loading custom node Worldlabs-Comfy: ...
```

**Solution:**

1. Check Python version: `python --version` (needs 3.8+)
2. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
3. Check for conflicting installations
4. Look at the full error in ComfyUI console

---

### Issue: Viewers Don't Load

**Solution:**

1. Ensure you have an active internet connection (viewers load from CDN)
2. Check browser console for errors (F12 in most browsers)
3. Try a different browser
4. Disable browser extensions that might block scripts

---

## Platform-Specific Notes

### Windows

- If using Windows portable version, use `python_embeded\python.exe` for pip commands
- Use double backslashes or forward slashes in paths: `C:\\ComfyUI\\custom_nodes` or `C:/ComfyUI/custom_nodes`

### Linux

- You might need to use `pip3` instead of `pip`
- You might need to use `python3` instead of `python`
- If permission denied, use `sudo` or virtual environment

### macOS

- Similar to Linux - use `pip3` and `python3` if needed
- On M1/M2 Macs, ensure you're using ARM-compatible Python

### Docker/Virtual Environments

If running ComfyUI in Docker or venv:

```bash
# Activate your environment first
source /path/to/venv/bin/activate  # Linux/Mac
# or
.\path\to\venv\Scripts\activate  # Windows

# Then install
cd ComfyUI/custom_nodes/Worldlabs-Comfy
pip install -r requirements.txt
```

---

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: 8GB minimum (16GB recommended for full-res viewing)
- **Internet**: Required for API calls and viewer CDN libraries
- **Disk Space**: ~100MB for nodes + space for downloaded assets

---

## Getting Help

If you're still having issues:

1. **Check the README**: [README.md](README.md) for usage information
2. **Search Issues**: Check [GitHub Issues](https://github.com/yourusername/Worldlabs-Comfy/issues)
3. **Create an Issue**: If your problem is new, open an issue with:
   - Your OS and Python version
   - ComfyUI version
   - Full error message from console
   - Steps to reproduce

---

## Next Steps

Once installed, check out:

- [README.md](README.md) - Complete usage guide
- `example_workflow.json` - Working example workflow
- [World Labs Documentation](https://docs.worldlabs.ai/api) - API details

**Happy 3D world generating! 🚀**
