"""
World Labs ComfyUI Nodes - Interactive 3D Viewer
Provides web-based viewers for splats, meshes, and panoramas
"""

import os
import webbrowser
import folder_paths


class WorldLabsViewer:
    """
    Node to display 3D worlds in interactive web viewers
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "world_data": ("WORLDLABS_WORLD",),
                "quality": ([
                    "100k",
                    "500k",
                    "full_res"
                ], {
                    "default": "100k"
                }),
                "viewer_type": ([
                    "splat",
                    "mesh",
                    "panorama"
                ], {
                    "default": "splat"
                }),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "display_world"
    OUTPUT_NODE = True
    CATEGORY = "WorldLabs"

    def get_asset_url(self, world_data, quality, viewer_type):
        """Get the appropriate asset URL based on quality and viewer type"""
        assets = world_data.get("assets", {})

        if viewer_type == "splat":
            # Splats are under assets.splats.spz_urls
            splats = assets.get("splats", {})
            spz_urls = splats.get("spz_urls", {})
            return spz_urls.get(quality, "")

        elif viewer_type == "mesh":
            # Mesh is under assets.mesh.collider_mesh_url
            mesh = assets.get("mesh", {})
            return mesh.get("collider_mesh_url", "")

        elif viewer_type == "panorama":
            # Panorama is under assets.imagery.pano_url
            imagery = assets.get("imagery", {})
            return imagery.get("pano_url", "")

        return ""

    def create_splat_viewer_html(self, asset_url, world_name, marble_url=""):
        """Create HTML for Gaussian Splat viewer with download and copy options"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>World Labs Splat Viewer - {world_name}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
        }}
        #container {{
            width: 100vw;
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 20px;
            box-sizing: border-box;
        }}
        #message {{
            background: rgba(0, 0, 0, 0.5);
            padding: 40px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            max-width: 600px;
        }}
        h1 {{
            margin: 0 0 20px 0;
            font-size: 28px;
        }}
        p {{
            margin: 15px 0;
            line-height: 1.6;
            opacity: 0.9;
        }}
        .btn {{
            display: inline-block;
            margin: 10px;
            padding: 12px 30px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            transition: background 0.3s;
            cursor: pointer;
            border: none;
            font-size: 16px;
        }}
        .btn:hover {{
            background: #5568d3;
        }}
        .btn-secondary {{
            background: #34495e;
        }}
        .btn-secondary:hover {{
            background: #2c3e50;
        }}
        .note {{
            margin-top: 30px;
            font-size: 14px;
            opacity: 0.7;
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="message">
            <h1>🌍 {world_name}</h1>
            <p><strong>Gaussian Splat File Ready</strong></p>
            <p>World Labs uses a proprietary .spz format. Use the options below to view or download your 3D world.</p>

            <div style="margin: 30px 0;">
                {"<a href='" + marble_url + "' class='btn' target='_blank'>🌐 View in Marble</a>" if marble_url else ""}
                <a href="{asset_url}" class="btn btn-secondary" download>📥 Download .spz File</a>
                <button onclick="copyToClipboard()" class="btn btn-secondary">📋 Copy Link</button>
            </div>

            <p class="note">
                <strong>💡 Tip for ComfyUI Users:</strong><br>
                The <strong>thumbnail</strong> output from the Generate World node provides a static image preview you can use directly in workflows!<br><br>
                <strong>Download Options:</strong><br>
                • Use WorldLabsDownloadAsset node to download .spz files<br>
                • View interactively in the Marble web viewer above
            </p>
        </div>
    </div>

    <script>
        function copyToClipboard() {{
            const url = '{asset_url}';
            navigator.clipboard.writeText(url).then(() => {{
                alert('Download link copied to clipboard!');
            }}).catch(err => {{
                console.error('Failed to copy:', err);
                prompt('Copy this URL:', url);
            }});
        }}
    </script>
</body>
</html>
"""

    def create_mesh_viewer_html(self, asset_url, world_name):
        """Create HTML for Three.js mesh viewer"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>World Labs Mesh Viewer - {world_name}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        #container {{
            width: 100vw;
            height: 100vh;
            position: relative;
        }}
        #info {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 14px;
            z-index: 100;
        }}
        #loading {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 20px;
            text-align: center;
            z-index: 100;
        }}
        .spinner {{
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="info">
            <strong>{world_name}</strong><br>
            3D Mesh Viewer<br>
            <small>Left click: Rotate | Right click: Pan | Scroll: Zoom</small>
        </div>
        <div id="loading">
            <div class="spinner"></div>
            Loading 3D Mesh...
        </div>
    </div>

    <script type="importmap">
    {{
        "imports": {{
            "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
            "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
        }}
    }}
    </script>

    <script type="module">
        import * as THREE from 'three';
        import {{ GLTFLoader }} from 'three/addons/loaders/GLTFLoader.js';
        import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

        const container = document.getElementById('container');
        const loading = document.getElementById('loading');

        // Setup scene
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x667eea);

        // Setup camera
        const camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        camera.position.set(0, 1, 3);

        // Setup renderer
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.shadowMap.enabled = true;
        container.appendChild(renderer.domElement);

        // Setup controls
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;

        // Add lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 5, 5);
        directionalLight.castShadow = true;
        scene.add(directionalLight);

        const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
        directionalLight2.position.set(-5, 3, -5);
        scene.add(directionalLight2);

        // Load GLB model
        const loader = new GLTFLoader();
        const assetUrl = '{asset_url}';

        loader.load(
            assetUrl,
            (gltf) => {{
                const model = gltf.scene;

                // Center the model
                const box = new THREE.Box3().setFromObject(model);
                const center = box.getCenter(new THREE.Vector3());
                model.position.sub(center);

                // Scale to fit
                const size = box.getSize(new THREE.Vector3());
                const maxDim = Math.max(size.x, size.y, size.z);
                const scale = 2 / maxDim;
                model.scale.multiplyScalar(scale);

                scene.add(model);
                loading.style.display = 'none';

                console.log('Model loaded successfully');
            }},
            (progress) => {{
                const percent = (progress.loaded / progress.total) * 100;
                console.log(`Loading: ${{percent.toFixed(0)}}%`);
            }},
            (error) => {{
                console.error('Error loading model:', error);
                loading.innerHTML = '<div style="color: red;">Error loading mesh file</div>';
            }}
        );

        // Animation loop
        function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }}
        animate();

        // Handle window resize
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>
"""

    def create_panorama_viewer_html(self, asset_url, world_name):
        """Create HTML for Photo Sphere Viewer"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>World Labs Panorama Viewer - {world_name}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@photo-sphere-viewer/core@5/index.min.css"/>
    <style>
        body {{
            margin: 0;
            padding: 0;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }}
        #viewer {{
            width: 100vw;
            height: 100vh;
        }}
        #info {{
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 14px;
            z-index: 100;
        }}
    </style>
