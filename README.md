# World Labs ComfyUI Nodes

Generate stunning 3D worlds from images using the [World Labs Marble API](https://docs.worldlabs.ai/api) directly in ComfyUI!

This custom node package integrates World Labs' cutting-edge AI technology that transforms single images into fully explorable 3D worlds, complete with Gaussian splats, 3D meshes, and panoramic views.

## Features

- 🖼️ **Generate 3D Worlds** from any image
- 🎨 **Multiple Output Formats**: Gaussian splats (.spz), 3D meshes (.glb), and panoramas
- 🌐 **Browser Viewers** - Auto-opens HTML viewers in your browser with download links and Marble viewer integration
- 📥 **Download Assets** directly to your ComfyUI output directory
- 🖼️ **Thumbnail Output** - Use the thumbnail image output directly in ComfyUI workflows
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
- `splat_100k_url` (STRING): URL for 100,000 point Gaussian splat (.spz)
- `splat_500k_url` (STRING): URL for 500,000 point Gaussian splat (.spz)
- `splat_full_url` (STRING): URL for full resolution Gaussian splat (.spz)
- `mesh_url` (STRING): URL for 3D mesh in GLB format
- `pano_url` (STRING): URL for generated panorama image (.webp)

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
- Automatically detects file type from URL (.spz, .glb, .webp, .png, .jpg)
- Shows download progress for large files
- Creates subfolder if it doesn't exist
- Files saved to: `ComfyUI/output/worldlabs/filename.ext`
- **Note:** This node has `OUTPUT_NODE = True`, so it executes even without downstream connections

**Example:**
```
WorldLabsWorldInfo.splat_100k_url → WorldLabsDownloadAsset
```

---

### 5. 3D Viewer (World Labs)

**Purpose:** Creates an HTML viewer file and automatically opens it in your default browser for viewing/downloading assets.

**Inputs:**
- `world_data` (WORLDLABS_WORLD): Output from Generate World node
- `quality` (DROPDOWN): Choose quality level:
  - `100k`: Fast loading, lower detail
  - `500k`: Balanced quality and performance
  - `full_res`: Maximum quality (large file size)
- `viewer_type` (DROPDOWN): Choose viewer type:
  - `splat`: Gaussian splat download/viewer page
  - `mesh`: 3D mesh viewer (Three.js)
  - `panorama`: 360° panorama viewer (Photo Sphere Viewer)

**Outputs:**
- None (OUTPUT_NODE - saves HTML and opens in browser)

**Behavior:**
- Generates HTML viewer file
- Saves to `ComfyUI/output/worldlabs_viewers/`
- Automatically opens in your default web browser
- Prints file path to console for later access

**For Splat Viewer:**
- Provides "View in Marble" button (opens official World Labs viewer)
- Download button for .spz file
- Copy link button to copy download URL to clipboard
- **Note:** .spz is a proprietary format best viewed in the Marble web viewer

**For Mesh/Panorama Viewers:**
- Interactive 3D/360° viewing with mouse controls
- Uses Three.js and Photo Sphere Viewer (CDN-hosted)

**Tips:**
- Use the **thumbnail output** from Generate World for static images in ComfyUI workflows
- Splat viewer provides direct links to Marble for best 3D viewing experience
- HTML files are saved so you can reopen them later from the output folder

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

### Gaussian Splats (.spz)
- **100k**: ~1-2 MB, fast loading, good for previews
- **500k**: ~5-10 MB, balanced quality
- **Full Resolution**: ~20-50 MB, maximum quality
- **Format:** Proprietary compressed format (.spz) by World Labs
- **Viewing:** Best viewed in the Marble web viewer (link provided by nodes)

### 3D Mesh (.glb)
- Industry-standard GLB format
- Importable into Blender, Unity, Unreal Engine, etc.
- Includes textures and materials
- Can be viewed in the built-in Three.js viewer

### Panorama (.webp)
- 360° equirectangular panorama
- High resolution WebP format
- Viewable in the built-in Photo Sphere viewer
- Usable in VR applications

### Thumbnail (IMAGE)
- Preview image returned directly as ComfyUI IMAGE type
- Use this for static images in your workflows
- No need for download - already available as a node output

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

### Viewer Not Opening in Browser

- Check if popup blockers are preventing the browser from opening
- Manually open the HTML file from `ComfyUI/output/worldlabs_viewers/`
- Console will print the file path if auto-open fails

### Splat Viewer Shows Download Links Only

- This is expected behavior! .spz files use a proprietary format
- Click "View in Marble" to see your world in the official viewer
- Use the Download Asset node to save .spz files locally
- Use the **thumbnail** output for static images in ComfyUI workflows

### Download Fails

- Verify the asset URL is not empty
- Check disk space
- Ensure write permissions for ComfyUI output directory

## Tips & Best Practices

1. **Use Thumbnails for Images**: The `thumbnail` output from Generate World provides a static image you can use directly in ComfyUI workflows - no need to screenshot!
2. **Start Small**: Test with `Marble 0.1-mini` before using `Marble 0.1-plus`
3. **Input Images**: Works best with clear, well-lit images with good depth cues
4. **Panoramas**: For 360° input images, set `is_panorama` to true
5. **Text Prompts**: Add descriptive text prompts to guide generation
6. **Quality Settings**: Use `100k` quality for quick previews, `full_res` for final outputs
7. **Caching**: World data is preserved in the workflow - you can change viewer/download settings without regenerating
8. **Viewing Splats**: Use the "View in Marble" button for the best interactive 3D experience with .spz files

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
- Support for all World Labs output formats (.spz, .glb, .webp)
- Browser-based viewers with auto-open functionality
- Thumbnail output for direct use in ComfyUI workflows
- Download Asset node with OUTPUT_NODE for automatic execution
- Marble viewer integration for optimal .spz viewing

## Credits

- **World Labs**: For the amazing Marble API and .spz format
- **ComfyUI**: For the powerful node-based interface
- **Three.js**: 3D mesh rendering
- **Photo Sphere Viewer**: Panorama viewer

---

**Enjoy creating incredible 3D worlds from your images! 🎨🌍**
