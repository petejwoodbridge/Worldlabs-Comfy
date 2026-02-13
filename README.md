# World Labs ComfyUI Nodes

Generate stunning 3D worlds from images using the [World Labs Marble API](https://docs.worldlabs.ai/api) directly in ComfyUI!

This custom node package integrates World Labs' cutting-edge AI technology that transforms single images into fully explorable 3D worlds, complete with Gaussian splats, 3D meshes, and panoramic views.

## Features

- 🖼️ **Generate 3D Worlds** from any image
- 🎨 **Multiple Output Formats**: Gaussian splats (100k, 500k, full resolution), 3D meshes (GLB), and panoramas
- 👁️ **Interactive 3D Viewers** built into ComfyUI using PlayCanvas SuperSplat, Three.js, and Photo Sphere Viewer
- 📥 **Download Assets** directly to your ComfyUI output directory
- 🔄 **Full API Integration** with progress tracking and timeout handling
- 🔐 **Flexible API Key Management** via environment variables or node inputs

## Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

**Quick Install:**

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/yourusername/Worldlabs-Comfy.git
cd Worldlabs-Comfy
pip install -r requirements.txt
```

Then restart ComfyUI.

## Getting Started

### 1. Get Your API Key

Sign up at [World Labs](https://worldlabs.ai) and obtain your API key from the dashboard.

### 2. Set Up Your API Key

You can provide your API key in three ways:

**Option A: Environment Variable (Recommended)**
```bash
# Windows
set WORLDLABS_API_KEY=your_api_key_here

# Linux/Mac
export WORLDLABS_API_KEY=your_api_key_here
```

**Option B: Use the WorldLabsAPIKey Node**

Add a "World Labs API Key" node and enter your key directly.

**Option C: Enter Directly in Generate World Node**

Type your API key into the `api_key` field of the "Generate World" node.

### 3. Load the Example Workflow

Import `example_workflow.json` in ComfyUI to see a complete working example.

## Nodes Overview

### 1. World Labs API Key

**Purpose:** Store and provide your World Labs API key for reuse across workflows.

**Inputs:**
- `api_key` (STRING, optional): Your API key. Leave empty to use the `WORLDLABS_API_KEY` environment variable.

**Outputs:**
- `api_key` (STRING): The API key to connect to other nodes.

**Usage:**
```
WorldLabsAPIKey → WorldLabsGenerateWorld
```

---

### 2. Generate World (World Labs)

**Purpose:** The main node that uploads your image and generates a 3D world using the World Labs API.

**Inputs:**
- `image` (IMAGE, required): Input image from ComfyUI (e.g., from LoadImage node)
- `display_name` (STRING): Name for your world (default: "My World")
- `model` (DROPDOWN): Choose between:
  - `Marble 0.1-plus`: Higher quality, ~5 minutes generation time
  - `Marble 0.1-mini`: Faster, ~45 seconds generation time
- `is_panorama` (BOOLEAN): Set to true if input is a 360° panorama image
- `poll_interval` (INT, 5-60): Seconds between status checks (default: 15)
- `max_wait_time` (INT, 60-1800): Maximum wait time in seconds (default: 600)
- `api_key` (STRING, optional): API key (can be connected from WorldLabsAPIKey node)
- `text_prompt` (STRING, optional): Additional text description to guide generation

**Outputs:**
- `world_data` (WORLDLABS_WORLD): Complete world data structure (connect to other World Labs nodes)
- `world_id` (STRING): Unique ID for the generated world
- `marble_url` (STRING): Link to view your world in the Marble web UI
- `thumbnail` (IMAGE): Preview image of the generated world

**Behavior:**
1. Converts ComfyUI image to JPEG format
2. Uploads to World Labs
3. Initiates world generation
4. Polls for completion with progress updates
5. Downloads thumbnail and returns all results

**Example Settings:**
- Quick test: Use `Marble 0.1-mini` with 600s timeout
- Production: Use `Marble 0.1-plus` with 1200s timeout

---

### 3. World Info (World Labs)

**Purpose:** Extract individual asset URLs from the generated world data.

**Inputs:**
- `world_data` (WORLDLABS_WORLD): Output from Generate World node

**Outputs:**
- `splat_100k_url` (STRING): URL for 100,000 point Gaussian splat (.ply)
- `splat_500k_url` (STRING): URL for 500,000 point Gaussian splat (.ply)
- `splat_full_url` (STRING): URL for full resolution Gaussian splat (.ply)
- `mesh_url` (STRING): URL for 3D mesh in GLB format
- `pano_url` (STRING): URL for generated panorama image

**Behavior:**
- Prints all available asset URLs to the console
- Useful for manually downloading or sharing specific assets

---

### 4. Download Asset (World Labs)

**Purpose:** Download generated assets to your local ComfyUI output directory.

**Inputs:**
- `asset_url` (STRING, required): URL of the asset to download (connect from World Info node)
- `filename` (STRING, optional): Custom filename without extension (default: "world_asset")
- `subfolder` (STRING, optional): Subfolder in output directory (default: "worldlabs")

**Outputs:**
- `file_path` (STRING): Absolute path to the downloaded file

**Behavior:**
- Automatically detects file type from URL (.ply, .glb, .png, .jpg)
- Shows download progress for large files
- Creates subfolder if it doesn't exist
- Files saved to: `ComfyUI/output/worldlabs/filename.ext`

**Example:**
```
WorldLabsWorldInfo.splat_100k_url → WorldLabsDownloadAsset
```

---

### 5. 3D Viewer (World Labs)

**Purpose:** Display your generated 3D world in an interactive web viewer directly in ComfyUI.

**Inputs:**
- `world_data` (WORLDLABS_WORLD): Output from Generate World node
- `quality` (DROPDOWN): Choose quality level:
  - `100k`: Fast loading, lower detail
  - `500k`: Balanced quality and performance
  - `full_res`: Maximum quality (large file size)
- `viewer_type` (DROPDOWN): Choose viewer type:
  - `splat`: Gaussian splat viewer (PlayCanvas SuperSplat)
  - `mesh`: 3D mesh viewer (Three.js)
  - `panorama`: 360° panorama viewer (Photo Sphere Viewer)

**Outputs:**
- None (OUTPUT_NODE - displays in ComfyUI web UI)

**Behavior:**
- Generates interactive HTML viewer
- Uses CDN-hosted libraries (no local installation needed)
- Viewers support mouse/touch controls:
  - **Left click/drag**: Rotate view
  - **Right click/drag**: Pan camera
  - **Scroll wheel**: Zoom in/out

**Tips:**
- Start with `100k` quality for quick previews
- Use `splat` viewer for best quality and performance
- Use `mesh` viewer for solid 3D representation
- Use `panorama` viewer to see the full 360° environment

---

## Example Workflows

### Basic World Generation

```
LoadImage → WorldLabsGenerateWorld → WorldLabsViewer
               ↑
          WorldLabsAPIKey
```

### Complete Workflow with Download

```
LoadImage ──→ WorldLabsGenerateWorld ──→ WorldLabsWorldInfo ──→ WorldLabsDownloadAsset
                      ↑                         ↓
                 WorldLabsAPIKey           WorldLabsViewer
```

### Multiple Viewers

```
WorldLabsGenerateWorld ──┬──→ WorldLabsViewer (splat, 100k)
                         ├──→ WorldLabsViewer (mesh, 500k)
                         └──→ WorldLabsViewer (panorama, full_res)
```

## API Models

### Marble 0.1-plus
- **Quality**: High
- **Generation Time**: ~5 minutes
- **Use Case**: Production-quality 3D worlds
- **Recommended For**: Final outputs, detailed scenes

### Marble 0.1-mini
- **Quality**: Good
- **Generation Time**: ~45 seconds
- **Use Case**: Quick iterations and testing
- **Recommended For**: Workflow testing, rapid prototyping

## Output Assets

### Gaussian Splats (.ply)
- **100k**: ~5-10 MB, fast loading, good for previews
- **500k**: ~20-40 MB, balanced quality
- **Full Resolution**: ~100+ MB, maximum quality

### 3D Mesh (.glb)
- Industry-standard GLB format
- Importable into Blender, Unity, Unreal Engine, etc.
- Includes textures and materials

### Panorama (.png)
- 360° equirectangular panorama
- High resolution
- Usable in VR applications

## Troubleshooting

### "No API key provided" Error

Make sure you've set your API key via one of the three methods:
1. Environment variable `WORLDLABS_API_KEY`
2. WorldLabsAPIKey node
3. Direct input in Generate World node

### Generation Timeout

If world generation times out:
- Increase `max_wait_time` (try 1200 for Marble 0.1-plus)
- Check your internet connection
- Verify your API key is valid

### "Failed to prepare upload" Error

- Check your API key is correct
- Verify you have API credits remaining
- Check World Labs API status

### Viewer Not Loading

- Ensure you have an active internet connection (viewers use CDN libraries)
- Try a different quality level
- Check browser console for errors

### Download Fails

- Verify the asset URL is not empty
- Check disk space
- Ensure write permissions for ComfyUI output directory

## Tips & Best Practices

1. **Start Small**: Test with `Marble 0.1-mini` before using `Marble 0.1-plus`
2. **Input Images**: Works best with clear, well-lit images with good depth cues
3. **Panoramas**: For 360° input images, set `is_panorama` to true
4. **Text Prompts**: Add descriptive text prompts to guide generation
5. **Quality Settings**: Use `100k` quality for quick previews, `full_res` for final outputs
6. **Caching**: World data is preserved in the workflow - you can change viewer settings without regenerating

## API Documentation

For detailed API information, visit the [World Labs API Documentation](https://docs.worldlabs.ai/api).

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/Worldlabs-Comfy/issues)
- **API Support**: Contact World Labs support for API-related questions
- **ComfyUI Help**: Visit the [ComfyUI Discord](https://discord.gg/comfyui)

## Changelog

### Version 1.0.0
- Initial release
- Complete API integration
- 5 nodes: API Key, Generate World, World Info, Download Asset, 3D Viewer
- Support for all World Labs output formats
- Interactive web viewers using CDN libraries

## Credits

- **World Labs**: For the amazing Marble API
- **ComfyUI**: For the powerful node-based interface
- **PlayCanvas SuperSplat**: Gaussian splat viewer
- **Three.js**: 3D mesh rendering
- **Photo Sphere Viewer**: Panorama viewer

---

**Enjoy creating incredible 3D worlds from your images! 🎨🌍**
