# Gradient Color Implementation for Tolerance Matches

## Overview
Implemented a **server-side gradient color system** that color-codes products meeting requirements with tolerance based on their "soft violation" score. Products closer to the ideal requirements display greener, while those at the tolerance boundary appear redder.

## Implementation Summary

### ✅ Backend Changes (`backend/app.py`)

#### 1. Fixed `map_to_colour_gradient` Function (Lines 217-261)
**Previous Issues:**
- Undefined `gradient_step` variable
- Typo: `np.mins` instead of `np.min`
- Incorrect normalization formula
- No return of RGB strings

**New Implementation:**
```python
def map_to_colour_gradient(loss: np.array, rgb0: np.array = np.array([0, 255, 0]), rgb1: np.array = np.array([255, 0, 0])):
    """
    Map loss values to RGB color gradient.
    Lower loss (better) -> green (rgb0)
    Higher loss (worse) -> red (rgb1)
    """
    # Handles edge cases
    # Normalizes loss to 0-1 range
    # Linear interpolation between green and red
    # Returns array of RGB strings: ['rgb(r, g, b)', ...]
```

**Key Features:**
- ✅ Proper min-max normalization
- ✅ Linear interpolation between green (0,255,0) and red (255,0,0)
- ✅ Edge case handling (all same loss values)
- ✅ Returns CSS-ready RGB strings

#### 2. Updated `plot_data` Function (Lines 147-186)
Added optional `colors` parameter to include gradient colors in response:
```python
def plot_data(product_data, combinations, indices, performances, colors=None):
    # ...existing code...
    if colors is not None and i < len(colors):
        item["color"] = colors[i]
```

#### 3. Enhanced `filter_single_product` Function (Lines 444-501)
Added gradient color calculation for tolerance matches:
```python
# Calculate soft violation colors for tolerance matches
gradient_colors = []
if len(matching_indices_with_tol) > 0:
    soft_violation = get_soft_violation(request, Weights(), matching_indices_with_tol, performances, "logistic")
    if soft_violation is not None and len(soft_violation) > 0:
        gradient_colors = map_to_colour_gradient(soft_violation.flatten())
        print(f"Generated {len(gradient_colors)} gradient colors for tolerance matches")

# Use gradient colors when plotting tolerance matches
updated_meets_req_with_tol[request.product] = plot_data(
    product_data, combinations, matching_indices_with_tol, performances, gradient_colors
)
```

#### 4. Enhanced `filter_all_products` Function (Lines 400-447)
Same gradient color calculation added for "All" product comparisons.

### ✅ Frontend Changes

#### 1. TypeScript Interfaces (`frontend/src/types/interfaces.ts`)
Created new `ProductCombination` interface:
```typescript
export interface ProductCombination {
  thicknesses: number[];
  performances: number[];
  color?: string;  // Gradient color for tolerance matches
}
```

Updated response interfaces to use the new type.

#### 2. App.tsx Updates

**Import ProductCombination:**
```typescript
import type { 
  ...
  ProductCombination
} from './types/interfaces';
```

**Updated Data Conversion (Lines 756-774):**
```typescript
const convertNewDataToOldFormat = (newData: { [productName: string]: Array<ProductCombination> }) => {
  const flatData: number[][] = [];
  const flatLayerThicknesses: number[][] = [];
  const flatProductNames: string[] = [];
  const flatColors: string[] = [];  // NEW: Extract colors
  
  Object.entries(newData).forEach(([productName, items]) => {
    items.forEach(item => {
      flatData.push(item.performances);
      flatLayerThicknesses.push(item.thicknesses);
      flatProductNames.push(productName);
      if (item.color) {
        flatColors.push(item.color);  // NEW: Collect gradient colors
      }
    });
  });
  
  return { flatData, flatLayerThicknesses, flatProductNames, flatColors };
};
```

**Updated 3D Plot Marker Colors (Lines 843-848):**
```typescript
marker: { 
  color: meetsWithTolData.flatColors && meetsWithTolData.flatColors.length > 0 
    ? meetsWithTolData.flatColors  // Use gradient colors from backend
    : 'orange',                     // Fallback to orange
  size: 6 
}
```

## How It Works

### 1. Soft Violation Calculation
For each product meeting requirements with tolerance:
- Calculate distance from ideal thresholds
- Apply penalty/credit based on comparison operators
- Weight by importance (thickness, price, U-value)
- Aggregate into single "soft violation" score

### 2. Color Mapping
- **Min violation** (closest to ideal) → **Green** `rgb(0, 255, 0)`
- **Max violation** (at tolerance boundary) → **Red** `rgb(255, 0, 0)`
- **In between** → Linear interpolation

Example:
```
Soft Violation: [0.1, 0.3, 0.5, 0.8, 1.0]
Colors:         [green, yellow-green, yellow, orange, red]
```

### 3. Visual Result
In the 3D plot:
- **Green markers**: Exact matches (meets requirements perfectly)
- **Green-to-Red gradient**: Tolerance matches (color indicates how close to ideal)
- **Red markers**: Failed requirements

