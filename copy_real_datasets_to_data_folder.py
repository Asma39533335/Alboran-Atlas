
from pathlib import Path
import shutil
import os

# ============================================================
# Copy real local datasets into the platform data folder
#
# Run this locally if you want the Streamlit Cloud app to use real NetCDF
# files instead of static generated PNG layers.
#
# Important:
# GitHub has a normal file-size limit of 100 MB per file.
# If your NetCDF files are larger, use Git LFS or cloud storage.
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
AQUASAFE_DIR = DATA_DIR / "aquasafe"
BATHY_DIR = DATA_DIR / "bathymetry"
ODYSSEA_DIR = DATA_DIR / "odyssea"
GLIDER_DIR = DATA_DIR / "gliders"

for d in [AQUASAFE_DIR, BATHY_DIR, ODYSSEA_DIR, GLIDER_DIR]:
    d.mkdir(parents=True, exist_ok=True)

FILES = {
    # AQUASAFE
    r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-amonium-concentration.nc": AQUASAFE_DIR,
    r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-dissolved-oxygen.nc": AQUASAFE_DIR,
    r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-Eastward Sea Water Velocity.nc": AQUASAFE_DIR,
    r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-flow-subset-06_14_2024_8_03_PM.nc": AQUASAFE_DIR,
    r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-flow-subset-ssh.nc": AQUASAFE_DIR,
    r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-inorganic phosphate.nc": AQUASAFE_DIR,
    r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-nitrate-concentration.nc": AQUASAFE_DIR,
    r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-phytoplankton.nc": AQUASAFE_DIR,
    r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-sea-water-salinity.nc": AQUASAFE_DIR,
    r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-sea-water-temperature.nc": AQUASAFE_DIR,
    r"C:\Users\Asus\Desktop\aquasafe data\dataset-aquasafe-morocco-zooplankton.nc": AQUASAFE_DIR,

    # bathymetry
    r"C:\Users\Asus\Desktop\bathymetry\gebco_alboran.nc": BATHY_DIR,

    # glider
    r"C:\Users\Asus\Downloads\SEA038.32.pld1.sub.all.csv": GLIDER_DIR,
    r"C:\Users\Asus\Downloads\SEA038.32.gli.sub.all.csv": GLIDER_DIR,
    r"C:\Users\Asus\Downloads\SEA038.26.pld1.sub.all.csv": GLIDER_DIR,
    r"C:\Users\Asus\Downloads\SEA038.26.gli.sub.all.csv": GLIDER_DIR,

    # ODYSSEA / CMEMS mission products
    r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_26_Mission1_MED_L4_SST_REP.nc": ODYSSEA_DIR,
    r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_26_Mission1_MED_L4_SST_REP_with_degC.nc": ODYSSEA_DIR,
    r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_26_Mission1_MED_PHY_REANALYSIS_SALINITY_0_500m.nc": ODYSSEA_DIR,
    r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_26_Mission1_MED_PHY_REANALYSIS_SALINITY_0_500m_with_surface_and_0_50m_mean.nc": ODYSSEA_DIR,
    r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_32_Mission2_MED_L4_SST_REP.nc": ODYSSEA_DIR,
    r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_32_Mission2_MED_L4_SST_REP_with_degC.nc": ODYSSEA_DIR,
    r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_32_Mission2_MED_PHY_REANALYSIS_SALINITY_0_500m.nc": ODYSSEA_DIR,
    r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_32_Mission2_MED_PHY_REANALYSIS_SALINITY_0_500m_with_surface_and_0_50m_mean.nc": ODYSSEA_DIR,
    r"C:\Users\Asus\Desktop\ODYSSEA_SST_Glider_Missions\SEA038_32_Mission2_ODYSSEA_L3S_SST_subset.nc": ODYSSEA_DIR,
}

copied = []
missing = []
large = []

for src, dst_dir in FILES.items():
    p = Path(src)
    if not p.exists():
        missing.append(src)
        continue

    target = dst_dir / p.name
    shutil.copy2(p, target)
    size_mb = target.stat().st_size / (1024 * 1024)
    copied.append((str(p), str(target), size_mb))
    if size_mb > 95:
        large.append((str(target), size_mb))

print()
print("Copied files:")
for src, dst, mb in copied:
    print(f"  {mb:8.1f} MB | {dst}")

print()
print("Missing files:")
for src in missing:
    print(f"  {src}")

if large:
    print()
    print("Large files warning:")
    for dst, mb in large:
        print(f"  {mb:.1f} MB | {dst}")
    print()
    print("GitHub normally blocks files larger than 100 MB.")
    print("For large files, use Git LFS or cloud storage.")

print()
print("Next GitHub steps:")
print("  git add data")
print('  git commit -m "Add real DTO datasets"')
print("  git push")
