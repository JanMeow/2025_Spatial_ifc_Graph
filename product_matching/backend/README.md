# Backend API

This FastAPI backend provides API endpoints for the product matching frontend.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the backend:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Documentation

Once the server is running, you can access:
- **Interactive API docs**: `http://localhost:5000/docs`
- **Alternative API docs**: `http://localhost:5000/redoc`
- **Health check**: `http://localhost:5000/api/v1/health`

## API Endpoints

### GET /
**Description:** Root endpoint with API information  
**Response:** API metadata and available endpoints

**Example Response:**
```json
{
  "message": "Product Performance API",
  "version": "1.0.0",
  "endpoints": {
    "/api/v1/health": "Health check endpoint",
    "/api/v1/products": "Get all available products",
    "/api/v1/products/{product_type}": "Get products by type",
    "/api/v1/products/{product_type}/{product_name}": "Get specific product details",
    "/api/v1/products/{product_type}/{product_name}/layers": "Get layers for a specific product",
    "/api/v1/products/{product_type}/{product_name}/lignum": "Get Lignum database data",
    "/api/v1/requirement_profiles/apply": "Apply requirement profile filter (POST)"
  },
  "documentation": {
    "swagger": "/docs",
    "redoc": "/redoc"
  }
}
```

### GET /api/v1/health
**Description:** Health check endpoint  
**Response:** API status and data loading status

**Example Response:**
```json
{
  "status": "healthy",
  "data_loaded": true
}
```

---

## Products Endpoints

### GET /api/v1/products
**Description:** Returns a list of all available products  
**Response:** Array of product names

**Example Response:**
```json
["Aussenwand 1.1", "Aussenwand 1.2", "Aussenwand 1.3", "Innenwand 2.1", "Decke 3.1"]
```

### GET /api/v1/products/{product_type}
**Description:** Returns a list of products filtered by type  
**Parameters:**
- `product_type` (path): Type of product (e.g., "Aussenwand", "Innenwand", "Decke")

**Example Request:**
```bash
GET /api/v1/products/Aussenwand
```

**Example Response:**
```json
["All", "Aussenwand 1.1", "Aussenwand 1.2", "Aussenwand 1.3", "Aussenwand 1.7", "Aussenwand 1.8"]
```

### GET /api/v1/products/{product_type}/{product_name}
**Description:** Get detailed information for a specific product  
**Parameters:**
- `product_type` (path): Type of product
- `product_name` (path): Name of the specific product

**Example Request:**
```bash
GET /api/v1/products/Aussenwand/Aussenwand%201.1
```

**Example Response:**
```json
{
  "variants": {
    "layer1": [[100, 50, 0.15], [120, 60, 0.14]],
    "layer2": [[200, 100, 0.10]]
  },
  "metadata": {...}
}
```

### GET /api/v1/products/{product_type}/{product_name}/layers
**Description:** Get layer information for a specific product  
**Parameters:**
- `product_type` (path): Type of product
- `product_name` (path): Name of the product

**Example Request:**
```bash
GET /api/v1/products/Aussenwand/Aussenwand%201.1/layers
```

**Example Response:**
```json
{
  "product_name": "Aussenwand 1.1",
  "layers": {
    "Außenschicht": [[20, 15.5], [25, 18.0]],
    "Dämmung": [[100, 45.0], [120, 52.0], [140, 58.0]],
    "Tragschicht": [[80, 65.0], [100, 75.0]],
    "Innenschicht": [[12.5, 8.5]]
  }
}
```

### GET /api/v1/products/{product_type}/{product_name}/lignum
**Description:** Get Lignum database data for a specific product  
**Parameters:**
- `product_type` (path): Type of product
- `product_name` (path): Name of the product (must be in Lignum references)

**Example Request:**
```bash
GET /api/v1/products/Aussenwand/Aussenwand%201.1/lignum
```