</head>
<body>
    <div id="viewer"></div>
    <div id="info">
        <strong>{world_name}</strong><br>
        360° Panorama<br>
        <small>Drag to look around | Scroll to zoom</small>
    </div>

    <script type="module">
        import {{ Viewer }} from 'https://cdn.jsdelivr.net/npm/@photo-sphere-viewer/core@5/index.module.js';

        const viewer = new Viewer({{
            container: document.querySelector('#viewer'),
            panorama: '{asset_url}',
            navbar: [
                'zoom',
                'fullscreen',
            ],
            defaultZoomLvl: 50,
            mousewheel: true,
            mousemove: true,
            loadingTxt: 'Loading panorama...',
        }});

        viewer.addEventListener('ready', () => {{
            console.log('Panorama loaded successfully');
        }});

        viewer.addEventListener('error', (error) => {{
            console.error('Error loading panorama:', error);
        }});
    </script>
</body>
</html>
"""

    def display_world(self, world_data, quality, viewer_type):
        """Generate HTML viewer and save to file, then open in browser"""
        marble_url = world_data.get("world_marble_url", "")
        world_id = world_data.get("world_id", "")
        world_name = world_data.get("display_name", "World Labs 3D World")

        # Get output directory and create viewer subfolder
        output_dir = folder_paths.get_output_directory()
        viewer_dir = os.path.join(output_dir, "worldlabs_viewers")
        os.makedirs(viewer_dir, exist_ok=True)

        # Generate filename
        safe_name = "".join(c for c in world_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')
        html_filename = f"{safe_name}_{viewer_type}_{quality}_{world_id[:8]}.html"
        html_path = os.path.join(viewer_dir, html_filename)

        asset_url = self.get_asset_url(world_data, quality, viewer_type)

        if not asset_url:
            print(f"\n[WorldLabs] Warning: No asset URL found for {viewer_type} at quality {quality}")
            print(f"[WorldLabs] Available assets: {world_data.get('assets', {}).keys()}")

            # Create error page with Marble link
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>View in Marble</title>
    <style>
        body {{
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .message {{
            text-align: center;
            padding: 40px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            backdrop-filter: blur(10px);
            max-width: 500px;
        }}
        h2 {{
            margin: 0 0 20px 0;
            font-size: 24px;
        }}
        p {{
            margin: 10px 0;
            line-height: 1.6;
        }}
        a {{
            display: inline-block;
            margin-top: 20px;
            padding: 12px 30px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            transition: background 0.3s;
        }}
        a:hover {{
            background: #5568d3;
        }}
        .note {{
            margin-top: 20px;
            font-size: 12px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="message">
        <h2>🌍 View Your 3D World</h2>
        <p>The requested {viewer_type} asset at quality {quality} is not available for this world.</p>
        {"<p><strong>View your world in the Marble web viewer:</strong></p><a href='" + marble_url + "' target='_blank'>Open in Marble 🚀</a>" if marble_url else ""}
        <p class="note">Tip: Try a different viewer type or quality setting.</p>
    </div>
</body>
</html>
"""
        else:
            # Generate appropriate viewer HTML
            if viewer_type == "splat":
                html = self.create_splat_viewer_html(asset_url, world_name, marble_url)
            elif viewer_type == "mesh":
                html = self.create_mesh_viewer_html(asset_url, world_name)
            elif viewer_type == "panorama":
                html = self.create_panorama_viewer_html(asset_url, world_name)
            else:
                html = "<html><body><h1>Unknown viewer type</h1></body></html>"

        # Save HTML file
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

        # Print viewing information
        print("\n" + "=" * 70)
        print("🌍 3D VIEWER READY")
        print("=" * 70)
        print(f"   Viewer Type: {viewer_type.upper()}")
        print(f"   Quality: {quality}")
        print(f"   World: {world_name}")
        if marble_url:
            print(f"   Marble URL: {marble_url}")
        print(f"\n   📁 Saved to: {html_path}")
        print("=" * 70 + "\n")

        # Open in browser
        try:
            webbrowser.open('file://' + os.path.abspath(html_path))
            print(f"[WorldLabs] Opening {viewer_type} viewer in your default browser...")
        except Exception as e:
            print(f"[WorldLabs] Could not auto-open browser: {e}")
            print(f"[WorldLabs] Please open manually: {html_path}")

        return {}


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "WorldLabsViewer": WorldLabsViewer,
}

# Display names
NODE_DISPLAY_NAME_MAPPINGS = {
    "WorldLabsViewer": "3D Viewer (World Labs)",
}
