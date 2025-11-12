// All interface definitions for the application

export interface Matching2Props {
  thickness: number;
  price: number;
  u_value: number;
  acoustic: number;
  fire_rating: number;
}

export interface PriceStats {
  max: number;
  median: number;
  min: number;
  count: number;
}

export interface LayerData {
  [layerName: string]: number[][];
}

export interface LayersResponse {
  product_name: string;
  layers: LayerData;
}

export interface LignumData {
  bauteilname: string;
  katalognr: string;
  laufnummer: string;
  uwert: string;
  aufbauhoehe?: number;
  gewicht?: number;
  gwp?: string;
  media?: {
    image_jpg?: string;
    detail?: string;
  };
  bauteiltyp?: {
    name?: string;
  };
  fassadentyp?: {
    name?: string;
  };
  bekleidung?: {
    name?: string;  
  };
  daemmwerte?: {
    luftschalldaemmwerte?: {
      rw?: number;
    };
  };
  quellekonstruktion?: {
    quelle?: string;
    year?: number;
  };
}

export interface ProductCombination {
  thicknesses: number[];
  performances: number[];
  color?: string;  // Gradient color for tolerance matches
  soft_violation?: number;  // Soft violation score for tolerance matches
}

export interface SingleProductFilterResponse {
  meets_req: { [productName: string]: Array<ProductCombination> };
  meets_req_with_tol: { [productName: string]: Array<ProductCombination> };
  fails_req: { [productName: string]: Array<ProductCombination> };
}

export interface AllProductsFilterResponse {
  meets_req: { [productName: string]: Array<ProductCombination> };
  meets_req_with_tol: { [productName: string]: Array<ProductCombination> };
  fails_req: { [productName: string]: Array<ProductCombination> };
}

export interface PreFilterRequest {
  product: string;
  preFilter: { [key: string]: number[] | null };
}


