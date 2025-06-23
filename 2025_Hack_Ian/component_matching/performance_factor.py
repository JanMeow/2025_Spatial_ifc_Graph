import numpy as no
import pandas as pd
from pathlib import Path

excels = Path("data/excel")
def load_excel(file_path):
    # Load raw Excel
    df_raw = pd.read_excel("data.xlsx", header=None)

    # Material layer names
    material_names = df_raw.iloc[3, 1:].dropna().unique().tolist()
    start_col = 1  # 'Schicht' column is at 0
    # ------------------------------
    # 1️ Extract properties (Lambda, Brandverhalten)
    # ------------------------------
    properties_rows = [ 4, 5]  # zero-based row indices for Lambda and Brandverhalten
    properties = []
    for row in properties_rows:
        row_label = df_raw.iloc[row, 0]
        values = df_raw.iloc[row, start_col::2].values[:len(material_names)]  # skip every second (Preis col)
        properties.append([row_label] + list(values))
    df_0 = pd.DataFrame(properties, columns=["Property"] + material_names)
    # ------------------------------
    # 2️ Extract layer combinations (Dicke/Preis)
    # ------------------------------
    entries = []
    for i, material in enumerate(material_names):
        col_thickness = start_col + i * 2
        col_price = col_thickness + 1
        for row in range(8, df_raw.shape[0]):  # Assuming data starts at row 8
            dicke = df_raw.iloc[row, col_thickness]
            preis = df_raw.iloc[row, col_price]
            if isinstance(dicke, str) or isinstance(preis, str):
                continue
            if pd.notna(dicke) and pd.notna(preis):
                entries.append({
                    "Schicht": material,
                    "Dicke [mm]": dicke,
                    "Preis [CHF/m2]": preis
                })
    df_1 = pd.DataFrame(entries)
    return df_0, df_1
def main():
    return
if __name__ == "__main__":
    main()