## Server-Side vs Client-Side

### Why Server-Side? ✅ **Chosen Implementation**
✅ **Efficiency**: Calculate once, use everywhere  
✅ **Performance**: NumPy is faster than JavaScript for array ops  
✅ **Consistency**: All clients see identical colors  
✅ **Simplicity**: Frontend just displays the colors  
✅ **Caching**: Results can be cached with other data  

### Client-Side Alternative (Not Chosen)
❌ Recalculate on every render  
❌ Inconsistent between browsers/devices  
❌ More complex frontend code  
❌ Additional state management needed  

## Testing

### 1. Start Backend
```bash
cd backend
python app.py
```

### 2. Start Frontend
```bash
cd frontend
npm start
```

### 3. Test Scenarios

**Scenario A: Single Product with Tolerance**
1. Select a product (e.g., "Aussenwand 1.1")
2. Set thresholds with tolerances:
   - Thickness: 350mm ± 20mm
   - Price: 350 CHF/m² ± 10
   - U-value: 0.15 W/m²K ± 0.03
3. Click "Apply"
4. **Expected**: Orange points now show gradient from green to red

**Scenario B: All Products Comparison**
1. Select "All Aussenwand"
2. Set same thresholds
3. **Expected**: Each product's tolerance matches show individual gradients

### 4. Verify in Browser DevTools
```javascript
// Check the network response
// POST to /api/v1/requirement_profiles/apply
// Response should include:
{
  "meets_req_with_tol": {
    "Aussenwand 1.1": [
      {
        "thicknesses": [20, 120, 80, 12.5],
        "performances": [232.5, 285.50, 0.145],
        "color": "rgb(0, 255, 0)"  // ← NEW: Gradient color
      },
      {
        "thicknesses": [25, 140, 100, 12.5],
        "performances": [277.5, 358.20, 0.172],
        "color": "rgb(128, 127, 0)"  // ← Yellow-ish (mid-range)
      }
    ]
  }
}
```

## Color Gradient Examples

| Soft Violation | Normalized (0-1) | RGB Color | Visual |
|---|---|---|---|
| 0.05 (best) | 0.00 | rgb(0, 255, 0) | 🟢 Green |
| 0.15 | 0.25 | rgb(64, 191, 0) | 🟢 Yellow-green |
| 0.25 | 0.50 | rgb(128, 127, 0) | 🟡 Yellow |
| 0.35 | 0.75 | rgb(191, 64, 0) | 🟠 Orange |
| 0.45 (worst) | 1.00 | rgb(255, 0, 0) | 🔴 Red |

## API Response Format

### Before (Old)
```json
{
  "meets_req_with_tol": {
    "Aussenwand 1.1": [
      {
        "thicknesses": [20, 120, 80, 12.5],
        "performances": [232.5, 285.50, 0.145]
      }
    ]
  }
}
```

### After (New)
```json
{
  "meets_req_with_tol": {
    "Aussenwand 1.1": [
      {
        "thicknesses": [20, 120, 80, 12.5],
        "performances": [232.5, 285.50, 0.145],
        "color": "rgb(0, 255, 0)"
      }
    ]
  }
}
```

## Future Enhancements

### Potential Improvements:
1. **Customizable Colors**: Allow users to set green/red endpoints
2. **Non-Linear Mapping**: Exponential or logarithmic gradients
3. **Multi-Criteria Coloring**: Different colors for different violation types
4. **Color Legend**: Show what each color represents
5. **Hover Details**: Display soft violation score in tooltip

### Code Extension Points:
```python
# backend/app.py
def map_to_colour_gradient(
    loss: np.array, 
    rgb0: np.array = np.array([0, 255, 0]),  # Customizable
    rgb1: np.array = np.array([255, 0, 0]),  # Customizable
    mapping: str = "linear"  # NEW: "linear", "exponential", "logarithmic"
):
    # Implementation for different mapping functions
```

## Summary

### What Was Implemented:
✅ Fixed `map_to_colour_gradient` function with proper gradient calculation  
✅ Server-side gradient color generation based on soft violation scores  
✅ Updated API response to include color data  
✅ Frontend integration to display gradient colors  
✅ TypeScript interfaces updated with color support  

### Visual Result:
- Products meeting requirements **exactly** → **Green** 🟢
- Products meeting with **tolerance** → **Green-to-Red gradient** 🟢🟡🟠🔴 (based on how close to ideal)
- Products **failing** requirements → **Red** 🔴

### Benefits:
- **Intuitive**: Visual feedback on product quality
- **Informative**: Easily identify best tolerance matches
- **Efficient**: Calculated once on server, displayed on all clients
- **Scalable**: Works for single products and "All" comparisons

## Files Modified

1. ✅ `backend/app.py` - Core gradient logic
2. ✅ `frontend/src/App.tsx` - Display gradient colors
3. ✅ `frontend/src/types/interfaces.ts` - TypeScript types
4. ✅ `GRADIENT_COLOR_IMPLEMENTATION.md` - This documentation


