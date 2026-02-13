"""
World Labs ComfyUI Nodes - Main Generation Nodes
Implements API integration for generating 3D worlds from images
"""

import os
import time
import io
import requests
import numpy as np
from PIL import Image
import folder_paths


# API Configuration
BASE_URL = "https://api.worldlabs.ai/marble/v1"


class WorldLabsAPIKey:
    """
    Node to store and provide World Labs API key
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Leave empty to use WORLDLABS_API_KEY environment variable"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("api_key",)
    FUNCTION = "get_api_key"
    CATEGORY = "WorldLabs"

    def get_api_key(self, api_key=""):
        """Get API key from input or environment variable"""
        if api_key and api_key.strip():
            return (api_key.strip(),)

        env_key = os.getenv("WORLDLABS_API_KEY", "")
        if not env_key:
            raise ValueError(
                "No API key provided. Either:\n"
                "1. Enter API key in the node, OR\n"
                "2. Set WORLDLABS_API_KEY environment variable"
            )

        return (env_key,)


class WorldLabsGenerateWorld:
    """
    Main node to generate 3D worlds from images using World Labs API
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "display_name": ("STRING", {
                    "default": "My World",
                    "multiline": False
                }),
                "model": ([
                    "Marble 0.1-plus",
                    "Marble 0.1-mini"
                ], {
                    "default": "Marble 0.1-mini"
                }),
                "is_panorama": ("BOOLEAN", {
                    "default": False
                }),
                "poll_interval": ("INT", {
                    "default": 15,
                    "min": 5,
                    "max": 60,
                    "step": 1
                }),
                "max_wait_time": ("INT", {
                    "default": 600,
                    "min": 60,
                    "max": 1800,
                    "step": 10
                }),
            },
            "optional": {
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "text_prompt": ("STRING", {
                    "default": "",
                    "multiline": True
                }),
            }
        }

    RETURN_TYPES = ("WORLDLABS_WORLD", "STRING", "STRING", "IMAGE")
    RETURN_NAMES = ("world_data", "world_id", "marble_url", "thumbnail")
    FUNCTION = "generate_world"
    CATEGORY = "WorldLabs"

    def get_api_key(self, api_key=""):
        """Get API key from input or environment variable"""
        if api_key and api_key.strip():
            return api_key.strip()

        env_key = os.getenv("WORLDLABS_API_KEY", "")
        if not env_key:
            raise ValueError(
                "No API key provided. Either:\n"
                "1. Connect from WorldLabsAPIKey node, OR\n"
                "2. Enter API key in this node, OR\n"
                "3. Set WORLDLABS_API_KEY environment variable"
            )

        return env_key

    def convert_image_to_bytes(self, image_tensor):
        """
        Convert ComfyUI image tensor to JPEG bytes
        Input: [B, H, W, C] float32 tensor with values 0.0-1.0
        Output: JPEG bytes
        """
        # Take first image if batch
        if len(image_tensor.shape) == 4:
            image_tensor = image_tensor[0]

        # Convert from float [0, 1] to uint8 [0, 255]
        image_np = (image_tensor.cpu().numpy() * 255).astype(np.uint8)

        # Convert to PIL Image
        pil_image = Image.fromarray(image_np)

        # Convert to JPEG bytes
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)

        return buffer.getvalue()

    def convert_bytes_to_image(self, image_bytes):
        """
        Convert image bytes to ComfyUI image tensor
        Output: [1, H, W, C] float32 tensor with values 0.0-1.0
        """
        pil_image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if needed
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # Convert to numpy array and normalize to [0, 1]
        image_np = np.array(pil_image).astype(np.float32) / 255.0

        # Add batch dimension [H, W, C] -> [1, H, W, C]
        image_tensor = np.expand_dims(image_np, axis=0)

        return image_tensor

    def prepare_upload(self, api_key, filename="image.jpg"):
        """Step 1: Prepare upload and get signed URL"""
        url = f"{BASE_URL}/media-assets:prepare_upload"
        headers = {
            "WLT-Api-Key": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "file_name": filename,
            "kind": "image",
            "extension": "jpg"
        }

        print(f"[WorldLabs] Preparing upload for {filename}...")
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to prepare upload: {response.status_code} - {response.text}")

        data = response.json()

        # Extract nested data from actual API response structure
        if "media_asset" not in data or "upload_info" not in data:
            raise Exception(
                f"Unexpected API response structure. "
                f"Received keys: {list(data.keys())}. "
                f"Full response: {data}"
            )

        media_asset_id = data["media_asset"]["media_asset_id"]
        upload_url = data["upload_info"]["upload_url"]
        required_headers = data["upload_info"].get("required_headers", {})

        print(f"[WorldLabs] Media Asset ID: {media_asset_id}")

        return media_asset_id, upload_url, required_headers

    def upload_image(self, upload_url, image_bytes, required_headers=None):
        """Step 2: Upload image to signed URL"""
        print(f"[WorldLabs] Uploading image ({len(image_bytes)} bytes)...")

        # Build headers
        headers = {"Content-Type": "image/jpeg"}
        if required_headers:
            headers.update(required_headers)

        response = requests.put(
            upload_url,
            data=image_bytes,
            headers=headers
        )

        if response.status_code != 200:
            raise Exception(f"Failed to upload image: {response.status_code} - {response.text}")

        print("[WorldLabs] Image uploaded successfully")

    def start_generation(self, api_key, media_asset_id, display_name, model, is_panorama, text_prompt=""):
        """Step 3: Start world generation"""
        url = f"{BASE_URL}/worlds:generate"
        headers = {
            "WLT-Api-Key": api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "display_name": display_name,
            "model": model,
            "world_prompt": {
                "type": "image",
                "image_prompt": {
                    "source": "media_asset",
                    "media_asset_id": media_asset_id,
                    "is_pano": is_panorama
                }
            }
        }

        if text_prompt and text_prompt.strip():
            payload["world_prompt"]["text_prompt"] = text_prompt.strip()

        print(f"[WorldLabs] Starting world generation with {model}...")
        print(f"[WorldLabs] Display name: {display_name}")
        if text_prompt:
            print(f"[WorldLabs] Text prompt: {text_prompt}")
        print(f"[WorldLabs] Panorama mode: {is_panorama}")

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to start generation: {response.status_code} - {response.text}")

        data = response.json()

        # Debug: Print response
        print(f"[WorldLabs] Generation API Response: {data}")

        # Check for operation_id
        if "operation_id" not in data:
            raise Exception(
                f"API response missing 'operation_id'. "
                f"Received keys: {list(data.keys())}. "
                f"Full response: {data}"
            )

        operation_id = data["operation_id"]

        print(f"[WorldLabs] Generation started. Operation ID: {operation_id}")

        return operation_id

    def poll_operation(self, api_key, operation_id, poll_interval, max_wait_time):
        """Step 4: Poll for completion"""
        url = f"{BASE_URL}/operations/{operation_id}"
        headers = {
            "WLT-Api-Key": api_key
        }

        start_time = time.time()
        last_progress = -1

        while True:
            elapsed = time.time() - start_time

            if elapsed > max_wait_time:
                raise TimeoutError(
                    f"World generation timed out after {max_wait_time} seconds. "
                    f"Operation ID: {operation_id}"
                )

            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                raise Exception(f"Failed to poll operation: {response.status_code} - {response.text}")

            data = response.json()

            # Show progress if available
            if "progress" in data and data["progress"] != last_progress:
                last_progress = data["progress"]
                print(f"[WorldLabs] Progress: {last_progress}%")

            if data.get("done", False):
                print("[WorldLabs] Generation complete!")

                # Check if there's an actual error (not None)
                error = data.get("error")
                if error is not None and error:
                    raise Exception(f"Generation failed: {error}")

                # Check if we have response data
                if "response" not in data or data["response"] is None:
                    raise Exception(
                        f"Generation completed but no response data received. "
                        f"Full response: {data}"
                    )

                return data["response"]

            print(f"[WorldLabs] Waiting... ({int(elapsed)}s elapsed)")
            time.sleep(poll_interval)

    def download_thumbnail(self, thumbnail_url):
        """Download thumbnail and convert to ComfyUI image"""
        print("[WorldLabs] Downloading thumbnail...")

        response = requests.get(thumbnail_url)

        if response.status_code != 200:
            print(f"[WorldLabs] Warning: Failed to download thumbnail: {response.status_code}")
            # Return blank image
            blank = np.zeros((256, 256, 3), dtype=np.float32)
            return np.expand_dims(blank, axis=0)

        return self.convert_bytes_to_image(response.content)

    def generate_world(self, image, display_name, model, is_panorama, poll_interval, max_wait_time,
                      api_key="", text_prompt=""):
        """Main function to orchestrate world generation"""
        try:
            # Get API key
            actual_api_key = self.get_api_key(api_key)

            # Convert image to bytes
            image_bytes = self.convert_image_to_bytes(image)

            # Step 1: Prepare upload
            media_asset_id, upload_url, required_headers = self.prepare_upload(actual_api_key)

            # Step 2: Upload image
            self.upload_image(upload_url, image_bytes, required_headers)

            # Step 3: Start generation
            operation_id = self.start_generation(
                actual_api_key,
                media_asset_id,
                display_name,
                model,
                is_panorama,
                text_prompt
            )

            # Step 4: Poll for completion
            world_data = self.poll_operation(
                actual_api_key,
                operation_id,
                poll_interval,
                max_wait_time
            )

            # Extract key information
            world_id = world_data.get("world_id", "")
            marble_url = world_data.get("marble_url", "")

            # Download thumbnail
            thumbnail_url = world_data.get("thumbnail_url", "")
            if thumbnail_url:
                thumbnail = self.download_thumbnail(thumbnail_url)
            else:
                # Create blank thumbnail
                blank = np.zeros((256, 256, 3), dtype=np.float32)
                thumbnail = np.expand_dims(blank, axis=0)

            print(f"[WorldLabs] World ID: {world_id}")
            print(f"[WorldLabs] Marble URL: {marble_url}")
            print("[WorldLabs] ✓ World generation complete!")

            return (world_data, world_id, marble_url, thumbnail)

        except Exception as e:
            print(f"[WorldLabs] ✗ Error: {str(e)}")
            raise


