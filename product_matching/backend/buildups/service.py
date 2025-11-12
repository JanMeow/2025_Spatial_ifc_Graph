import pandas as pd
import numpy as np
# =========================================================================================
"""
will be replaced by the DB function later 
"""
def load_data_from_excel(file_path):
  xls = pd.ExcelFile(file_path)
  sheet_keys = xls.sheet_names
  sheet_data = {}

  for sheet_name in sheet_keys:
      df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

      # Extract material names from row 3
      raw_material_names = df_raw.iloc[3, 1:].dropna().tolist()
      raw_material_names = [str(name).strip() for name in raw_material_names]
      start_col = 1

      # Track seen keys and build unique names
      name_counts = {}
      final_material_names = []

      for name in raw_material_names:
          if name not in name_counts:
              name_counts[name] = 1
              final_material_names.append(name)
          else:
              name_counts[name] += 1
              final_material_names.append(f"{name}{name_counts[name]}")

      # --- Extract df_0 (properties like Lambda-Wert) ---
      properties_rows = [4, 5]
      properties = []

      for row in properties_rows:
          row_label = df_raw.iloc[row, 0]
          values = df_raw.iloc[row, start_col::2].values[:len(final_material_names)]
          properties.append([row_label] + list(values))

      df_0 = pd.DataFrame(properties, columns=["Property"] + final_material_names)

      # Convert each column (excluding 'Property') into a numpy array
      data_0 = {}
      for material in df_0.columns[1:]:
        values = df_0[material].to_numpy()
        data_0[material] = values

      # --- Extract df_1 as dict of np arrays ---
      data_1 = {}
      name_counts = {}  # Reset to reassign same renaming logic for df_1

      for i, base_name in enumerate(raw_material_names):
          col_thickness = start_col + i * 2
          col_price = col_thickness + 1

          # Get group of entries
          group = []
          for row in range(8, df_raw.shape[0]):
              dicke = df_raw.iloc[row, col_thickness]
              preis = df_raw.iloc[row, col_price]
              if isinstance(dicke, str) or isinstance(preis, str):
                  continue
              if pd.notna(dicke) and pd.notna(preis):
                  group.append([dicke, preis])

          # Rename key consistently
          if base_name not in name_counts:
              name_counts[base_name] = 1
              final_key = base_name
          else:
              name_counts[base_name] += 1
              final_key = f"{base_name}{name_counts[base_name]}"

          if group:
              data_1[final_key] = np.array(group)

      # Store result
      sheet_data[sheet_name] = {
          "properties": data_0,
          "variants": data_1
      }
  return sheet_data