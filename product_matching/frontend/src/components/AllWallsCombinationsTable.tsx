import React, { useState, useMemo } from 'react';
import { Box, Typography, Paper, Chip } from '@mui/material';

interface AllWallsCombinationsTableProps {
  meetsReqData: number[][];
  layerThicknesses: number[][];
  wallNames: string[];
  productLayersData: { [productName: string]: string[] };
  rawMeetsReqData?: { [productName: string]: Array<{ thicknesses: number[], performances: number[] }> };
  rawMeetsReqWithTolData?: { [productName: string]: Array<{ thicknesses: number[], performances: number[] }> };
}

const AllWallsCombinationsTable: React.FC<AllWallsCombinationsTableProps> = ({ 
  meetsReqData, 
  layerThicknesses, 
  wallNames, 
  productLayersData, 
  rawMeetsReqData, 
  rawMeetsReqWithTolData 
}) => {
  const [selectedWall, setSelectedWall] = useState<string>('');

  // Use raw data if available, otherwise fall back to old grouped data
  const groupedData = useMemo(() => {
    if (rawMeetsReqData && Object.keys(rawMeetsReqData).length > 0) {
      // Use the new raw data structure
      const grouped: { [wallName: string]: { data: number[][], layers: number[][], indices: number[], toleranceData: number[][], toleranceLayers: number[][], toleranceIndices: number[] } } = {};
      
      Object.entries(rawMeetsReqData).forEach(([productName, items]) => {
        grouped[productName] = { data: [], layers: [], indices: [], toleranceData: [], toleranceLayers: [], toleranceIndices: [] };
        
        items.forEach((item, index) => {
          grouped[productName].data.push(item.performances);
          grouped[productName].layers.push(item.thicknesses);
          grouped[productName].indices.push(index);
        });
      });
      
      // Add tolerance data if available
      if (rawMeetsReqWithTolData && Object.keys(rawMeetsReqWithTolData).length > 0) {
        Object.entries(rawMeetsReqWithTolData).forEach(([productName, items]) => {
          if (!grouped[productName]) {
            grouped[productName] = { data: [], layers: [], indices: [], toleranceData: [], toleranceLayers: [], toleranceIndices: [] };
          }
          
          items.forEach((item, index) => {
            grouped[productName].toleranceData.push(item.performances);
            grouped[productName].toleranceLayers.push(item.thicknesses);
            grouped[productName].toleranceIndices.push(index);
          });
        });
      }
      
      return grouped;
    } else {
      // Fallback to old grouping logic
      const grouped: { [wallName: string]: { data: number[][], layers: number[][], indices: number[], toleranceData: number[][], toleranceLayers: number[][], toleranceIndices: number[] } } = {};
      
      meetsReqData.forEach((dataPoint, index) => {
        const wallName = wallNames[index] || 'Unknown';
        if (!grouped[wallName]) {
          grouped[wallName] = { data: [], layers: [], indices: [], toleranceData: [], toleranceLayers: [], toleranceIndices: [] };
        }
        grouped[wallName].data.push(dataPoint);
        grouped[wallName].layers.push(layerThicknesses[index] || []);
        grouped[wallName].indices.push(index);
      });
      
      return grouped;
    }
  }, [rawMeetsReqData, rawMeetsReqWithTolData, wallNames, meetsReqData, layerThicknesses]);

  // Get unique wall names
  const uniqueWallNames = Object.keys(groupedData);
  
  // Find the first wall that has matching combinations
  const firstWallWithData = uniqueWallNames.find(wallName => groupedData[wallName].data.length > 0);
  
  // Update selected wall when data changes
  React.useEffect(() => {
    if (uniqueWallNames.length > 0) {
      const newSelectedWall = firstWallWithData || uniqueWallNames[0];
      
      // Check if current selection is valid and has data
      const currentWallHasData = selectedWall && 
        uniqueWallNames.includes(selectedWall) && 
        groupedData[selectedWall] && 
        groupedData[selectedWall].data.length > 0;
      
      // Auto-select if:
      // 1. No current selection, OR
      // 2. Current selection doesn't exist in new data, OR  
      // 3. Current selection has no data
      if (!selectedWall || 
          !uniqueWallNames.includes(selectedWall) || 
          !currentWallHasData) {
        console.log(`Auto-switching from "${selectedWall}" to "${newSelectedWall}" because current wall has no data`);
        setSelectedWall(newSelectedWall);
      }
    }
  }, [meetsReqData, wallNames, uniqueWallNames, firstWallWithData, selectedWall, groupedData]);

  if (!meetsReqData || meetsReqData.length === 0) {
    return (
      <Paper sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No matching combinations found across all walls
        </Typography>
      </Paper>
    );
  }

  const selectedWallData = selectedWall ? groupedData[selectedWall] : null;
  const layerNames = selectedWall ? (productLayersData[selectedWall] || []) : [];

  // If no wall is selected or selected wall has no data, auto-select the first wall with data
  if (!selectedWallData || selectedWallData.data.length === 0) {
    if (firstWallWithData && firstWallWithData !== selectedWall) {
      console.log(`Fallback: Auto-selecting "${firstWallWithData}" because current selection has no data`);
      setSelectedWall(firstWallWithData);
      return null; // Return null to trigger re-render
    }
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        All Matching Combinations
      </Typography>
      
      {/* Summary of all walls */}
      <Box sx={{ mb: 2, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold' }}>
          Available Types with Matches:
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {uniqueWallNames.map((wallName) => (
            <Chip
              key={wallName}
              label={`${wallName}: ${groupedData[wallName].data.length} exact, ${groupedData[wallName].toleranceData.length} tolerance`}
              size="small"
              variant="outlined"
              sx={{ 
                bgcolor: 'white',
                borderColor: '#1976d2',
                color: '#1976d2'
              }}
            />
          ))}
        </Box>
      </Box>

      {/* Wall Type Selector */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 'bold' }}>
          Select Wall Type to View Details:
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {uniqueWallNames.map((wallName) => (
            <Chip
              key={wallName}
              label={`${wallName} (${groupedData[wallName].data.length + groupedData[wallName].toleranceData.length})`}
              onClick={() => setSelectedWall(wallName)}
              color={selectedWall === wallName ? 'primary' : 'default'}
              variant={selectedWall === wallName ? 'filled' : 'outlined'}
              sx={{ 
                cursor: 'pointer',
                '&:hover': { 
                  opacity: 0.8,
                  transform: 'scale(1.05)'
                },
                transition: 'all 0.2s ease-in-out'
              }}
            />
          ))}
        </Box>
      </Box>

      {selectedWallData && (
        <Box>
          <Typography variant="subtitle1" gutterBottom sx={{ color: 'primary.main', fontWeight: 'bold' }}>
            {selectedWall} - {selectedWallData.data.length} exact matches, {selectedWallData.toleranceData.length} tolerance matches
          </Typography>
          
          <Paper sx={{ overflow: 'auto', maxHeight: '500px' }}>
            <Box sx={{ display: 'table', width: '100%', borderCollapse: 'collapse' }}>
              {/* Header Row */}
              <Box sx={{ display: 'table-row', bgcolor: '#f5f5f5' }}>
                <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', fontWeight: 'bold', textAlign: 'center', minWidth: '50px' }}>
                  #
                </Box>
                {layerNames.map((layerName, index) => (
                  <Box key={index} sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', fontWeight: 'bold', textAlign: 'center', minWidth: '120px' }}>
                    {layerName}
                  </Box>
                ))}
                <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', fontWeight: 'bold', textAlign: 'center', minWidth: '100px' }}>
                  Thickness (mm)
                </Box>
                <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', fontWeight: 'bold', textAlign: 'center', minWidth: '100px' }}>
                  Price (CHF/m²)
                </Box>
                <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', fontWeight: 'bold', textAlign: 'center', minWidth: '100px' }}>
                  U-Value (W/m²K)
                </Box>
              </Box>
              
              {/* Data Rows - Exact Matches */}
              {selectedWallData.data.map((point: number[], index: number) => {
                const rowIndex = selectedWallData.indices[index];
                const layers = selectedWallData.layers[index] || layerNames.map(() => 0);
                
                return (
                  <Box key={`exact-${rowIndex}`} sx={{ display: 'table-row', '&:hover': { bgcolor: '#f9f9f9' }, bgcolor: '#e8f5e8' }}>
                    <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center', fontWeight: 'bold' }}>
                      {index + 1}
                    </Box>
                    {layers.map((layer, layerIndex) => (
                      <Box key={layerIndex} sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                        {layer}
                      </Box>
                    ))}
                    <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                      {point[0].toFixed(1)}
                    </Box>
                    <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                      {point[1].toFixed(0)}
                    </Box>
                    <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                      {point[2].toFixed(3)}
                    </Box>
                  </Box>
                );
              })}
              
              {/* Data Rows - Tolerance Matches */}
              {selectedWallData.toleranceData.map((point: number[], index: number) => {
                const rowIndex = selectedWallData.toleranceIndices[index];
                const layers = selectedWallData.toleranceLayers[index] || layerNames.map(() => 0);
                
                return (
                  <Box key={`tolerance-${rowIndex}`} sx={{ display: 'table-row', '&:hover': { bgcolor: '#f9f9f9' }, bgcolor: '#fff3e0' }}>
                    <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center', fontWeight: 'bold' }}>
                      {selectedWallData.data.length + index + 1}
                    </Box>
                    {layers.map((layer, layerIndex) => (
                      <Box key={layerIndex} sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                        {layer}
                      </Box>
                    ))}
                    <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                      {point[0].toFixed(1)}
                    </Box>
                    <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                      {point[1].toFixed(0)}
                    </Box>
                    <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                      {point[2].toFixed(3)}
                    </Box>
                  </Box>
                );
              })}
            </Box>
          </Paper>
          
          <Typography variant="caption" sx={{ color: 'text.secondary', mt: 1, display: 'block' }}>
            Total matching combinations across all walls: {Object.values(groupedData).reduce((total, wallData) => total + wallData.data.length + wallData.toleranceData.length, 0)}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default AllWallsCombinationsTable;

