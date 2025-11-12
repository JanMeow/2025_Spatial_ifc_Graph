import React, { useState, useEffect, useRef, useMemo } from 'react';
import Plot from 'react-plotly.js';
import { Box, Slider, Typography, Select, MenuItem, FormControl, InputLabel, CircularProgress, Paper, Checkbox, FormControlLabel, Chip, TextField, Button } from '@mui/material';
import './App.css';
import Matching2 from './components/matching2';
import PriceStatsVisualization from './components/PriceStatsVisualization';
import CombinationsTable from './components/CombinationsTable';
import AllWallsCombinationsTable from './components/AllWallsCombinationsTable';
import RequirementProfile, { RequirementProfileProps } from './components/RequirementProfile';
import type { 
  Matching2Props, 
  LayerData, 
  LayersResponse, 
  LignumData, 
  SingleProductFilterResponse, 
  AllProductsFilterResponse, 
  PreFilterRequest,
  ProductCombination
} from './types/interfaces';

// API base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api/v1';

// Component for displaying Lignum data
const LignumVisualization: React.FC<{ lignumData: LignumData | null }> = ({ lignumData }) => {
  if (!lignumData) {
    return (
      <Paper sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No Lignum data available
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Lignum Bauteil Reference
      </Typography>
      
      <Box sx={{ display: 'flex', gap: 2, flexDirection: { xs: 'column', md: 'row' } }}>
        {/* Image */}
        <Box sx={{ flex: '1 1 800px' }}>
          {lignumData.media?.image_jpg && (
            <Paper sx={{ p: 1, textAlign: 'center' }}>
              <img 
                src={lignumData.media.image_jpg} 
                alt="Construction detail"
                style={{ 
                  width: '100%', 
                  height: 'auto',
                  maxHeight: '400px',
                  objectFit: 'contain'
                }}
              />
            </Paper>
          )}
        </Box>
        
        {/* Data Grid */}
        <Box sx={{ flex: '1 1 400px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 1, height: '400px' }}>
            <Paper sx={{ p: 1, textAlign: 'center', bgcolor: '#f5f5f5' }}>
              <Typography variant="body2" color="text.secondary">Lignum ID</Typography>
              <Typography variant="body1" fontWeight="bold">{lignumData.laufnummer}</Typography>
            </Paper>
            <Paper sx={{ p: 1, textAlign: 'center', bgcolor: '#f5f5f5' }}>
              <Typography variant="body2" color="text.secondary">Katalognummer</Typography>
              <Typography variant="body1" fontWeight="bold">{lignumData.katalognr}</Typography>
            </Paper>
            <Paper sx={{ p: 1, textAlign: 'center', bgcolor: '#f5f5f5' }}>
              <Typography variant="body2" color="text.secondary">Quelle Konstruktion</Typography>
              <Typography variant="body1" fontWeight="bold">
                {lignumData.quellekonstruktion?.quelle}, Jahr {lignumData.quellekonstruktion?.year}
              </Typography>
            </Paper>
            <Paper sx={{ p: 1, textAlign: 'center', bgcolor: '#f5f5f5' }}>
              <Typography variant="body2" color="text.secondary">Grundkonstruktion</Typography>
              <Typography variant="body1" fontWeight="bold">{lignumData.bauteiltyp?.name}</Typography>
            </Paper>
            <Paper sx={{ p: 1, textAlign: 'center', bgcolor: '#f5f5f5' }}>
              <Typography variant="body2" color="text.secondary">Fassadentyp</Typography>
              <Typography variant="body1" fontWeight="bold">{lignumData.fassadentyp?.name}</Typography>
            </Paper>
            <Paper sx={{ p: 1, textAlign: 'center', bgcolor: '#f5f5f5' }}>
              <Typography variant="body2" color="text.secondary">Bekleidung</Typography>
              <Typography variant="body1" fontWeight="bold">{lignumData.bekleidung?.name}</Typography>
            </Paper>
            <Paper sx={{ p: 1, textAlign: 'center', bgcolor: '#f5f5f5' }}>
              <Typography variant="body2" color="text.secondary">Aufbauhöhe</Typography>
              <Typography variant="body1" fontWeight="bold">{lignumData.aufbauhoehe} mm</Typography>
            </Paper>
            <Paper sx={{ p: 1, textAlign: 'center', bgcolor: '#f5f5f5' }}>
              <Typography variant="body2" color="text.secondary">Gewicht</Typography>
              <Typography variant="body1" fontWeight="bold">{lignumData.gewicht} kg/m²</Typography>
            </Paper>
            <Paper sx={{ p: 1, textAlign: 'center', bgcolor: '#f5f5f5' }}>
              <Typography variant="body2" color="text.secondary">U-Wert</Typography>
              <Typography variant="body1" fontWeight="bold">≈ {lignumData.uwert} W/m²K</Typography>
            </Paper>
            <Paper sx={{ p: 1, textAlign: 'center', bgcolor: '#f5f5f5' }}>
              <Typography variant="body2" color="text.secondary">GWP</Typography>
              <Typography variant="body1" fontWeight="bold">{lignumData.gwp} kg CO₂-eq/m²</Typography>
            </Paper>
            <Paper sx={{ p: 1, textAlign: 'center', bgcolor: '#f5f5f5' }}>
              <Typography variant="body2" color="text.secondary">Schalldämmung</Typography>
              <Typography variant="body1" fontWeight="bold">Rw = {lignumData.daemmwerte?.luftschalldaemmwerte?.rw} dB</Typography>
            </Paper>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

// Wrapper component that fetches layer data for a specific wall
const LayersVisualizationWrapper: React.FC<{ 
  wallName: string; 
  onApplyPreFilter: (preFilter: PreFilterRequest) => void;
  storedPreFilter?: PreFilterRequest | null;
}> = ({ wallName, onApplyPreFilter, storedPreFilter }) => {
  const [layers, setLayers] = useState<LayerData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchLayers = async () => {
      if (!wallName) return;
      
      setLoading(true);
      try {
        // Extract bauteilTyp from wallName (e.g., "Aussenwand 1.1" -> "Aussenwand")
        const productType = wallName.split(' ')[0];
        const response = await fetch(`${API_BASE_URL}/buildups/${productType}/${encodeURIComponent(wallName)}/layers`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch layers data');
        }

        const data: LayersResponse = await response.json();
        setLayers(data.layers);
      } catch (err) {
        console.error('Error fetching layers data:', err);
        setLayers(null);
      } finally {
        setLoading(false);
      }
    };

    fetchLayers();
  }, [wallName]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!layers) {
    return (
      <Paper sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No layers data available
        </Typography>
      </Paper>
    );
  }

  return (
    <LayersVisualization 
      wallName={wallName} 
      layers={layers} 
      onApplyPreFilter={onApplyPreFilter}
      storedPreFilter={storedPreFilter}
    />
  );
};

// Component for displaying wall layers
const LayersVisualization: React.FC<{ 
  wallName: string; 
  layers: LayerData; 
  onApplyPreFilter: (preFilter: PreFilterRequest) => void;
  storedPreFilter?: PreFilterRequest | null;
}> = ({ wallName, layers, onApplyPreFilter, storedPreFilter }) => {
  const [layerThicknessRanges, setLayerThicknessRanges] = useState<{[key: string]: {min: number, max: number}}>({});
  // Local state for the current preFilter (not yet applied)
  const [localPreFilter, setLocalPreFilter] = useState<PreFilterRequest>({
    product: wallName,
    preFilter: {}
  });
  // The actual applied preFilter (from stored state)
  const [currentPreFilter, setCurrentPreFilter] = useState<PreFilterRequest>({
    product: wallName,
    preFilter: {}
  });

  // Initialize thickness ranges and preFilter when layers change
  useEffect(() => {
    const ranges: {[key: string]: {min: number, max: number}} = {};
    const preFilter: {[key: string]: number[] | null} = {};
    
    Object.entries(layers).forEach(([layerName, variants]) => {
      const thicknesses = variants.map(v => v[0]);
      ranges[layerName] = {
        min: Math.min(...thicknesses),
        max: Math.max(...thicknesses)
      };
      // Initialize preFilter with all variant indices [0, 1, 2, ..., n-1]
      preFilter[layerName] = Array.from({ length: variants.length }, (_, i) => i);
    });
    
    const initialPreFilter = {
      product: wallName,
      preFilter
    };
    
    setLayerThicknessRanges(ranges);
    setLocalPreFilter(initialPreFilter);
    setCurrentPreFilter(initialPreFilter);
  }, [layers, wallName]);

  // Sync with stored preFilter when it changes
  useEffect(() => {
    if (storedPreFilter && storedPreFilter.product === wallName) {
      setCurrentPreFilter(storedPreFilter);
      setLocalPreFilter(storedPreFilter);
      
      // Update thickness ranges based on stored preFilter
      const newRanges: {[key: string]: {min: number, max: number}} = {};
      Object.entries(layers).forEach(([layerName, variants]) => {
        const thicknesses = variants.map(v => v[0]);
        if (storedPreFilter.preFilter[layerName] && storedPreFilter.preFilter[layerName] !== null) {
          // If there's a preFilter, calculate the range from the filtered variants
          const filteredIndices = storedPreFilter.preFilter[layerName] as number[];
          const filteredThicknesses = filteredIndices.map(idx => thicknesses[idx]);
          newRanges[layerName] = {
            min: Math.min(...filteredThicknesses),
            max: Math.max(...filteredThicknesses)
          };
        } else {
          // If no preFilter, show all variants
          newRanges[layerName] = {
            min: Math.min(...thicknesses),
            max: Math.max(...thicknesses)
          };
        }
      });
      setLayerThicknessRanges(newRanges);
    }
  }, [storedPreFilter, wallName, layers]);

  if (!layers || Object.keys(layers).length === 0) {
    return (
      <Paper sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No layers data available
        </Typography>
      </Paper>
    );
  }

  const handleThicknessChange = (layerName: string, type: 'min' | 'max', value: number) => {
    setLayerThicknessRanges(prev => ({
      ...prev,
      [layerName]: {
        ...prev[layerName],
        [type]: value
      }
    }));
    
    // Update the LOCAL preFilter based on the new range (not yet applied)
    const range = layerThicknessRanges[layerName];
    if (range) {
      const newRange = { ...range, [type]: value };
      const variants = layers[layerName];
      const thicknesses = variants.map(v => v[0]);
      
      // Find indices that fall within the range
      const indices: number[] = [];
      thicknesses.forEach((thickness, index) => {
        if (thickness >= newRange.min && thickness <= newRange.max) {
          indices.push(index);
        }
      });
      
      // Update LOCAL preFilter (not the applied one)
      setLocalPreFilter(prev => ({
        ...prev,
        preFilter: {
          ...prev.preFilter,
          [layerName]: indices.length === thicknesses.length ? null : indices
        }
      }));
    }
  };

  const handleApplyPreFilter = () => {
    if (onApplyPreFilter) {
      // Apply the local preFilter
      onApplyPreFilter(localPreFilter);
      // Update the current preFilter to match the local one
      setCurrentPreFilter(localPreFilter);
    }
  };

  const handleResetPreFilter = () => {
    const resetPreFilter: {[key: string]: number[] | null} = {};
    Object.entries(layers).forEach(([layerName, variants]) => {
      // Reset to show all variants [0, 1, 2, ..., n-1]
      resetPreFilter[layerName] = Array.from({ length: variants.length }, (_, i) => i);
    });
    
    // Reset both local and current preFilters
    const resetPreFilterRequest = {
      product: wallName,
      preFilter: resetPreFilter
    };
    
    setLocalPreFilter(resetPreFilterRequest);
    setCurrentPreFilter(resetPreFilterRequest);
    
    // Also reset the ranges to show all variants
    const ranges: {[key: string]: {min: number, max: number}} = {};
    Object.entries(layers).forEach(([layerName, variants]) => {
      const thicknesses = variants.map(v => v[0]);
      ranges[layerName] = {
        min: Math.min(...thicknesses),
        max: Math.max(...thicknesses)
      };
    });
    setLayerThicknessRanges(ranges);
    
    // Notify parent component to reset the stored preFilter for this wall
    if (onApplyPreFilter) {
      onApplyPreFilter({
        product: wallName,
        preFilter: {} // Empty object means reset/clear the preFilter
      });
    }
  };

  return (
    <Box>
      {/* Header with buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="h6">
            Layers for {wallName}
          </Typography>
          {storedPreFilter && storedPreFilter.product === wallName && (
            <Chip 
              label="Pre-filter Active" 
              color="success" 
              size="small" 
              variant="outlined"
            />
          )}
          {JSON.stringify(localPreFilter.preFilter) !== JSON.stringify(currentPreFilter.preFilter) && (
            <Chip 
              label="Unsaved Changes" 
              color="warning" 
              size="small" 
              variant="outlined"
            />
          )}
        </Box>
        
        {/* Buttons on the right */}
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            size="small"
            onClick={handleResetPreFilter}
            sx={{ minWidth: '80px' }}
          >
            Reset
          </Button>
          <Button
            variant="outlined"
            color="warning"
            size="small"
            onClick={() => {
              // Reset all preFilters across all walls
              if (onApplyPreFilter) {
                onApplyPreFilter({
                  product: "RESET_ALL",
                  preFilter: {} // Empty object signals reset all
                });
              }
            }}
            sx={{ minWidth: '80px' }}
          >
            Reset All
          </Button>
          <Button
            variant="contained"
            size="small"
            onClick={handleApplyPreFilter}
            sx={{ minWidth: '100px' }}
          >
            Apply Pre-filter
          </Button>
        </Box>
      </Box>
      
      {/* Debug: Show applied preFilter state */}
      {process.env.NODE_ENV === 'development' && (
        <Box sx={{ mb: 2, p: 1, bgcolor: '#f5f5f5', borderRadius: 1, fontSize: '0.75rem' }}>
          <Typography variant="caption" color="text.secondary">
            Debug - Applied PreFilter: {JSON.stringify(currentPreFilter.preFilter, null, 2)}
          </Typography>
        </Box>
      )}
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {Object.entries(layers).map(([layerName, variants]) => {
          const range = layerThicknessRanges[layerName];
          const thicknesses = variants.map(v => v[0]);
          const minThickness = Math.min(...thicknesses);
          const maxThickness = Math.max(...thicknesses);
          
          return (
            <Paper key={layerName} sx={{ p: 2, backgroundColor: '#f8f9fa' }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1, color: 'primary.main' }}>
                {layerName}
              </Typography>
              
              {/* Variants and Sliders in horizontal layout */}
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start' }}>
                {/* Variants on the left */}
                <Box sx={{ flex: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {variants.map((variant, index) => {
                    const isInRange = range && variant[0] >= range.min && variant[0] <= range.max;
                    return (
                      <Chip
                        key={index}
                        label={`${variant[0]}mm - ${variant[1]}CHF/m²`}
                        size="small"
                        variant="outlined"
                        sx={{ 
                          backgroundColor: isInRange ? '#e7f9f2' : 'white',
                          color: isInRange ? '#2e7d32' : 'inherit',
                          borderColor: isInRange ? '#2e7d32' : 'primary.light',
                          '&:hover': {
                            backgroundColor: isInRange ? '#c8e6c9' : 'primary.light',
                            color: isInRange ? '#1b5e20' : 'white'
                          }
                        }}
                      />
                    );
                  })}
                </Box>
                
                {/* Sliders on the right */}
                <Box sx={{ minWidth: '200px', display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                      Min: {range?.min || minThickness}mm
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                      Max: {range?.max || maxThickness}mm
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Slider
                      value={range?.min || minThickness}
                      min={minThickness}
                      max={maxThickness}
                      step={1}
                      onChange={(_, value) => handleThicknessChange(layerName, 'min', value as number)}
                      size="small"
                      sx={{ flex: 1, mr: 1 }}
                    />
                    <TextField
                      value={range?.min || minThickness}
                      onChange={(e) => {
                        const value = parseInt(e.target.value);
                        if (!isNaN(value)) {
                          handleThicknessChange(layerName, 'min', value);
                        }
                      }}
                      onBlur={(e) => {
                        const value = parseInt(e.target.value);
                        if (isNaN(value) || value < minThickness) {
                          handleThicknessChange(layerName, 'min', minThickness);
                        } else if (value > maxThickness) {
                          handleThicknessChange(layerName, 'min', maxThickness);
                        }
                      }}
                      size="small"
                      sx={{ 
                        width: '50px',
                        '& .MuiOutlinedInput-root': {
                          height: '28px',
                          fontSize: '0.7rem'
                        }
                      }}
                    />
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Slider
                      value={range?.max || maxThickness}
                      min={minThickness}
                      max={maxThickness}
                      step={1}
                      onChange={(_, value) => handleThicknessChange(layerName, 'max', value as number)}
                      size="small"
                      sx={{ flex: 1, mr: 1 }}
                    />
                    <TextField
                      value={range?.max || maxThickness}
                      onChange={(e) => {
                        const value = parseInt(e.target.value);
                        if (!isNaN(value)) {
                          handleThicknessChange(layerName, 'max', value);
                        }
                      }}
                      onBlur={(e) => {
                        const value = parseInt(e.target.value);
                        if (isNaN(value) || value < minThickness) {
                          handleThicknessChange(layerName, 'max', minThickness);
                        } else if (value > maxThickness) {
                          handleThicknessChange(layerName, 'max', maxThickness);
                        }
                      }}
                      size="small"
                      sx={{ 
                        width: '50px',
                        '& .MuiOutlinedInput-root': {
                          height: '28px',
                          fontSize: '0.7rem'
                        }
                      }}
                    />
                  </Box>
                </Box>
              </Box>
              <Typography variant="caption" sx={{ color: 'text.secondary', mt: 1, display: 'block' }}>
                {variants.length} variant{variants.length !== 1 ? 's' : ''} available
              </Typography>
            </Paper>
          );
        })}
      </Box>
    </Box>
  );
};

function App() {
  // State for sliders and dropdown
  const [walls, setWalls] = useState<string[]>([]);
  const [key, setKey] = useState<string>('');
  const [dataSource, setDataSource] = useState<string>('Schaerholz');
  const [bauteilTyp, setBauteilTyp] = useState<string>('Aussenwand');
  const [sampling, setSampling] = useState<string>('horizontal');
  const [tThresh, setTThresh] = useState(350);
  const [pThresh, setPThresh] = useState(350);
  const [uThresh, setUThresh] = useState(0.15);
  const [tTol, setTTol] = useState(20);
  const [pTol, setPTol] = useState(10);
  const [uTol, setUTol] = useState(0.03);
  
  // Comparison operators for sliders
  const [tThreshOp, setTThreshOp] = useState<"==" | "~=" | "<" | "<=" | ">" | ">=">("~=");
  const [pThreshOp, setPThreshOp] = useState<"==" | "~=" | "<" | "<=" | ">" | ">=">("<=");
  const [uThreshOp, setUThreshOp] = useState<"==" | "~=" | "<" | "<=" | ">" | ">=">("<=");
  
  // State for priority rankings
  const [priorityRankings, setPriorityRankings] = useState<Matching2Props>({
    thickness: 1,
    price: 2,
    u_value: 3,
    acoustic: 4,
    fire_rating: 5
  });
  
  // State for checkboxes
  const [showOnlyCurrentType, setShowOnlyCurrentType] = useState(true);
  const [showAllWithinCompany, setShowAllWithinCompany] = useState(false);
  const [showAllAcrossCompanies, setShowAllAcrossCompanies] = useState(false);
  const [showLayers, setShowLayers] = useState(true);
  const [showLignum, setShowLignum] = useState(true);
  const [showPriorityRanking, setShowPriorityRanking] = useState(false);
  const [showRequirementProfile, setShowRequirementProfile] = useState(true);
  
  // State for data and loading
  const [plotData, setPlotData] = useState<any[]>([]);
  const [meetsReqData, setMeetsReqData] = useState<number[][]>([]);
  const [meetsReqWithTolData, setMeetsReqWithTolData] = useState<number[][]>([]);
  const [layerThicknesses, setLayerThicknesses] = useState<number[][]>([]);
  const [wallNames, setWallNames] = useState<string[]>([]);
  const [rawMeetsReqData, setRawMeetsReqData] = useState<{ [productName: string]: Array<{ thicknesses: number[], performances: number[] }> }>({});
  const [rawMeetsReqWithTolData, setRawMeetsReqWithTolData] = useState<{ [productName: string]: Array<{ thicknesses: number[], performances: number[] }> }>({});
  const [productLayersData, setProductLayersData] = useState<{ [productName: string]: string[] }>({});
  const [lignumData, setLignumData] = useState<LignumData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // State for 3D plot data lengths
  const [totalPoints, setTotalPoints] = useState<number>(0);
  const [meetsReqs, setMeetsReqs] = useState<number>(0);
  const [meetsReqsWithTol, setMeetsReqsWithTol] = useState<number>(0);
  const [failsReqs, setFailsReqs] = useState<number>(0);
  const plotRef = useRef<any>(null);
  const cameraRef = useRef<any>({
    eye: { x: 1.5, y: 1.5, z: 1.5 },
    center: { x: 0, y: 0, z: 0 },
    up: { x: 0, y: 0, z: 1 }
  });
  // State to memorize preFilter for each wall
  const [wallPreFilters, setWallPreFilters] = useState<{ [wallName: string]: PreFilterRequest | null }>({});
  const [currentPreFilter, setCurrentPreFilter] = useState<PreFilterRequest | null>(null);
  const [debouncedParams, setDebouncedParams] = useState({ tThresh, pThresh, uThresh, tTol, pTol, uTol, sampling, tThreshOp, pThreshOp, uThreshOp });

  // Debounce filter parameters to prevent excessive API calls
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedParams({ tThresh, pThresh, uThresh, tTol, pTol, uTol, sampling, tThreshOp, pThreshOp, uThreshOp });
    }, 300); // 300ms delay

    return () => clearTimeout(timer);
  }, [tThresh, pThresh, uThresh, tTol, pTol, uTol, sampling, tThreshOp, pThreshOp, uThreshOp]);

  const fetchProductLayersData = React.useCallback(async () => {
    if (!bauteilTyp || !walls || walls.length === 0) return;
    
    try {
      const productLayers: { [productName: string]: string[] } = {};
      
      // Filter walls based on bauteilTyp
      const filteredWalls = walls.filter(wall => wall.includes(bauteilTyp));
      
      // Fetch layer data for each wall of this bauteilTyp
      for (const wallName of filteredWalls) {
        try {
          const productType = wallName.split(' ')[0];
          const response = await fetch(`${API_BASE_URL}/buildups/${productType}/${encodeURIComponent(wallName)}/layers`);
          if (response.ok) {
            const data: LayersResponse = await response.json();
            // Extract layer names from the layers data
            const layerNames = Object.keys(data.layers);
            productLayers[wallName] = layerNames;
          } else {
            productLayers[wallName] = [];
          }
        } catch (err) {
          console.error(`Error fetching layers data for ${wallName}:`, err);
          productLayers[wallName] = [];
        }
      }
      
      setProductLayersData(productLayers);
      console.log('Product layers data:', productLayers);
    } catch (err) {
      console.error('Error fetching product layers data:', err);
      setProductLayersData({});
    }
  }, [bauteilTyp, walls]);



  const fetchLignumData = React.useCallback(async () => {
    if (!key) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/lignum/${encodeURIComponent(key)}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch Lignum data');
      }

      const data: LignumData = await response.json();
      setLignumData(data);
    } catch (err) {
      console.error('Error fetching Lignum data:', err);
      setLignumData(null);
    }
  }, [key]);

  const fetchProducts = React.useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/buildups/${bauteilTyp}`);
      if (!response.ok) {
        throw new Error('Failed to fetch products');
      }
      const allProductsData = await response.json();
      console.log('All products received from backend:', allProductsData); // Debug log
      
      setWalls(allProductsData);
      
      if (allProductsData.length > 0) {
        setKey(allProductsData[0]);
      } else {
        setKey('');
      }
    } catch (err) {
      setError('Failed to load product types');
      console.error('Error fetching products:', err);
    }
  }, [bauteilTyp]);

  // Fetch available products when component mounts or bauteilTyp changes
  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  // Fetch product layers data when bauteilTyp or walls change
  useEffect(() => {
    fetchProductLayersData();
  }, [fetchProductLayersData]);

  const fetchFilteredData = React.useCallback(async () => {
    if (!key) return;
    
    setLoading(true);
    setError(null);
    
          try {
        // Prepare the preFilter for the request
        const requestPreFilter = key === "All" ? 
          null :  // When "All" is selected, no preFilter is applied
          (wallPreFilters[key] ? wallPreFilters[key]?.preFilter : null);

        console.log('Sending request with preFilter:', requestPreFilter);
        
        const response = await fetch(`${API_BASE_URL}/requirement_profiles/apply`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            product: key,
            tThresh: debouncedParams.tThresh,
            pThresh: debouncedParams.pThresh,
            uThresh: debouncedParams.uThresh,
            tTol: debouncedParams.tTol,
            pTol: debouncedParams.pTol,
            uTol: debouncedParams.uTol,
            sampling: debouncedParams.sampling === 'none' ? null : debouncedParams.sampling,
            preFilter: requestPreFilter,
            tThreshOp: debouncedParams.tThreshOp,
            pThreshOp: debouncedParams.pThreshOp,
            uThreshOp: debouncedParams.uThreshOp,
          }),
        });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Backend error response:', errorText);
        throw new Error(`Failed to fetch filtered data: ${response.status} ${response.statusText}`);
      }

      const data: AllProductsFilterResponse | SingleProductFilterResponse = await response.json();
      
      // Convert new data structure to old format for backward compatibility
      const convertNewDataToOldFormat = (newData: { [productName: string]: Array<ProductCombination> }) => {
        const flatData: number[][] = [];
        const flatLayerThicknesses: number[][] = [];
        const flatProductNames: string[] = [];
        const flatColors: string[] = [];
        const flatSoftViolations: (number | undefined)[] = [];
        
        Object.entries(newData).forEach(([productName, items]) => {
          items.forEach(item => {
            flatData.push(item.performances);
            flatLayerThicknesses.push(item.thicknesses);
            flatProductNames.push(productName);
            if (item.color) {
              flatColors.push(item.color);
            }
            flatSoftViolations.push(item.soft_violation);
          });
        });
        
        return { flatData, flatLayerThicknesses, flatProductNames, flatColors, flatSoftViolations };
      };
      
      // Convert meets_req data
      const meetsData = convertNewDataToOldFormat(data.meets_req);
      const meetsWithTolData = convertNewDataToOldFormat(data.meets_req_with_tol);
      const failsData = convertNewDataToOldFormat(data.fails_req);
      
      // Store converted data for statistics and components
      setMeetsReqData(meetsData.flatData);
      setMeetsReqWithTolData(meetsWithTolData.flatData);
      // Combine layer thicknesses from both exact and tolerance matches
      setLayerThicknesses([...meetsData.flatLayerThicknesses, ...meetsWithTolData.flatLayerThicknesses]);
      setWallNames([...meetsData.flatProductNames, ...meetsWithTolData.flatProductNames]);
      setRawMeetsReqData(data.meets_req); // Store raw data for advanced features
      setRawMeetsReqWithTolData(data.meets_req_with_tol); // Store raw tolerance data
      
      // Calculate and set data lengths for 3D plot
      const totalMeetsReqs = meetsData.flatData.length;
      const totalMeetsReqsWithTol = meetsWithTolData.flatData.length;
      const totalFailsReqs = failsData.flatData.length;
      const totalPointsCount = totalMeetsReqs + totalMeetsReqsWithTol + totalFailsReqs;
      
      setMeetsReqs(totalMeetsReqs);
      setMeetsReqsWithTol(totalMeetsReqsWithTol);
      setFailsReqs(totalFailsReqs);
      setTotalPoints(totalPointsCount);

      
      // Transform data for Plotly
      const transformedData = [
        {
          x: meetsData.flatData.map((point: number[]) => point[0]), // thickness
          y: meetsData.flatData.map((point: number[]) => point[1]), // price
          z: meetsData.flatData.map((point: number[]) => point[2]), // u_value
          mode: 'markers',
          type: 'scatter3d',
          marker: { color: 'green', size: 6 },
          name: `Meets req (${totalMeetsReqs})`,
          text: meetsData.flatData.map((point: number[], index: number) => {
            const productName = meetsData.flatProductNames[index] || 'Unknown';
            const layerThicknesses = meetsData.flatLayerThicknesses[index] || [];
            const layerNames = productLayersData[productName] || [];
            
            let tooltip = '';
            if (key === "All") {
              tooltip += `<b>${productName}</b><br>`;
            }
            
            // Add layer thicknesses with better formatting
            if (layerNames.length > 0 && layerThicknesses.length > 0) {
              tooltip += '<b>Layer Thicknesses:</b><br>';
              tooltip += layerNames.map((layerName, i) => 
                `  ${layerName}: ${layerThicknesses[i] || 0}mm`
              ).join('<br>') + '<br>';
            }
            
            tooltip += `<b>Performance:</b><br>` +
                      `  Thickness: ${point[0].toFixed(1)} mm<br>` +
                      `  Price: ${point[1].toFixed(0)} CHF/m²<br>` +
                      `  U-Value: ${point[2].toFixed(3)} W/m²K`;
            
            return tooltip;
          }),
          hovertemplate: 
            '%{text}' +
            '<extra></extra>',
          hoverinfo: 'text'
        },
        {
          x: meetsWithTolData.flatData.map((point: number[]) => point[0]), // thickness
          y: meetsWithTolData.flatData.map((point: number[]) => point[1]), // price
          z: meetsWithTolData.flatData.map((point: number[]) => point[2]), // u_value
          mode: 'markers',
          type: 'scatter3d',
          marker: { 
            color: meetsWithTolData.flatColors && meetsWithTolData.flatColors.length > 0 
              ? meetsWithTolData.flatColors 
              : 'orange', 
            size: 6 
          },
          name: `Meets with tolerance (${totalMeetsReqsWithTol})`,
          text: meetsWithTolData.flatData.map((point: number[], index: number) => {
            const productName = meetsWithTolData.flatProductNames[index] || 'Unknown';
            const layerThicknesses = meetsWithTolData.flatLayerThicknesses[index] || [];
            const layerNames = productLayersData[productName] || [];
            const softViolation = meetsWithTolData.flatSoftViolations[index];
            
            let tooltip = '';
            if (key === "All") {
              tooltip += `<b>${productName}</b><br>`;
            }
            
            // Add layer thicknesses with better formatting
            if (layerNames.length > 0 && layerThicknesses.length > 0) {
              tooltip += '<b>Layer Thicknesses:</b><br>';
              tooltip += layerNames.map((layerName, i) => 
                `  ${layerName}: ${layerThicknesses[i] || 0}mm`
              ).join('<br>') + '<br>';
            }
            
            tooltip += `<b>Performance:</b><br>` +
                      `  Thickness: ${point[0].toFixed(1)} mm<br>` +
                      `  Price: ${point[1].toFixed(0)} CHF/m²<br>` +
                      `  U-Value: ${point[2].toFixed(3)} W/m²K`;
            
            // Add soft violation score if available
            if (softViolation !== undefined && softViolation !== null) {
              tooltip += `<br><b>Soft Violation Score:</b> ${softViolation.toFixed(4)}`;
            }
            
            return tooltip;
          }),
          hovertemplate: 
            '%{text}' +
            '<extra></extra>',
          hoverinfo: 'text'
        },
        {
          x: failsData.flatData.map((point: number[]) => point[0]), // thickness
          y: failsData.flatData.map((point: number[]) => point[1]), // price
          z: failsData.flatData.map((point: number[]) => point[2]), // u_value
          mode: 'markers',
          type: 'scatter3d',
          marker: { color: 'red', size: 6 },
          name: `Fails req (${totalFailsReqs})`,
          text: failsData.flatData.map((point: number[], index: number) => {
            const productName = failsData.flatProductNames[index] || 'Unknown';
            const layerThicknesses = failsData.flatLayerThicknesses[index] || [];
            const layerNames = productLayersData[productName] || [];
            
            let tooltip = '';
            if (key === "All") {
              tooltip += `<b>${productName}</b><br>`;
            }
            
            // Add layer thicknesses with better formatting
            if (layerNames.length > 0 && layerThicknesses.length > 0) {
              tooltip += '<b>Layer Thicknesses:</b><br>';
              tooltip += layerNames.map((layerName, i) => 
                `  ${layerName}: ${layerThicknesses[i] || 0}mm`
              ).join('<br>') + '<br>';
            }
            
            tooltip += `<b>Performance:</b><br>` +
                      `  Thickness: ${point[0].toFixed(1)} mm<br>` +
                      `  Price: ${point[1].toFixed(0)} CHF/m²<br>` +
                      `  U-Value: ${point[2].toFixed(3)} W/m²K`;
            
            return tooltip;
          }),
          hovertemplate: 
            '%{text}' +
            '<extra></extra>',
          hoverinfo: 'text'
        },
        {
          x: [],
          y: [],
          z: [],
          mode: 'markers',
          type: 'scatter3d',
          marker: { color: 'blue', size: 0 },
          name: `Total points (${totalPointsCount})`,
          showlegend: true,
          visible: 'legendonly'
        },
      ];
      
      setPlotData(transformedData);
    } catch (err) {
      setError('Failed to load performance data');
      console.error('Error fetching filtered data:', err);
    } finally {
      setLoading(false);
    }
  }, [key, wallPreFilters, debouncedParams]);

  // Reset preFilters when wall changes (but keep them for other walls)
  const resetPreFiltersForWall = React.useCallback((wallName: string) => {
    // Only reset if the current preFilter is for a different wall
    setCurrentPreFilter(prev => {
      if (prev && prev.product !== wallName) {
        return null;
      }
      return prev;
    });
    // Don't clear wallPreFilters here - we want to keep them for other walls
  }, []);

  // Fetch filtered data when parameters change
  useEffect(() => {
    if (key) {
      // Reset current preFilter when wall changes
      resetPreFiltersForWall(key);
      
      // Fetch product data
      fetchFilteredData();
    }
  }, [key, debouncedParams, wallPreFilters[key]]);

  // Fetch Lignum data only when product changes (not when filter parameters change)
  useEffect(() => {
    if (key && key !== "All") {
      fetchLignumData();
    }
  }, [key, fetchLignumData]);

  const handleApplyPreFilter = (preFilter: PreFilterRequest) => {
    // Check if this is a reset operation (empty preFilter object)
    const isEmptyPreFilter = Object.keys(preFilter.preFilter).length === 0;
    
    if (isEmptyPreFilter) {
      // Check if this is a "Reset All" operation (from Reset All button)
      if (preFilter.product === "RESET_ALL") {
        // Reset ALL preFilters across all walls
        setWallPreFilters({});
        setCurrentPreFilter(null);
        console.log('Reset ALL pre-filters across all products');
        return;
      } else {
        // Reset the preFilter for this specific wall
        setWallPreFilters(prev => ({
          ...prev,
          [preFilter.product]: null
        }));
        setCurrentPreFilter(null);
        console.log('Reset pre-filter for wall:', preFilter.product);
        return;
      }
    } else {
      // Store the preFilter for this specific wall
      setWallPreFilters(prev => ({
        ...prev,
        [preFilter.product]: preFilter
      }));
      setCurrentPreFilter(preFilter);
      console.log('Applied pre-filter for wall:', preFilter.product, preFilter);
    }
    
    // The useEffect will automatically trigger a new filter request when wallPreFilters changes
    console.log('Pre-filter updated, useEffect will trigger new filter request');
  };

  return (
    <Box sx={{ 
      minHeight: '100vh',
      backgroundColor: 'rgba(201, 216, 201, 0.2)', // Updated to lighter mint green
    }}>
              <Box sx={{ 
          mb: 3, 
          textAlign: 'left',
          backgroundColor: 'rgb(215, 232, 215)',
          borderRadius: 3,
          p: 3,
          boxShadow: '0 4px 20px rgba(107, 142, 107, 0.2)',
          position: 'relative',
          overflow: 'hidden',
          border: '1px solid rgba(107, 142, 107, 0.3)'
        }}>
          <Typography 
            variant="h3" 
            sx={{ 
              fontWeight: 600,
              color: 'White',
              textShadow: '0 1px 2px rgba(0,0,0,0.3)',
              mb: 1,
              letterSpacing: '0.5px'
            }}
          >
            Dokwood
          </Typography>
          <Typography 
            variant="h5" 
            sx={{ 
              color: 'rgba(255,255,255,0.9)',
              fontWeight: 400,
              letterSpacing: '1px',
              textTransform: 'uppercase'
            }}
          >
            Product Matching Component
          </Typography>
        </Box>
      
      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}
      
      <Box sx={{ 
        display: 'flex', 
        gap: 4, 
        mb: 2,
        flexWrap: 'wrap',
        '& .MuiFormControl-root': {
          borderRadius: 1,
          height: '60px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          '& .MuiOutlinedInput-root': {
            backgroundColor: 'white',
          }
        },
        '& .MuiBox-root': {
          borderRadius: 1,
          px: 2,
          py: 0,
          boxShadow: 'none'
        },
        // Target the specific generated class
        '& [class*="css-"] .MuiBox-root': {
          paddingTop: 0,
          paddingBottom: 0
        }
      }}>
        <FormControl>
          <InputLabel id="data-source-label">Data Source</InputLabel>
          <Select
            labelId="data-source-label"
            value={dataSource}
            label="Data Source"
            onChange={e => setDataSource(e.target.value as string)}
            sx={{ minWidth: 180 }}
          >
            <MenuItem value="Schaerholz">Schaerholz</MenuItem>
            <MenuItem value="Grumpp_Maier">Grumpp_Maier</MenuItem>
          </Select>
        </FormControl>
        <FormControl>
          <InputLabel id="bauteil-typ-label">Bauteil Typ</InputLabel>
          <Select
            labelId="bauteil-typ-label"
            value={bauteilTyp}
            label="Bauteil Typ"
            onChange={e => setBauteilTyp(e.target.value as string)}
            sx={{ minWidth: 180 }}
          >
            <MenuItem value="Aussenwand">Aussenwand</MenuItem>
            <MenuItem value="Innerwand">Innerwand</MenuItem>
            <MenuItem value="Decken">Decken</MenuItem>
            <MenuItem value="Boden">Boden</MenuItem>
          </Select>
        </FormControl>
        <FormControl>
          <InputLabel id="key-label">{bauteilTyp}</InputLabel>
          <Select
            labelId="key-label" 
            value={key}
            label={bauteilTyp}
            onChange={e => setKey(e.target.value as string)}
            sx={{ minWidth: 120 }}
            disabled={walls.length === 0}
          >
            {walls.map((wall: string) => (
              <MenuItem key={wall} value={wall}>{wall}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <FormControl>
          <InputLabel id="sampling-label">Sampling</InputLabel>
          <Select
            labelId="sampling-label"  
            value={sampling}
            label="Sampling"
            onChange={e => setSampling(e.target.value as string)}
            sx={{ minWidth: 150 }}
          >
            <MenuItem value="none">none</MenuItem>
            <MenuItem value="horizontal">horizontal</MenuItem>
            <MenuItem value="vertical">vertical</MenuItem>
          </Select>
        </FormControl>
      </Box>
      
      {/* Checkboxes Row */}
      <Box sx={{ 
        display: 'flex', 
        gap: 3, 
        mb: 2,
        mt: -2,
        flexWrap: 'wrap',
        alignItems: 'center',
        minHeight: '30px'
      }}>
        <FormControlLabel
          control={
            <Checkbox
              checked={showRequirementProfile}
              onChange={(e) => setShowRequirementProfile(e.target.checked)}
            />
          }
          label="Set Requirement Profile"
        />
        <FormControlLabel
          control={
            <Checkbox
              checked={showPriorityRanking}
              onChange={(e) => setShowPriorityRanking(e.target.checked)}
            />
          }
          label="Show Priority Ranking"
        />
        <FormControlLabel
          control={
            <Checkbox
              checked={showLayers}
              onChange={(e) => setShowLayers(e.target.checked)}
            />
          }
          label="Show layers"
        />
        <FormControlLabel
          control={
            <Checkbox
              checked={showLignum}
              onChange={(e) => setShowLignum(e.target.checked)}
            />
          }
          label="Show Lignum reference"
        />
      </Box>
      
      {/* Requirement Profile Component */}
      {showRequirementProfile && (
        <Box sx={{ 
          mb: 3,
          backgroundColor: 'white',
          borderRadius: 2,
          p: 2,
          boxShadow: 2,
        }}>
          <RequirementProfile 
            profile={{
              tThresh,
              pThresh,
              uThresh,
              tTol,
              pTol,
              uTol,
              tThreshOp,
              pThreshOp,
              uThreshOp
            }}
            onChange={(profile) => {
              setTThresh(profile.tThresh);
              setPThresh(profile.pThresh);
              setUThresh(profile.uThresh);
              setTTol(profile.tTol);
              setPTol(profile.pTol);
              setUTol(profile.uTol);
              setTThreshOp(profile.tThreshOp);
              setPThreshOp(profile.pThreshOp);
              setUThreshOp(profile.uThreshOp);
            }}
          />
        </Box>
      )}
      
      {/* Priority Rankings Component */}
      {showPriorityRanking && (
        <Box sx={{ 
          mb: 3,
          backgroundColor: 'white',
          borderRadius: 2,
          p: 2,
          boxShadow: 2,
        }}>
          <Matching2 
            rankings={priorityRankings}
            onChange={setPriorityRankings}
          />
        </Box>
      )}
      
      {/* Layers Section */}
      {showLayers && key !== "All" && (
        <Box sx={{ 
          mb: 3,
          backgroundColor: 'white',
          borderRadius: 2,
          p: 2,
          boxShadow: 2,
        }}>
          <LayersVisualizationWrapper 
            wallName={key} 
            onApplyPreFilter={handleApplyPreFilter}
            storedPreFilter={wallPreFilters[key] || null}
          />
        </Box>
      )}
      
      {/* Lignum Data Section */}
      {showLignum && (
        <Box sx={{ 
          mb: 3,
          backgroundColor: 'white',
          borderRadius: 2,
          p: 2,
          boxShadow: 2,
          position: 'relative',
        }}>
          {loading && (
            <Box sx={{ 
              position: 'absolute', 
              top: '50%', 
              left: '50%', 
              transform: 'translate(-50%, -50%)',
              zIndex: 1,
              bgcolor: 'rgba(255,255,255,0.9)',
              borderRadius: 1,
              p: 1
            }}>
              <CircularProgress />
            </Box>
          )}
          {lignumData ? (
            <LignumVisualization lignumData={lignumData} />
          ) : (
            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              minHeight: '200px' 
            }}>
              <Typography variant="h6" color="text.secondary">
                {loading ? 'Loading Lignum data...' : 'No Lignum data available'}
              </Typography>
            </Box>
          )}
        </Box>
      )}
      
      <Box sx={{ 
        display: 'flex', 
        gap: 3, 
        flexDirection: { xs: 'column', md: 'row' } 
      }}>
        <Box sx={{ 
          flex: '1 1 700px', 
          position: 'relative',
          backgroundColor: 'white',
          borderRadius: 2,
          p: 1.5,
          boxShadow: 2,
        }}>
          <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
            Product Data Distribution
          </Typography>
          {loading && (
            <Box sx={{ 
              position: 'absolute', 
              top: '50%', 
              left: '50%', 
              transform: 'translate(-50%, -50%)',
              zIndex: 1,
              bgcolor: 'rgba(255,255,255,0.9)',
              borderRadius: 1,
              p: 1
            }}>
              <CircularProgress />
            </Box>
          )}
          {plotData.length > 0 && (
            <Plot
              ref={plotRef}
              data={plotData}
              layout={{
                width: 850,
                height: 700,
                title: `3D Performance Plot (Total: ${totalPoints}, Meets: ${meetsReqs}, Meets with tolerance: ${meetsReqsWithTol}, Fails: ${failsReqs})`,
                plot_bgcolor: 'white',
                paper_bgcolor: 'white',
                scene: {
                  xaxis: { 
                    title: {
                      text: 'Thickness [mm]',
                      font: { size: 14, color: 'black' }
                    },
                    showticklabels: true,
                    tickfont: { size: 12 },
                    showgrid: true,
                    gridcolor: 'lightgray'
                  },
                  yaxis: { 
                    title: {
                      text: 'Price [CHF/m²]',
                      font: { size: 14, color: 'black' }
                    },
                    showticklabels: true,
                    tickfont: { size: 12 },
                    showgrid: true,
                    gridcolor: 'lightgray'
                  },
                  zaxis: { 
                    title: {
                      text: 'U-Value [W/m²K]',
                      font: { size: 14, color: 'black' }
                    },
                    showticklabels: true,
                    tickfont: { size: 12 },
                    showgrid: true,
                    gridcolor: 'lightgray'
                  },
                  camera: cameraRef.current
                },
                autosize: true,
              }}
              config={{
                displayModeBar: true,
                responsive: true
              }}
              style={{ width: '100%', height: '100%' }}
              useResizeHandler={true}
              onUpdate={(figure: any) => {
                // Store camera position when user interacts with the plot
                if (figure.layout.scene && figure.layout.scene.camera) {
                  const newCamera = figure.layout.scene.camera;
                  // Only update if camera actually changed (not during data updates)
                  if (JSON.stringify(newCamera) !== JSON.stringify(cameraRef.current)) {
                    cameraRef.current = newCamera;
                  }
                }
              }}
              onInitialized={(figure: any) => {
                // Store initial camera position
                if (figure.layout.scene && figure.layout.scene.camera) {
                  cameraRef.current = figure.layout.scene.camera;
                }
              }}
            />
          )}
        </Box>
        <Box sx={{ 
          flex: '1 1 600px', 
          position: 'relative',
          backgroundColor: 'white',
          borderRadius: 2,
          p: 2,
          boxShadow: 2,
        }}>
          <PriceStatsVisualization meetsReqData={meetsReqData} />
        </Box>
      </Box>


      {/* Matching Combinations Table */}
      <Box sx={{ 
        mb: 3,
        backgroundColor: 'white',
        borderRadius: 2,
        p: 2,
        boxShadow: 2,
      }}>
        {key === "All" ? (
          <AllWallsCombinationsTable 
            meetsReqData={meetsReqData} 
            layerThicknesses={layerThicknesses}
            wallNames={wallNames}
            productLayersData={productLayersData}
            rawMeetsReqData={rawMeetsReqData}
            rawMeetsReqWithTolData={rawMeetsReqWithTolData}
          />
        ) : (
          <CombinationsTable 
            meetsReqData={meetsReqData} 
            meetsReqWithTolData={meetsReqWithTolData}
            layerThicknesses={layerThicknesses}
            productLayersData={productLayersData}
            wallName={key}
            rawMeetsReqData={rawMeetsReqData}
            rawMeetsReqWithTolData={rawMeetsReqWithTolData}
          />
        )}
      </Box>

      {/* All Walls Combinations Table */}
      {/* This section is now handled by the conditional rendering above */}
    </Box>
  );
}

export default App;
