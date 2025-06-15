# 🌟 3D Star Viewer - Gaia Data Visualization

An interactive 3D visualization of nearby stars using real data from the Gaia space telescope. Built with Streamlit, Three.js, and Astropy.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Features

- Fetches real star data from the ESA Gaia DR3 catalog
- Interactive 3D visualization using Three.js
- Color-coded stars based on temperature
- Star sizes represent actual stellar radii
- Click on stars to see detailed information
- Adjustable parameters for number of stars and distance range
- Export data as JSON or CSV

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- GitHub account
- Streamlit Cloud account (free)

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/3d-star-viewer.git
cd 3d-star-viewer
```

### 2. Create a virtual environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create data directory

```bash
mkdir data
```

## 💻 Local Development

### Running the Gaia data fetcher standalone

```bash
python gaia_star_fetcher.py
```

### Running the Streamlit app

```bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## 📤 GitHub Setup

### 1. Initialize Git repository

```bash
git init
git add .
git commit -m "Initial commit: 3D star viewer with Gaia data"
```

### 2. Create GitHub repository

1. Go to [GitHub](https://github.com/new)
2. Create a new repository named `3d-star-viewer`
3. Don't initialize with README (we already have one)

### 3. Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/3d-star-viewer.git
git branch -M main
git push -u origin main
```

## 🌐 Streamlit Cloud Deployment

### 1. Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"

### 2. Deploy the app

1. Select your repository: `YOUR_USERNAME/3d-star-viewer`
2. Branch: `main`
3. Main file path: `streamlit_app.py`
4. Click "Deploy"

### 3. Wait for deployment

The app will take a few minutes to deploy. Once ready, you'll get a URL like:
`https://your-app-name.streamlit.app`

## 📁 Project Structure

```
3d-star-viewer/
│
├── gaia_star_fetcher.py    # Core module for fetching Gaia data
├── streamlit_app.py        # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore file
├── README.md              # This file
└── data/                  # Directory for star data (git ignored)
    ├── star_data.json     # JSON format for Three.js
    └── star_data.csv      # CSV format for analysis
```

## 🎮 Usage

1. **Select Parameters**: Use the sidebar to choose:
   - Number of stars (50-2000)
   - Maximum distance in parsecs (10-100)

2. **Fetch Data**: Click "Fetch & Visualize Stars"

3. **Interact with Visualization**:
   - Left click + drag: Rotate view
   - Right click + drag: Pan view
   - Scroll: Zoom in/out
   - Click on a star: View details

4. **Export Data**: Download the data as JSON or CSV

## 🔧 Configuration

### Modifying star colors

Edit the `_temp_to_color` method in `gaia_star_fetcher.py`:

```python
def _temp_to_color(self, temp):
    if temp > 30000:
        return "#9bb0ff"  # O-type: blue
    # ... etc
```

### Adjusting visualization settings

Modify the Three.js parameters in `streamlit_app.py`:

```javascript
const radius = Math.max(0.1, Math.min(2, star.properties.radius_solar * 0.3));
```

## 📊 Data Sources

This project uses data from:
- [ESA Gaia Archive](https://gea.esac.esa.int/archive/)
- Gaia Data Release 3 (DR3)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- ESA Gaia mission for providing the stellar data
- Astropy community for the excellent astronomy tools
- Streamlit team for the amazing web framework
- Three.js for the 3D visualization library

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'astroquery'"**
   ```bash
   pip install --upgrade astroquery
   ```

2. **Gaia query timeout**
   - Try reducing the number of stars
   - Check your internet connection

3. **Streamlit deployment fails**
   - Ensure all files are committed to GitHub
   - Check the requirements.txt file
   - View deployment logs on Streamlit Cloud

## 📞 Contact

Your Name - [@your_twitter](https://twitter.com/your_twitter)

Project Link: [https://github.com/YOUR_USERNAME/3d-star-viewer](https://github.com/YOUR_USERNAME/3d-star-viewer)