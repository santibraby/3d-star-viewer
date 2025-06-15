"""
3D Star Viewer - Gaia Data Visualization
A Streamlit app that visualizes nearby stars in 3D using Three.js
"""

import streamlit as st
import json
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

def create_threejs_visualization(star_data):
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
        </style>
    </head>
    <body>
        <div id="info">
            Left Click + Drag: Rotate | Right Click + Drag: Pan | Scroll: Zoom<br>
            Click on a star for details
        </div>
        <div id="star-info"></div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script>
            // Star data from Python
            const starData = {json.dumps(star_data)};
            
            // Scene setup
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0a0a0a); // Very dark grey, almost black
            
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({{ antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);
            
            // Add stars to scene
            const starGroup = new THREE.Group();
            const starMeshes = [];
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();
            let selectedStar = null;
            let originalMaterial = null;
            let connectionLine = null;
            
            starData.stars.forEach((star, index) => {{
                // Create sphere geometry for each star - scaled down by 1/10
                const radius = Math.max(0.01, Math.min(0.2, star.properties.radius_solar * 0.03));
                const geometry = new THREE.SphereGeometry(radius, 16, 16);
                
                // Create material with star color
                const material = new THREE.MeshBasicMaterial({{
                    color: star.properties.color,
                    emissive: star.properties.color,
                    emissiveIntensity: 1
                }});
                
                const mesh = new THREE.Mesh(geometry, material);
                mesh.position.set(star.position.x, star.position.y, star.position.z);
                mesh.userData = star;
                
                starGroup.add(mesh);
                starMeshes.push(mesh);
            }});
            
            scene.add(starGroup);
            
            // Add some ambient light
            const ambientLight = new THREE.AmbientLight(0x404040);
            scene.add(ambientLight);
            
            // Camera position
            camera.position.set(30, 30, 30);
            camera.lookAt(0, 0, 0);
            
            // Controls
            let isMouseDown = false;
            let mouseButton = -1;
            let mouseX = 0;
            let mouseY = 0;
            let cameraRadius = 50;
            let cameraTheta = Math.PI / 4;
            let cameraPhi = Math.PI / 4;
            let panOffset = new THREE.Vector3(0, 0, 0);
            
            function updateCamera() {{
                camera.position.x = cameraRadius * Math.sin(cameraPhi) * Math.cos(cameraTheta) + panOffset.x;
                camera.position.y = cameraRadius * Math.cos(cameraPhi) + panOffset.y;
                camera.position.z = cameraRadius * Math.sin(cameraPhi) * Math.sin(cameraTheta) + panOffset.z;
                camera.lookAt(panOffset);
            }}
            
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
                    
                    if (mouseButton === 0) {{ // Left click - rotate
                        cameraTheta -= deltaX * 0.01;
                        cameraPhi = Math.max(0.1, Math.min(Math.PI - 0.1, cameraPhi - deltaY * 0.01));
                    }} else if (mouseButton === 2) {{ // Right click - pan
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
                cameraRadius = Math.max(5, Math.min(200, cameraRadius + e.deltaY * 0.05));
                updateCamera();
                e.preventDefault();
            }});
            
            renderer.domElement.addEventListener('contextmenu', (e) => {{
                e.preventDefault();
            }});
            
            // Click detection for star info and hot pink selection
            renderer.domElement.addEventListener('click', (e) => {{
                mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
                mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
                
                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(starMeshes);
                
                // Reset previous selection
                if (selectedStar && originalMaterial) {{
                    selectedStar.material = originalMaterial;
                }}
                
                // Remove previous connection line
                if (connectionLine) {{
                    scene.remove(connectionLine);
                    connectionLine.geometry.dispose();
                    connectionLine.material.dispose();
                    connectionLine = null;
                }}
                
                if (intersects.length > 0) {{
                    const clickedStar = intersects[0].object;
                    const star = clickedStar.userData;
                    
                    // Store original material and create hot pink material
                    originalMaterial = clickedStar.material;
                    selectedStar = clickedStar;
                    
                    // Create hot pink material for selection
                    clickedStar.material = new THREE.MeshBasicMaterial({{
                        color: 0xFF1493,  // Hot pink
                        emissive: 0xFF1493,
                        emissiveIntensity: 1
                    }});
                    
                    // Create line from star to info box
                    const starWorldPos = new THREE.Vector3();
                    clickedStar.getWorldPosition(starWorldPos);
                    
                    // Convert info box position to 3D world coordinates
                    const infoBoxX = -0.9; // Left side of screen in normalized coords
                    const infoBoxY = -0.8; // Bottom of screen in normalized coords
                    
                    const vector = new THREE.Vector3(infoBoxX, infoBoxY, 0.5);
                    vector.unproject(camera);
                    const dir = vector.sub(camera.position).normalize();
                    const distance = 20; // Fixed distance from camera
                    const infoBoxWorldPos = camera.position.clone().add(dir.multiplyScalar(distance));
                    
                    // Create line geometry
                    const lineGeometry = new THREE.BufferGeometry().setFromPoints([
                        starWorldPos,
                        infoBoxWorldPos
                    ]);
                    
                    // Create line material
                    const lineMaterial = new THREE.LineBasicMaterial({{
                        color: 0xFF1493, // Hot pink to match selected star
                        opacity: 0.6,
                        transparent: true
                    }});
                    
                    // Create and add line to scene
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
                
                // Update connection line if it exists
                if (connectionLine && selectedStar) {{
                    const starWorldPos = new THREE.Vector3();
                    selectedStar.getWorldPosition(starWorldPos);
                    
                    // Recalculate info box position based on current camera
                    const infoBoxX = -0.9;
                    const infoBoxY = -0.8;
                    const vector = new THREE.Vector3(infoBoxX, infoBoxY, 0.5);
                    vector.unproject(camera);
                    const dir = vector.sub(camera.position).normalize();
                    const distance = 20;
                    const infoBoxWorldPos = camera.position.clone().add(dir.multiplyScalar(distance));
                    
                    // Update line positions
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
        - Blue stars are the hottest
        - Yellow stars (like our Sun)
        - Red stars are the coolest
        - Size represents stellar radius
        """)

    # Main content area
    if fetch_button:
        # Warning for very large queries
        if num_stars > 100000:
            st.warning("Large queries may take several minutes and could timeout. Consider starting with a smaller number of stars.")

        with st.spinner(f"Fetching {num_stars} stars from Gaia catalog..."):
            fetcher = GaiaStarFetcher()
            df = fetcher.fetch_nearby_stars(max_stars=num_stars, max_distance_pc=max_distance)

            if df is not None:
                # Save data
                star_data = fetcher.save_data(df)

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
                st.components.v1.html(html_content, height=600, scrolling=False)

                # Download options
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    with open("data/star_data.json", "r") as f:
                        st.download_button(
                            label="Download JSON Data",
                            data=f.read(),
                            file_name="star_data.json",
                            mime="application/json"
                        )
                with col2:
                    with open("data/star_data.csv", "r") as f:
                        st.download_button(
                            label="Download CSV Data",
                            data=f.read(),
                            file_name="star_data.csv",
                            mime="text/csv"
                        )
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