class WorldLabsWorldInfo:
    """
    Node to extract asset URLs from world data
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "world_data": ("WORLDLABS_WORLD",),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("splat_100k_url", "splat_500k_url", "splat_full_url", "mesh_url", "pano_url")
    FUNCTION = "extract_urls"
    CATEGORY = "WorldLabs"

    def extract_urls(self, world_data):
        """Extract asset URLs from world data"""
        assets = world_data.get("assets", {})

        # Extract URLs from actual API structure
        # Splats are under assets.splats.spz_urls
        splats = assets.get("splats", {})
        spz_urls = splats.get("spz_urls", {})
        splat_100k = spz_urls.get("100k", "")
        splat_500k = spz_urls.get("500k", "")
        splat_full = spz_urls.get("full_res", "")

        # Mesh is under assets.mesh.collider_mesh_url
        mesh_data = assets.get("mesh", {})
        mesh = mesh_data.get("collider_mesh_url", "")

        # Panorama is under assets.imagery.pano_url
        imagery = assets.get("imagery", {})
        pano = imagery.get("pano_url", "")

        # Print info
        print("\n[WorldLabs] World Assets:")
        print("=" * 60)
        if splat_100k:
            print(f"  Splat 100k: {splat_100k}")
        if splat_500k:
            print(f"  Splat 500k: {splat_500k}")
        if splat_full:
            print(f"  Splat Full: {splat_full}")
        if mesh:
            print(f"  Mesh (GLB): {mesh}")
        if pano:
            print(f"  Panorama:   {pano}")
        print("=" * 60 + "\n")

        return (splat_100k, splat_500k, splat_full, mesh, pano)


class WorldLabsDownloadAsset:
    """
    Node to download assets from URLs
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "asset_url": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
            },
            "optional": {
                "filename": ("STRING", {
                    "default": "world_asset",
                    "multiline": False
                }),
                "subfolder": ("STRING", {
                    "default": "worldlabs",
                    "multiline": False
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("file_path",)
    FUNCTION = "download_asset"
    OUTPUT_NODE = True
    CATEGORY = "WorldLabs"

    def download_asset(self, asset_url, filename="world_asset", subfolder="worldlabs"):
        """Download asset from URL to ComfyUI output directory"""
        if not asset_url or not asset_url.strip():
            raise ValueError("Asset URL is empty")

        # Get output directory
        output_dir = folder_paths.get_output_directory()

        # Create subfolder if needed
        if subfolder:
            output_dir = os.path.join(output_dir, subfolder)
            os.makedirs(output_dir, exist_ok=True)

        # Determine file extension from URL
        url_lower = asset_url.lower()
        if '.spz' in url_lower:
            ext = '.spz'
        elif '.ply' in url_lower:
            ext = '.ply'
        elif '.glb' in url_lower or '.gltf' in url_lower:
            ext = '.glb'
        elif '.png' in url_lower:
            ext = '.png'
        elif '.jpg' in url_lower or '.jpeg' in url_lower:
            ext = '.jpg'
        elif '.webp' in url_lower:
            ext = '.webp'
        else:
            ext = '.bin'

        # Add extension if not present
        if not filename.endswith(ext):
            filename = filename + ext

        file_path = os.path.join(output_dir, filename)

        print(f"[WorldLabs] Downloading asset...")
        print(f"[WorldLabs] URL: {asset_url}")
        print(f"[WorldLabs] Destination: {file_path}")

        # Download file
        response = requests.get(asset_url, stream=True)

        if response.status_code != 200:
            raise Exception(f"Failed to download asset: {response.status_code} - {response.text}")

        # Get file size if available
        total_size = int(response.headers.get('content-length', 0))

        # Write to file
        downloaded = 0
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    # Show progress for large files
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        if progress % 10 < 1:  # Print every ~10%
                            print(f"[WorldLabs] Progress: {progress:.0f}%")

        print(f"[WorldLabs] ✓ Asset downloaded successfully ({downloaded} bytes)")
        print(f"[WorldLabs] Saved to: {file_path}")

        return (file_path,)


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "WorldLabsAPIKey": WorldLabsAPIKey,
    "WorldLabsGenerateWorld": WorldLabsGenerateWorld,
    "WorldLabsWorldInfo": WorldLabsWorldInfo,
    "WorldLabsDownloadAsset": WorldLabsDownloadAsset,
}

# Display names
NODE_DISPLAY_NAME_MAPPINGS = {
    "WorldLabsAPIKey": "World Labs API Key",
    "WorldLabsGenerateWorld": "Generate World (World Labs)",
    "WorldLabsWorldInfo": "World Info (World Labs)",
    "WorldLabsDownloadAsset": "Download Asset (World Labs)",
}
