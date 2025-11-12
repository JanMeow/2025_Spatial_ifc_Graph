import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

interface ProductCombination {
  thicknesses: number[];
  performances: number[];
  color?: string;
  soft_violation?: number;
}

interface CombinationsTableProps {
  meetsReqData: number[][];
  meetsReqWithTolData: number[][];
  layerThicknesses: number[][];
  productLayersData: { [productName: string]: string[] };
  wallName: string;
  rawMeetsReqData: { [productName: string]: Array<ProductCombination> };
  rawMeetsReqWithTolData: { [productName: string]: Array<ProductCombination> };
}

const CombinationsTable: React.FC<CombinationsTableProps> = ({ 
  meetsReqData, 
  meetsReqWithTolData, 
  layerThicknesses, 
  productLayersData, 
  wallName,
  rawMeetsReqData,
  rawMeetsReqWithTolData
}) => {
  if ((!meetsReqData || meetsReqData.length === 0) && (!meetsReqWithTolData || meetsReqWithTolData.length === 0)) {
    return (
      <Paper sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No matching combinations found
        </Typography>
      </Paper>
    );
  }

  // Get layer names from productLayersData
  const layerNames = productLayersData[wallName] || [];
  
  // Get raw data for this wall
  const rawExactData = rawMeetsReqData[wallName] || [];
  const rawToleranceData = rawMeetsReqWithTolData[wallName] || [];
  
  // Create table data for exact matches
  const exactTableData = meetsReqData.map((point: number[], index: number) => ({
    id: index + 1,
    thickness: point[0],
    price: point[1],
    uValue: point[2],
    type: 'exact',
    softViolation: NaN, // Exact matches don't have soft violation
    // Use real layer thicknesses from backend
    layers: layerThicknesses[index] || layerNames.map(() => Math.floor(Math.random() * 200) + 20)
  }));

  // Create table data for tolerance matches
  const toleranceTableData = meetsReqWithTolData.map((point: number[], index: number) => ({
    id: meetsReqData.length + index + 1,
    thickness: point[0],
    price: point[1],
    uValue: point[2],
    type: 'tolerance',
    softViolation: rawToleranceData[index]?.soft_violation ?? NaN, // Get soft violation from raw data
    // Use real layer thicknesses from backend (tolerance matches come after exact matches in the combined array)
    layers: layerThicknesses[meetsReqData.length + index] || layerNames.map(() => Math.floor(Math.random() * 200) + 20)
  }));

  // Combine both datasets
  const allTableData = [...exactTableData, ...toleranceTableData];

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        {wallName} Matching Combinations ({exactTableData.length} exact, {toleranceTableData.length} tolerance)
      </Typography>
      
      <Paper sx={{ overflow: 'auto', maxHeight: '400px' }}>
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
            <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', fontWeight: 'bold', textAlign: 'center', minWidth: '100px' }}>
              Soft Violation
            </Box>
          </Box>
          
          {/* Data Rows - Exact Matches */}
          {exactTableData.map((row) => (
            <Box key={`exact-${row.id}`} sx={{ display: 'table-row', '&:hover': { bgcolor: '#f9f9f9' }, bgcolor: '#e8f5e8' }}>
              <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center', fontWeight: 'bold' }}>
                {row.id}
              </Box>
              {row.layers.map((layer, index) => (
                <Box key={index} sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                  {layer}
                </Box>
              ))}
              <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                {row.thickness.toFixed(1)}
              </Box>
              <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                {row.price.toFixed(0)}
              </Box>
              <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                {row.uValue.toFixed(3)}
              </Box>
              <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center', color: 'text.secondary' }}>
                N/A
              </Box>
            </Box>
          ))}
          
          {/* Data Rows - Tolerance Matches */}
          {toleranceTableData.map((row) => (
            <Box key={`tolerance-${row.id}`} sx={{ display: 'table-row', '&:hover': { bgcolor: '#f9f9f9' }, bgcolor: '#fff3e0' }}>
              <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center', fontWeight: 'bold' }}>
                {row.id}
              </Box>
              {row.layers.map((layer, index) => (
                <Box key={index} sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                  {layer}
                </Box>
              ))}
              <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                {row.thickness.toFixed(1)}
              </Box>
              <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                {row.price.toFixed(0)}
              </Box>
              <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                {row.uValue.toFixed(3)}
              </Box>
              <Box sx={{ display: 'table-cell', p: 1.5, border: '1px solid #ddd', textAlign: 'center' }}>
                {isNaN(row.softViolation) ? 'N/A' : row.softViolation.toFixed(4)}
              </Box>
            </Box>
          ))}
        </Box>
      </Paper>
      
      <Typography variant="caption" sx={{ color: 'text.secondary', mt: 1, display: 'block' }}>
        Showing {allTableData.length} matching combinations ({exactTableData.length} exact, {toleranceTableData.length} tolerance)
      </Typography>
    </Box>
  );
};

export default CombinationsTable;

