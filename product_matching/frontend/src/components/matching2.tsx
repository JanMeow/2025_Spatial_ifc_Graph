import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, Select, MenuItem, FormControl, InputLabel, Button } from '@mui/material';
import type { Matching2Props } from '../types/interfaces';

interface Matching2ComponentProps {
  rankings: Matching2Props;
  onChange: (rankings: Matching2Props) => void;
}

const Matching2: React.FC<Matching2ComponentProps> = ({ rankings, onChange }) => {
  // Local state for uncommitted changes
  const [localRankings, setLocalRankings] = useState<Matching2Props>(rankings);
  const [hasChanges, setHasChanges] = useState(false);

  // Sync local state with prop changes
  useEffect(() => {
    setLocalRankings(rankings);
    setHasChanges(false);
  }, [rankings]);

  const handleRankingChange = (key: keyof Matching2Props, value: number) => {
    setLocalRankings({
      ...localRankings,
      [key]: value
    });
    setHasChanges(true);
  };

  const handleCommit = () => {
    onChange(localRankings);
    setHasChanges(false);
  };

  const handleReset = () => {
    setLocalRankings(rankings);
    setHasChanges(false);
  };

  const rankOptions = [1, 2, 3, 4, 5];

  const criteriaLabels = {
    thickness: 'Thickness',
    price: 'Price',
    u_value: 'U-Value',
    acoustic: 'Acoustic',
    fire_rating: 'Fire Rating'
  };

  return (
    <Paper sx={{ p: 3, backgroundColor: '#f8f9fa', borderRadius: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ color: 'primary.main', fontWeight: 'bold' }}>
          Priority Rankings
        </Typography>
        {hasChanges && (
          <Typography variant="caption" color="warning.main" sx={{ fontWeight: 'bold' }}>
            ⚠ Unsaved changes
          </Typography>
        )}
      </Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Rank each criterion by priority (1 = highest priority, 5 = lowest priority)
      </Typography>
      
      <Box sx={{ 
        display: 'flex', 
        gap: 2, 
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        {Object.entries(criteriaLabels).map(([key, label]) => (
          <FormControl key={key} sx={{ minWidth: 180 }}>
            <InputLabel id={`${key}-label`}>{label}</InputLabel>
            <Select
              labelId={`${key}-label`}
              value={localRankings[key as keyof Matching2Props]}
              label={label}
              onChange={(e) => handleRankingChange(key as keyof Matching2Props, e.target.value as number)}
              sx={{ 
                backgroundColor: 'white',
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'white',
                }
              }}
            >
              {rankOptions.map((rank) => (
                <MenuItem key={rank} value={rank}>
                  {rank}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        ))}
        
        {/* Action Buttons - Inline with dropdowns */}
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <Button
            variant="outlined"
            color="secondary"
            onClick={handleReset}
            disabled={!hasChanges}
            sx={{ minWidth: '90px', height: '56px' }}
          >
            Reset
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={handleCommit}
            disabled={!hasChanges}
            sx={{ minWidth: '90px', height: '56px' }}
          >
            Commit
          </Button>
        </Box>
      </Box>
      
      {/* Display committed rankings summary */}
      <Box sx={{ mt: 2, p: 2, backgroundColor: 'white', borderRadius: 1 }}>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
          Committed Rankings:
        </Typography>
        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
          {Object.entries(rankings).map(([key, value]) => 
            `${key}: ${value}`
          ).join(', ')}
        </Typography>
      </Box>
    </Paper>
  );
};

export default Matching2;