**Example Response:**
```json
{
  "bauteilname": "Aussenwand Holz",
  "katalognr": "D0100",
  "laufnummer": "D0100",
  "uwert": "0.15",
  "aufbauhoehe": 350,
  "gewicht": 45,
  "gwp": "12.5",
  "media": {
    "image_jpg": "https://lignumdata.ch/images/D0100.jpg"
  },
  "bauteiltyp": {
    "name": "Holzrahmenbau"
  },
  "fassadentyp": {
    "name": "Hinterlüftete Fassade"
  },
  "bekleidung": {
    "name": "Holzverschalung"
  },
  "daemmwerte": {
    "luftschalldaemmwerte": {
      "rw": 52
    }
  },
  "quellekonstruktion": {
    "quelle": "Lignum",
    "year": 2023
  }
}
```

---

## Requirement Profiles Endpoint

### POST /api/v1/requirement_profiles/apply
**Description:** Applies a requirement profile to filter and evaluate products  
**Request Body:**
```json
{
  "product": "Aussenwand 1.1",
  "tThresh": 350,
  "pThresh": 350,
  "uThresh": 0.15,
  "pTol": 10,
  "tTol": 20,
  "uTol": 0.03,
  "tThreshOp": "~=",
  "pThreshOp": "<=",
  "uThreshOp": "<=",
  "sampling": "horizontal",
  "preFilter": {
    "Außenschicht": [0, 1],
    "Dämmung": [1, 2]
  }
}
```

**Request Parameters:**
- `product` (string): Product name or "All" for comparison across products, or "All Aussenwand" for type comparison
- `tThresh` (float): Thickness threshold in mm
- `pThresh` (float): Price threshold in CHF/m²
- `uThresh` (float): U-value threshold in W/m²K
- `pTol` (float): Price tolerance
- `tTol` (float): Thickness tolerance in mm
- `uTol` (float): U-value tolerance in W/m²K
- `tThreshOp` (string): Thickness comparison operator ("~=", "<", "<=", ">", ">=")
- `pThreshOp` (string): Price comparison operator ("==", "~=", "<", "<=", ">", ">=")
- `uThreshOp` (string): U-value comparison operator ("==", "~=", "<", "<=", ">", ">=")
- `sampling` (string, optional): Sampling method ("horizontal", "vertical", or null for none)
- `preFilter` (object, optional): Layer variant indices to include in combinations

**Response for Single Product:**
```json
{
  "meets_req": {
    "Aussenwand 1.1": [
      {
        "thicknesses": [20, 120, 80, 12.5],
        "performances": [232.5, 285.50, 0.145]
      }
    ]
  },
  "meets_req_with_tol": {
    "Aussenwand 1.1": [
      {
        "thicknesses": [25, 140, 100, 12.5],
        "performances": [277.5, 358.20, 0.172]
      }
    ]
  },
  "fails_req": {
    "Aussenwand 1.1": [
      {
        "thicknesses": [20, 100, 80, 12.5],
        "performances": [212.5, 420.00, 0.195]
      }
    ]
  }
}
```

**Response for Multiple Products (e.g., product: "All Aussenwand"):**
```json
{
  "meets_req": {
    "Aussenwand 1.1": [{...}],
    "Aussenwand 1.2": [{...}],
    "Aussenwand 1.3": [{...}]
  },
  "meets_req_with_tol": {
    "Aussenwand 1.1": [{...}],
    "Aussenwand 1.2": [{...}]
  },
  "fails_req": {
    "Aussenwand 1.1": [{...}],
    "Aussenwand 1.2": [{...}]
  }
}
```

**Comparison Operators:**
- `==`: Equal to
- `~=`: Approximately equal (within tolerance)
- `<`: Less than
- `<=`: Less than or equal to
- `>`: Greater than
- `>=`: Greater than or equal to

---

## Error Handling

### HTTP Status Codes
- `200 OK`: Successful request
- `404 Not Found`: Product or resource not found
- `422 Unprocessable Entity`: Invalid request body (validation error)
- `500 Internal Server Error`: Server error or external API failure

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

### Common Error Scenarios
- **Invalid product name**: Returns 404 when requesting a non-existent product
- **Lignum data not found**: Returns 404 when product is not in Lignum references
- **External API failure**: Returns 500 when Lignum API is unavailable
- **Invalid request body**: Returns 422 when request validation fails

---

## Data Processing

The backend uses `script.py` to process Excel data and calculate performance metrics for different product configurations. The processed data includes:

- **Thickness** [mm]: Total product thickness
- **Price** [CHF/m²]: Cost per square meter
- **U-Value** [W/m²K]: Thermal transmittance

### Performance Calculation
The API calculates performance metrics by:
1. Loading product configuration data from Excel files
2. Generating all possible layer combinations (or applying pre-filters)
3. Applying sampling methods (horizontal, vertical, or none)
4. Calculating thickness, price, and U-value for each combination
5. Filtering results based on user-defined thresholds, tolerances, and operators

### Caching
- Performance calculations are cached for improved response times
- Cache is automatically cleaned when it exceeds 100 entries
- Pre-filtered results bypass cache to ensure accuracy

---

## Usage Examples

### Get Products by Type
```bash
curl "http://localhost:5000/api/v1/products/Aussenwand"
```

### Get Product Layers
```bash
curl "http://localhost:5000/api/v1/products/Aussenwand/Aussenwand%201.1/layers"
```

### Apply Requirement Profile to Single Product
```bash
curl -X POST "http://localhost:5000/api/v1/requirement_profiles/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "product": "Aussenwand 1.1",
    "tThresh": 350,
    "pThresh": 350,
    "uThresh": 0.15,
    "tTol": 20,
    "uTol": 0.03,
    "tThreshOp": "~=",
    "pThreshOp": "<=",
    "uThreshOp": "<=",
    "sampling": "horizontal"
  }'
```

### Compare All Products of Same Type
```bash
curl -X POST "http://localhost:5000/api/v1/requirement_profiles/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "product": "All Aussenwand",
    "tThresh": 350,
    "pThresh": 350,
    "uThresh": 0.15,
    "tTol": 20,
    "uTol": 0.03,
    "tThreshOp": "~=",
    "pThreshOp": "<=",
    "uThreshOp": "<="
  }'
```

### Apply Pre-Filter and Requirement Profile
```bash
curl -X POST "http://localhost:5000/api/v1/requirement_profiles/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "product": "Aussenwand 1.1",
    "tThresh": 350,
    "pThresh": 350,
    "uThresh": 0.15,
    "tTol": 20,
    "uTol": 0.03,
    "tThreshOp": "~=",
    "pThreshOp": "<=",
    "uThreshOp": "<=",
    "sampling": "horizontal",
    "preFilter": {
      "Außenschicht": [0, 1],
      "Dämmung": [1, 2, 3]
    }
  }'
```

### Get Lignum Data
```bash
curl "http://localhost:5000/api/v1/products/Aussenwand/Aussenwand%201.1/lignum"
```

---

## REST API Design

This API follows RESTful design principles:

### Resource Hierarchy
```
/api/v1/
  ├── health                                    # Health check
  ├── products/                                 # Products collection
  │   ├── GET                                   # List all products
  │   ├── {product_type}/                       # Product type filter
  │   │   ├── GET                               # List products by type
  │   │   └── {product_name}/                   # Specific product
  │   │       ├── GET                           # Get product details
  │   │       ├── layers/                       # Product layers
  │   │       │   └── GET                       # Get layer data
  │   │       └── lignum/                       # Lignum reference data
  │   │           └── GET                       # Get Lignum data
  └── requirement_profiles/                     # Requirement profiles
      └── apply/                                # Apply filter
          └── POST                              # Execute filtering
```

### Design Principles
- **Versioned API** (`/api/v1/`): Allows future changes without breaking existing clients
- **Resource-based URLs**: Uses nouns (products, layers) instead of verbs
- **Hierarchical structure**: Reflects resource relationships (products → layers)
- **Appropriate HTTP methods**: GET for retrieval, POST for complex operations
- **Proper status codes**: 200, 404, 422, 500 for different scenarios
- **Consistent response format**: JSON with predictable structure

---

## Notes

- The backend currently uses Excel data structure. You may need to modify the data loading functions to match your actual Excel file structure.
- In the future, this may be connected to a database instead of reading from Excel files.
- The API supports CORS for frontend integration.
- Interactive API documentation is available at `/docs` and `/redoc` endpoints.
- All endpoints use `/api/v1/` prefix for versioning.
