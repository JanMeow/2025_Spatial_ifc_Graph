import React from 'react';
import Plot from 'react-plotly.js';
import { Box, Typography, Paper } from '@mui/material';
import type { PriceStats } from '../types/interfaces';

interface PriceStatsVisualizationProps {
  meetsReqData: number[][];
}

const PriceStatsVisualization: React.FC<PriceStatsVisualizationProps> = ({ meetsReqData }) => {
  if (meetsReqData.length === 0) {
    return (
      <Paper sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No data points meet the current requirements
        </Typography>
      </Paper>
    );
  }
  // Extract prices (index 1) and thicknesses (index 0) from data points
  const prices = meetsReqData.map((point: number[]) => point[1]).sort((a, b) => a - b);
  const thicknesses = meetsReqData.map((point: number[]) => point[0]).sort((a, b) => a - b);
  
  const priceStats: PriceStats = {
    max: Math.max(...prices),
    median: prices[Math.floor(prices.length / 2)],
    min: Math.min(...prices),
    count: prices.length
  };

  const thicknessStats = {
    max: Math.max(...thicknesses),
    median: thicknesses[Math.floor(thicknesses.length / 2)],
    min: Math.min(...thicknesses),
    count: thicknesses.length
  };

  // Create histogram data for prices
  const priceHistogramData = [
    {
      x: prices,
      type: 'histogram',
      nbinsx: 10,
      marker: {
        color: 'rgba(76, 175, 80, 0.7)',
        line: {
          color: 'rgba(76, 175, 80, 1)',
          width: 1
        }
      },
      name: 'Price Distribution'
    }
  ];

  // Create histogram data for thicknesses
  const thicknessHistogramData = [
    {
      x: thicknesses,
      type: 'histogram',
      nbinsx: 10,
      marker: {
        color: 'rgba(33, 150, 243, 0.7)',
        line: {
          color: 'rgba(33, 150, 243, 1)',
          width: 1
        }
      },
      name: 'Thickness Distribution'
    }
  ];

  return (
    <Box sx={{ width: '100%', overflow: 'hidden' }}>
      <Typography variant="h6" gutterBottom>
        Statistics for Points Meeting Requirements
      </Typography>
      
      {/* Total Points Row - Full Width */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.light', color: 'white', flex: 2 }}>
          <Typography variant="h4">{priceStats.count}</Typography>
          <Typography variant="body2">Total Points</Typography>
        </Paper>
        <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'warning.dark', color: 'white', flex: 1 }}>
          <Typography variant="h4">RF3</Typography>
          <Typography variant="body2">Overall Fire Rating</Typography>
        </Paper>
      </Box>

      {/* Price Statistics Row */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Paper sx={{ p: 1.5, textAlign: 'center', bgcolor: '#1976d2', color: 'white', flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography variant="h5" sx={{ fontWeight: 500 }}>Price</Typography>
        </Paper>
        <Paper sx={{ p: 1.2, textAlign: 'center', bgcolor: '#e3f2fd', color: '#1976d2', flex: 1 }}>
          <Typography variant="h4">{priceStats.max.toFixed(0)}</Typography>
          <Typography variant="body2">Max (CHF/m²)</Typography>
        </Paper>
        <Paper sx={{ p: 1.2, textAlign: 'center', bgcolor: '#e3f2fd', color: '#1976d2', flex: 1 }}>
          <Typography variant="h4">{priceStats.median.toFixed(0)}</Typography>
          <Typography variant="body2">Median (CHF/m²)</Typography>
        </Paper>
        <Paper sx={{ p: 1.2, textAlign: 'center', bgcolor: '#e3f2fd', color: '#1976d2', flex: 1 }}>
          <Typography variant="h4">{priceStats.min.toFixed(0)}</Typography>
          <Typography variant="body2">Min (CHF/m²)</Typography>
        </Paper>
      </Box>

      {/* Thickness Statistics Row */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Paper sx={{ p: 1.5, textAlign: 'center', bgcolor: '#ff9800', color: 'white', flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography variant="h5" sx={{ fontWeight: 500 }}>Thickness</Typography>
        </Paper>
        <Paper sx={{ p: 1.2, textAlign: 'center', bgcolor: '#fff3e0', color: '#f57c00', flex: 1 }}>
          <Typography variant="h4">{thicknessStats.max.toFixed(1)}</Typography>
          <Typography variant="body2">Max (mm)</Typography>
        </Paper>
        <Paper sx={{ p: 1.2, textAlign: 'center', bgcolor: '#fff3e0', color: '#f57c00', flex: 1 }}>
          <Typography variant="h4">{thicknessStats.median.toFixed(1)}</Typography>
          <Typography variant="body2">Median (mm)</Typography>
        </Paper>
        <Paper sx={{ p: 1.2, textAlign: 'center', bgcolor: '#fff3e0', color: '#f57c00', flex: 1 }}>
          <Typography variant="h4">{thicknessStats.min.toFixed(1)}</Typography>
          <Typography variant="body2">Min (mm)</Typography>
        </Paper>
      </Box>

      {/* Acoustic Performance Row */}
      <Box sx={{ mb: 2 }}>
        <Paper sx={{ p: 1.5, bgcolor: 'white' }}>
          <Plot
            data={[
              {
                x: [300, 320, 340, 360, 380, 400, 420, 440, 460, 480, 500], // More detailed thickness values
                y: [45, 44.5, 43.8, 42.2, 41.5, 40, 39.8, 38.5, 37.2, 36.8, 36], // Non-linear with spikes
                type: 'scatter',
                mode: 'lines+markers',
                line: { color: '#4caf50', width: 3 },
                marker: { color: '#4caf50', size: 8 },
                name: 'Acoustic Performance'
              }
            ]}
            layout={{
              width: undefined,
              height: 150,
              autosize: true,
              title: {
                text: 'Acoustic Performance vs Thickness',
                font: { size: 14, color: '#4caf50' }
              },
              xaxis: { 
                title: {
                  text: 'Thickness (mm)',
                  font: { size: 12, color: '#4caf50' }
                },
                showticklabels: true,
                tickfont: { size: 10 }
              },
              yaxis: { 
                title: {
                  text: 'Noise (dB)',
                  font: { size: 12, color: '#4caf50' }
                },
                showticklabels: true,
                tickfont: { size: 10 }
              },
              margin: { l: 60, r: 30, t: 50, b: 50 },
              showlegend: false
            }}
            config={{
              responsive: true,
              displayModeBar: false
            }}
            style={{ width: '100%', height: '100%' }}
            useResizeHandler={true}
          />
        </Paper>
      </Box>

      {/* Histograms side by side */}
      <Box sx={{ display: 'flex', gap: 2, flexDirection: { xs: 'column', md: 'row' } }}>
        <Box sx={{ flex: 1 }}>
          <Plot
            data={priceHistogramData}
            layout={{
              width: undefined,
              height: 250,
              autosize: true,
              title: {
                text: 'Price Distribution',
                font: { size: 14, color: 'black' }
              },
              xaxis: { 
                title: {
                  text: 'Price (CHF/m²)',
                  font: { size: 12, color: 'black' }
                },
                showticklabels: true,
                tickfont: { size: 10 }
              },
              yaxis: { 
                title: {
                  text: 'Number of Points',
                  font: { size: 12, color: 'black' }
                },
                showticklabels: true,
                tickfont: { size: 10 }
              },
              margin: { l: 50, r: 20, t: 40, b: 50 },
              showlegend: false
            }}
            config={{
              displayModeBar: false,
              responsive: true
            }}
            style={{ width: '100%', height: '100%' }}
          />
        </Box>
        <Box sx={{ flex: 1 }}>
          <Plot
            data={thicknessHistogramData}
            layout={{
              width: undefined,
              height: 250,
              autosize: true,
              title: {
                text: 'Thickness Distribution',
                font: { size: 14, color: 'black' }
              },
              xaxis: { 
                title: {
                  text: 'Thickness (mm)',
                  font: { size: 12, color: 'black' }
                },
                showticklabels: true,
                tickfont: { size: 10 }
              },
              yaxis: { 
                title: {
                  text: 'Number of Points',
                  font: { size: 12, color: 'black' }
                },
                showticklabels: true,
                tickfont: { size: 10 }
              },
              margin: { l: 50, r: 20, t: 40, b: 50 },
              showlegend: false
            }}
            config={{
              displayModeBar: false,
              responsive: true
            }}
            style={{ width: '100%', height: '100%' }}
          />
        </Box>
      </Box>
    </Box>
  );
};

export default PriceStatsVisualization;


