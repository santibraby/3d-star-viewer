"""
3D Star Viewer - Gaia Data Visualization
A Streamlit app that visualizes nearby stars in 3D using Three.js
"""

import streamlit as st
import json
import pandas as pd
from pathlib import Path
import base64
from gaia_star_fetcher import GaiaStarFetcher

# Page configuration
st.set_page_config(
    page_title="3D Star Viewer - Gaia Data",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme with Karla font
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Karla:wght@300;400;600&display=swap');
    
    /* Hide Streamlit header */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    /* Adjust main view to use full height */
    .main > div {
        padding-top: 0rem;
    }
    
    /* Main app styling */
    .stApp {
        background-color: #0a0a0a;
    }
    
    .main {
        padding-top: 0rem;
        background-color: #0a0a0a;
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        font-family: 'Karla', sans-serif !important;
        color: white !important;
    }
    
    h1 {
        text-align: center;
        font-weight: 600;
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #1f1f1f;
    }
    
    .css-1d391kg *, [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background-color: #3d3d3d;
        color: white;
        font-family: 'Karla', sans-serif;
        border: 1px solid #555;
    }
    
    .stButton>button:hover {
        background-color: #4d4d4d;
        border: 1px solid #666;
    }
    
    /* Slider styling */
    .stSlider label {
        color: white !important;
    }
    
    /* Metrics styling */
    [data-testid="metric-container"] {
        background-color: #3d3d3d;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #555;
    }
    
    [data-testid="metric-container"] label {
        color: white !important;
    }
    
    /* Info and error boxes */
    .stAlert {
        background-color: #3d3d3d;
        color: white;
        border: 1px solid #555;
    }
    
    /* Checkbox styling */
    .stCheckbox label {
        color: white !important;
        font-family: 'Karla', sans-serif !important;
    }
    
    /* Download button styling */
    .stDownloadButton>button {
        background-color: #3d3d3d;
        color: white;
        border: 1px solid #555;
    }
    
    .stDownloadButton>button:hover {
        background-color: #4d4d4d;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

def create_threejs_visualization(star_data, show_blue=True, show_white=True, show_yellow=True):
    """Create the Three.js visualization HTML"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Karla:wght@300;400&display=swap');
            body {{ 
                margin: 0; 
                overflow: hidden; 
                background: #0a0a0a; 
            }}
            #info {{
                position: absolute;
                top: 10px;
                left: 10px;
                color: white;
                font-family: 'Karla', sans-serif;
                font-size: 12px;
                font-weight: 300;
                background: rgba(61, 61, 61, 0.9);
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #555;
            }}
            #star-info {{
                position: absolute;
                bottom: 10px;
                left: 10px;
                color: white;
                font-family: 'Karla', sans-serif;
                font-size: 12px;
                font-weight: 300;
                background: rgba(61, 61, 61, 0.9);
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #555;
                display: none;
            }}
            #loading {{
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: white;
                font-family: 'Karla', sans-serif;
                font-size: 18px;
            }}
        </style>
    </head>
    <body>
        <div id="loading">Loading stars...</div>
        <div id="info">
            Left Click + Drag: Rotate | Right Click + Drag: Pan | Scroll: Zoom<br>
            Click on a star to select and orbit around it | Click empty space to reset
        </div>
        <div id="star-info"></div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
            // Star data from Python
            const starData = {json.dumps(star_data)};
            
            // Color filter states
            const showBlue = {str(show_blue).lower()};
            const showWhite = {str(show_white).lower()};
            const showYellow = {str(show_yellow).lower()};
            
            // Scene setup
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0a0a);
            
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            document.body.appendChild(renderer.domElement);
            
            // Filter stars based on temperature/color
            const filteredStars = starData.stars.filter(star => {{
                const temp = star.properties.temperature;
                if (temp > 10000 && !showBlue) return false;  // Blue stars
                if (temp >= 6000 && temp <= 10000 && !showWhite) return false;  // White stars
                if (temp < 6000 && !showYellow) return false;  // Yellow/Red stars
                return true;
            }});
            
            // Use Points for efficient rendering of many stars
            const positions = new Float32Array(filteredStars.length * 3);
            const colors = new Float32Array(filteredStars.length * 3);
            const sizes = new Float32Array(filteredStars.length);
            const starIndices = new Uint32Array(filteredStars.length);
            
            // Create mapping from filtered index to original index
            const filteredToOriginalIndex = {{}};
            
            // Populate buffers with filtered stars
            filteredStars.forEach((star, i) => {{
                // Store mapping
                const originalIndex = starData.stars.indexOf(star);
                filteredToOriginalIndex[i] = originalIndex;
                
                // Position
                positions[i * 3] = star.position.x;
                positions[i * 3 + 1] = star.position.y;
                positions[i * 3 + 2] = star.position.z;
                
                // Color - convert hex to RGB
                const color = new THREE.Color(star.properties.color);
                colors[i * 3] = color.r;
                colors[i * 3 + 1] = color.g;
                colors[i * 3 + 2] = color.b;
                
                // Size based on radius - adjusted values
                sizes[i] = Math.max(0.4, Math.min(0.8, star.properties.radius_solar * 0.05));
                
                // Store index for picking
                starIndices[i] = i;
            }});
            
            // Create BufferGeometry
            const geometry = new THREE.BufferGeometry();
            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
            geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
            
            // Create star texture for point sprites - solid circle
            const canvas = document.createElement('canvas');
            canvas.width = 32;
            canvas.height = 32;
            const ctx = canvas.getContext('2d');
            
            // Enable antialiasing
            ctx.imageSmoothingEnabled = true;
            ctx.imageSmoothingQuality = 'high';
            
            // Create a solid circle
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(16, 16, 14, 0, Math.PI * 2);
            ctx.fill();
            
            const starTexture = new THREE.CanvasTexture(canvas);
            
            // Shader for colored point sprites
            const vertexShader = `
                attribute float size;
                varying vec3 vColor;
                void main() {{
                    vColor = color;
                    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                    gl_PointSize = size * (50.0 / -mvPosition.z);
                    gl_Position = projectionMatrix * mvPosition;
                }}
            `;
            
            const fragmentShader = `
                uniform sampler2D pointTexture;
                varying vec3 vColor;
                void main() {{
                    vec4 color = vec4(vColor, 1.0) * texture2D(pointTexture, gl_PointCoord);
                    if (color.a < 0.5) discard;
                    gl_FragColor = color;
                }}
            `;
            
            // Create material
            const material = new THREE.ShaderMaterial({{
                uniforms: {{
                    pointTexture: {{ value: starTexture }}
                }},
                vertexShader: vertexShader,
                fragmentShader: fragmentShader,
                blending: THREE.NormalBlending,
                depthTest: true,
                depthWrite: false,
                vertexColors: true,
                transparent: true
            }});
            
            // Create points
            const starPoints = new THREE.Points(geometry, material);
            scene.add(starPoints);
            
            // Raycaster for picking with threshold
            const raycaster = new THREE.Raycaster();
            raycaster.params.Points.threshold = 0.1;
            const mouse = new THREE.Vector2();
            
            let selectedStarIndex = -1;
            let connectionLine = null;
            
            // Smooth transition function
            function smoothTransition(from, to, alpha) {{
                return from + (to - from) * alpha;
            }}
            
            // Create a separate geometry for the selected star
            const selectedStarGeometry = new THREE.SphereGeometry(0.05, 16, 16);
            const selectedStarMaterial = new THREE.MeshBasicMaterial({{
                color: 0xFF1493
            }});
            const selectedStarMesh = new THREE.Mesh(selectedStarGeometry, selectedStarMaterial);
            selectedStarMesh.visible = false;
            scene.add(selectedStarMesh);
            
            // Camera controls
            let isMouseDown = false;
            let mouseButton = -1;
            let mouseX = 0;
            let mouseY = 0;
            let cameraRadius = 50;
            let cameraTheta = Math.PI / 4;
            let cameraPhi = Math.PI / 4;
            let panOffset = new THREE.Vector3(0, 0, 0);
            let orbitTarget = new THREE.Vector3(0, 0, 0);
            let targetOrbitPosition = new THREE.Vector3(0, 0, 0);
            let targetRadius = 50;
            
            function updateCamera() {{
                camera.position.x = cameraRadius * Math.sin(cameraPhi) * Math.cos(cameraTheta) + orbitTarget.x + panOffset.x;
                camera.position.y = cameraRadius * Math.cos(cameraPhi) + orbitTarget.y + panOffset.y;
                camera.position.z = cameraRadius * Math.sin(cameraPhi) * Math.sin(cameraTheta) + orbitTarget.z + panOffset.z;
                camera.lookAt(orbitTarget.x + panOffset.x, orbitTarget.y + panOffset.y, orbitTarget.z + panOffset.z);
            }}
            
            // Mouse controls
            renderer.domElement.addEventListener('mousedown', (e) => {{
                isMouseDown = true;
                mouseButton = e.button;
                mouseX = e.clientX;
                mouseY = e.clientY;
                e.preventDefault();
            }});
            
            renderer.domElement.addEventListener('mouseup', () => {{
                isMouseDown = false;
            }});
            
            renderer.domElement.addEventListener('mousemove', (e) => {{
                if (isMouseDown) {{
                    const deltaX = e.clientX - mouseX;
                    const deltaY = e.clientY - mouseY;
                    
                    if (mouseButton === 0) {{
                        cameraTheta -= deltaX * 0.01;
                        cameraPhi = Math.max(0.1, Math.min(Math.PI - 0.1, cameraPhi - deltaY * 0.01));
                    }} else if (mouseButton === 2) {{
                        const panSpeed = 0.1;
                        const right = new THREE.Vector3();
                        const up = new THREE.Vector3();
                        camera.getWorldDirection(up);
                        right.crossVectors(up, camera.up).normalize();
                        
                        panOffset.add(right.multiplyScalar(-deltaX * panSpeed));
                        panOffset.add(camera.up.clone().multiplyScalar(deltaY * panSpeed));
                    }}
                    
                    mouseX = e.clientX;
                    mouseY = e.clientY;
                    updateCamera();
                }}
            }});
            
            renderer.domElement.addEventListener('wheel', (e) => {{
                targetRadius = Math.max(0.5, Math.min(2000, targetRadius + e.deltaY * 0.05));
                e.preventDefault();
            }});
            
            renderer.domElement.addEventListener('contextmenu', (e) => {{
                e.preventDefault();
            }});
            
            // Click detection
            renderer.domElement.addEventListener('click', (e) => {{
                mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
                mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
                
                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObject(starPoints);
                
                // Remove previous connection line
                if (connectionLine) {{
                    scene.remove(connectionLine);
                    connectionLine.geometry.dispose();
                    connectionLine.material.dispose();
                    connectionLine = null;
                }}
                
                if (intersects.length > 0) {{
                    const intersect = intersects[0];
                    const filteredIndex = intersect.index;
                    const originalIndex = filteredToOriginalIndex[filteredIndex];
                    selectedStarIndex = originalIndex;
                    const star = starData.stars[selectedStarIndex];
                    
                    // Set new orbit target to selected star
                    targetOrbitPosition.set(
                        star.position.x,
                        star.position.y,
                        star.position.z
                    );
                    
                    // Zoom in on the star
                    targetRadius = 2; // Zoom very close since stars are tiny
                    panOffset.set(0, 0, 0); // Reset pan when selecting new star
                    
                    // Position selected star mesh
                    selectedStarMesh.position.set(
                        star.position.x,
                        star.position.y,
                        star.position.z
                    );
                    selectedStarMesh.visible = true;
                    
                    // Create line to info box
                    const starWorldPos = new THREE.Vector3(
                        star.position.x,
                        star.position.y,
                        star.position.z
                    );
                    
                    const infoBoxX = -0.9;
                    const infoBoxY = -0.8;
                    const vector = new THREE.Vector3(infoBoxX, infoBoxY, 0.5);
                    vector.unproject(camera);
                    const dir = vector.sub(camera.position).normalize();
                    const distance = 20;
                    const infoBoxWorldPos = camera.position.clone().add(dir.multiplyScalar(distance));
                    
                    const lineGeometry = new THREE.BufferGeometry().setFromPoints([
                        starWorldPos,
                        infoBoxWorldPos
                    ]);
                    
                    const lineMaterial = new THREE.LineBasicMaterial({{
                        color: 0xFF1493,
                        opacity: 0.6,
                        transparent: true
                    }});
                    
                    connectionLine = new THREE.Line(lineGeometry, lineMaterial);
                    scene.add(connectionLine);
                    
                    // Update info display
                    const infoDiv = document.getElementById('star-info');
                    infoDiv.innerHTML = `
                        <strong>Star ID:</strong> ${{star.id}}<br>
                        <strong>Distance:</strong> ${{star.properties.distance_pc.toFixed(2)}} pc<br>
                        <strong>Temperature:</strong> ${{star.properties.temperature.toFixed(0)}} K<br>
                        <strong>Radius:</strong> ${{star.properties.radius_solar.toFixed(2)}} R☉<br>
                        <strong>Magnitude:</strong> ${{star.properties.magnitude.toFixed(2)}}<br>
                        <strong>RA/Dec:</strong> ${{star.properties.ra.toFixed(3)}}°, ${{star.properties.dec.toFixed(3)}}°
                    `;
                    infoDiv.style.display = 'block';
                }} else {{
                    // Clicking empty space - reset to origin
                    selectedStarMesh.visible = false;
                    selectedStarIndex = -1;
                    document.getElementById('star-info').style.display = 'none';
                    targetOrbitPosition.set(0, 0, 0);
                    targetRadius = 50;
                    panOffset.set(0, 0, 0);
                }}
            }});
            
            // Window resize
            window.addEventListener('resize', () => {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }});
            
            // Animation loop
            function animate() {{
                requestAnimationFrame(animate);
                
                // Smooth camera transitions
                cameraRadius = smoothTransition(cameraRadius, targetRadius, 0.1);
                orbitTarget.x = smoothTransition(orbitTarget.x, targetOrbitPosition.x, 0.1);
                orbitTarget.y = smoothTransition(orbitTarget.y, targetOrbitPosition.y, 0.1);
                orbitTarget.z = smoothTransition(orbitTarget.z, targetOrbitPosition.z, 0.1);
                updateCamera();
                
                // Update connection line if it exists
                if (connectionLine && selectedStarIndex >= 0) {{
                    const star = starData.stars[selectedStarIndex];
                    const starWorldPos = new THREE.Vector3(
                        star.position.x,
                        star.position.y,
                        star.position.z
                    );
                    
                    const infoBoxX = -0.9;
                    const infoBoxY = -0.8;
                    const vector = new THREE.Vector3(infoBoxX, infoBoxY, 0.5);
                    vector.unproject(camera);
                    const dir = vector.sub(camera.position).normalize();
                    const distance = 20;
                    const infoBoxWorldPos = camera.position.clone().add(dir.multiplyScalar(distance));
                    
                    const positions = connectionLine.geometry.attributes.position.array;
                    positions[0] = starWorldPos.x;
                    positions[1] = starWorldPos.y;
                    positions[2] = starWorldPos.z;
                    positions[3] = infoBoxWorldPos.x;
                    positions[4] = infoBoxWorldPos.y;
                    positions[5] = infoBoxWorldPos.z;
                    connectionLine.geometry.attributes.position.needsUpdate = true;
                }}
                
                renderer.render(scene, camera);
            }}
            
            // Hide loading message
            document.getElementById('loading').style.display = 'none';
            
            updateCamera();
            animate();
        </script>
    </body>
    </html>
    """
    return html_content

def main():
    st.title("3D Star Viewer - Gaia Data")
    st.markdown("Explore nearby stars in an interactive 3D visualization")

    # Color filter toggles at the top
    col1, col2, col3 = st.columns(3)
    with col1:
        show_blue = st.checkbox("Blue Stars", value=True, help="Hot stars (>10,000K)")
    with col2:
        show_white = st.checkbox("White Stars", value=True, help="Medium stars (6,000-10,000K)")
    with col3:
        show_yellow = st.checkbox("Yellow/Red Stars", value=True, help="Cool stars (<6,000K)")

    # Sidebar controls
    with st.sidebar:
        st.header("Configuration")

        num_stars = st.slider(
            "Number of stars to display",
            min_value=50,
            max_value=1000000,
            value=300,
            step=50,
            help="Select how many nearby stars to fetch and display"
        )

        max_distance = st.slider(
            "Maximum distance (parsecs)",
            min_value=10,
            max_value=1000000,
            value=30,
            step=10,
            help="Maximum distance from Earth to include stars"
        )

        fetch_button = st.button("Fetch & Visualize Stars", type="primary")

        st.markdown("---")
        st.markdown("### About the Data")
        st.markdown("""
        This app fetches real star data from the **Gaia DR3** catalog, which contains
        precise measurements of nearly 2 billion stars in our galaxy.
        
        **Star Properties:**
        - Blue stars are the hottest (>10,000K)
        - White stars are medium temperature (6,000-10,000K)
        - Yellow/Red stars are the coolest (<6,000K)
        - Size represents stellar radius
        
        **In-Viewer Controls:**
        - Toggle star colors with checkboxes (top right)
        - Real-time filtering without reloading
        - See visible/total star count
        
        **Color Categories:**
        - **Blue**: O, B, and hot A-type stars
        - **White**: Cool A and F-type stars  
        - **Yellow/Red**: G, K, and M-type stars (Sun is G-type)
        """)

    # Main content area
    if fetch_button:
        with st.spinner(f"Fetching {num_stars} stars from Gaia catalog..."):
            fetcher = GaiaStarFetcher()
            df = fetcher.fetch_nearby_stars(max_stars=num_stars, max_distance_pc=max_distance)

            if df is not None:
                # Save data
                star_data = fetcher.save_data(df)

                # Store in session state for filtering
                st.session_state.star_data = star_data

                # Display statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Stars", len(df))
                with col2:
                    st.metric("Avg Distance", f"{df['distance_pc'].mean():.1f} pc")
                with col3:
                    st.metric("Hottest Star", f"{df['temp_k'].max():.0f} K")
                with col4:
                    st.metric("Largest Star", f"{df['radius_solar'].max():.1f} R☉")

                # Create and display the 3D visualization
                html_content = create_threejs_visualization(star_data)

                # Embed the visualization
                st.components.v1.html(html_content, height=700, scrolling=False)
            else:
                st.error("Failed to fetch star data. Please try again.")
    else:
        # Show placeholder
        st.info("Use the sidebar to configure and fetch star data")

        # Display a sample image or placeholder
        st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h2>Ready to explore the cosmos?</h2>
            <p>Select the number of stars and maximum distance, then click 'Fetch & Visualize Stars'</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()