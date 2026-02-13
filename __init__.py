"""
World Labs ComfyUI Nodes
Generate 3D worlds from images using the World Labs Marble API

Author: ComfyUI Community
License: MIT
Repository: https://github.com/yourusername/Worldlabs-Comfy
"""

from .worldlabs_comfyui_nodes import NODE_CLASS_MAPPINGS as MAIN_NODES
from .worldlabs_comfyui_nodes import NODE_DISPLAY_NAME_MAPPINGS as MAIN_DISPLAY_NAMES
from .worldlabs_viewer_node import NODE_CLASS_MAPPINGS as VIEWER_NODES
from .worldlabs_viewer_node import NODE_DISPLAY_NAME_MAPPINGS as VIEWER_DISPLAY_NAMES


# Merge all node mappings
NODE_CLASS_MAPPINGS = {
    **MAIN_NODES,
    **VIEWER_NODES,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **MAIN_DISPLAY_NAMES,
    **VIEWER_DISPLAY_NAMES,
}

# Web directory for any web assets (currently none needed)
WEB_DIRECTORY = None

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']


print("\n" + "=" * 60)
print("World Labs ComfyUI Nodes loaded successfully!")
print("=" * 60)
print("Available nodes:")
print("  • World Labs API Key")
print("  • Generate World (World Labs)")
print("  • World Info (World Labs)")
print("  • Download Asset (World Labs)")
print("  • 3D Viewer (World Labs)")
print("\nMake sure to set your WORLDLABS_API_KEY environment variable")
print("or enter it directly in the WorldLabsAPIKey node.")
print("=" * 60 + "\n")
