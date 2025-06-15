"""
Gaia Star Data Fetcher
Fetches nearby star data from Gaia DR3 catalog using Astropy
"""

import numpy as np
import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord, ICRS
from astroquery.gaia import Gaia
import json
from pathlib import Path

class GaiaStarFetcher:
    def __init__(self):
        """Initialize the Gaia star data fetcher"""
        Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
        Gaia.ROW_LIMIT = -1  # Remove row limit
        
    def fetch_nearby_stars(self, max_stars=1000, max_distance_pc=50):
        """
        Fetch nearby stars from Gaia DR3
        
        Parameters:
        -----------
        max_stars : int
            Maximum number of stars to fetch
        max_distance_pc : float
            Maximum distance in parsecs
            
        Returns:
        --------
        pandas.DataFrame with star data
        """
        print(f"Fetching up to {max_stars} stars within {max_distance_pc} parsecs...")
        
        # Query for nearby stars with good parallax measurements
        # We need parallax > 0 and parallax error < 20% for reliable distances
        query = f"""
        SELECT TOP {max_stars}
            source_id,
            ra,
            dec,
            parallax,
            parallax_error,
            phot_g_mean_mag,
            bp_rp,
            radial_velocity,
            pmra,
            pmdec,
            1000.0/parallax as distance_pc
        FROM gaiadr3.gaia_source
        WHERE parallax > {1000.0/max_distance_pc}
            AND parallax_error/parallax < 0.2
            AND phot_g_mean_mag IS NOT NULL
            AND bp_rp IS NOT NULL
        ORDER BY parallax DESC
        """
        
        try:
            job = Gaia.launch_job(query)
            results = job.get_results()
            df = results.to_pandas()
            
            print(f"Successfully fetched {len(df)} stars")
            
            # Convert to 3D Cartesian coordinates
            df = self._convert_to_cartesian(df)
            
            # Estimate stellar properties
            df = self._estimate_stellar_properties(df)
            
            return df
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    def _convert_to_cartesian(self, df):
        """Convert RA/Dec/Distance to 3D Cartesian coordinates"""
        # Create SkyCoord objects
        coords = SkyCoord(
            ra=df['ra'].values * u.degree,
            dec=df['dec'].values * u.degree,
            distance=df['distance_pc'].values * u.pc,
            frame='icrs'
        )
        
        # Convert to Cartesian coordinates (in parsecs)
        df['x'] = coords.cartesian.x.value
        df['y'] = coords.cartesian.y.value
        df['z'] = coords.cartesian.z.value
        
        return df
    
    def _estimate_stellar_properties(self, df):
        """Estimate stellar radius and temperature from photometry"""
        # Estimate absolute magnitude
        df['abs_mag'] = df['phot_g_mean_mag'] - 5 * np.log10(df['distance_pc']) + 5
        
        # Estimate temperature from color (bp_rp)
        # This is a rough approximation
        df['temp_k'] = 4600 * (1 / (0.92 * df['bp_rp'] + 1.7) + 1 / (0.92 * df['bp_rp'] + 0.62))
        
        # Estimate radius relative to the Sun using Stefan-Boltzmann law
        # L ∝ R² T⁴, and L ∝ 10^(-0.4 * M)
        sun_abs_mag = 4.83
        sun_temp = 5778
        luminosity_ratio = 10**(-0.4 * (df['abs_mag'] - sun_abs_mag))
        df['radius_solar'] = np.sqrt(luminosity_ratio) * (sun_temp / df['temp_k'])**2
        
        # Assign star colors based on temperature
        df['star_color'] = df['temp_k'].apply(self._temp_to_color)
        
        return df
    
    def _temp_to_color(self, temp):
        """Convert temperature to RGB color hex string"""
        # Simplified color mapping based on stellar classification
        if temp > 30000:
            return "#9bb0ff"  # O-type: blue
        elif temp > 10000:
            return "#aabfff"  # B-type: blue-white
        elif temp > 7500:
            return "#cad7ff"  # A-type: white
        elif temp > 6000:
            return "#f8f7ff"  # F-type: yellow-white
        elif temp > 5200:
            return "#fff4ea"  # G-type: yellow (like our Sun)
        elif temp > 3700:
            return "#ffd2a1"  # K-type: orange
        else:
            return "#ffcc6f"  # M-type: red
    
    def save_data(self, df, output_dir="data"):
        """Save star data to JSON for web visualization"""
        Path(output_dir).mkdir(exist_ok=True)
        
        # Prepare data for JSON export
        star_data = {
            "stars": []
        }
        
        for _, star in df.iterrows():
            star_data["stars"].append({
                "id": int(star['source_id']),
                "position": {
                    "x": float(star['x']),
                    "y": float(star['y']),
                    "z": float(star['z'])
                },
                "properties": {
                    "ra": float(star['ra']),
                    "dec": float(star['dec']),
                    "distance_pc": float(star['distance_pc']),
                    "magnitude": float(star['phot_g_mean_mag']),
                    "abs_magnitude": float(star['abs_mag']),
                    "temperature": float(star['temp_k']),
                    "radius_solar": float(star['radius_solar']),
                    "color": star['star_color']
                }
            })
        
        # Save to JSON
        output_path = Path(output_dir) / "star_data.json"
        with open(output_path, 'w') as f:
            json.dump(star_data, f, indent=2)
        
        # Also save as CSV for analysis
        csv_path = Path(output_dir) / "star_data.csv"
        df.to_csv(csv_path, index=False)
        
        print(f"Data saved to {output_path} and {csv_path}")
        
        return star_data


def main():
    """Main function to fetch and save star data"""
    fetcher = GaiaStarFetcher()
    
    # Fetch nearby stars (you can adjust these parameters)
    df = fetcher.fetch_nearby_stars(max_stars=500, max_distance_pc=30)
    
    if df is not None:
        # Save the data
        star_data = fetcher.save_data(df)
        
        # Print some statistics
        print(f"\nStatistics:")
        print(f"Total stars: {len(df)}")
        print(f"Distance range: {df['distance_pc'].min():.2f} - {df['distance_pc'].max():.2f} pc")
        print(f"Temperature range: {df['temp_k'].min():.0f} - {df['temp_k'].max():.0f} K")
        print(f"Radius range: {df['radius_solar'].min():.2f} - {df['radius_solar'].max():.2f} solar radii")


if __name__ == "__main__":
    main()
