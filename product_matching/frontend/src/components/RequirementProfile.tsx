import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, Select, MenuItem, FormControl, InputLabel, Slider, TextField, Button } from '@mui/material';


export interface RequirementProfileProps {
  tThresh: number;
  pThresh: number;
  uThresh: number;
  tTol: number;
  pTol: number;
  uTol: number;
  tThreshOp: "==" | "~=" | "<" | "<=" | ">" | ">=";
  pThreshOp: "==" | "~=" | "<" | "<=" | ">" | ">=";
  uThreshOp: "==" | "~=" | "<" | "<=" | ">" | ">=";
}

interface RequirementProfileComponentProps {
  profile: RequirementProfileProps;
  onChange: (profile: RequirementProfileProps) => void;
}

// Dummy for Requirement Profile 
const Default1: RequirementProfileProps = {
  tThresh: 350,
  pThresh: 350,
  uThresh: 0.2,
  tTol: 20,
  pTol: 10,
  uTol: 0.15,
  tThreshOp: "~=" as const,
  pThreshOp: "<=" as const,
  uThreshOp: "<=" as const,
}

const Default2: RequirementProfileProps = {
  tThresh: 400,
  pThresh: 400,
  uThresh: 0.15,
  tTol: 20,
  pTol: 10,
  uTol: 0.1,
  tThreshOp: "~=" as const,
  pThreshOp: "<=" as const,
  uThreshOp: "<=" as const,
}

const RequirementProfile: React.FC<RequirementProfileComponentProps> = ({ profile, onChange }) => {
  // Local state - changes are immediately propagated to parent
  const [localProfile, setLocalProfile] = useState<RequirementProfileProps>(profile);
  
  // State for managing saved profiles
  const [savedProfiles, setSavedProfiles] = useState<{ [key: string]: RequirementProfileProps }>({
    'Default1': Default1,
    'Default2': Default2,
  });
  
  // State for profile selection and naming
  const [selectedProfile, setSelectedProfile] = useState<string>('');
  const [newProfileName, setNewProfileName] = useState<string>('');

  // Sync local state with prop changes
  useEffect(() => {
    setLocalProfile(profile);
  }, [profile]);

  const handleValueChange = (key: keyof RequirementProfileProps, value: any) => {
    const newProfile = {
      ...localProfile,
      [key]: value
    };
    setLocalProfile(newProfile);
    onChange(newProfile); // Immediately propagate changes to parent
  };

  const handleLoadProfile = (profileName: string) => {
    if (profileName && savedProfiles[profileName]) {
      const loadedProfile = savedProfiles[profileName];
      setLocalProfile(loadedProfile);
      onChange(loadedProfile);
      setSelectedProfile(profileName);
    }
  };

  const handleSaveProfile = () => {
    if (newProfileName.trim() === '') {
      alert('Please enter a profile name');
      return;
    }
    
    if (savedProfiles[newProfileName]) {
      const confirmOverwrite = window.confirm(`Profile "${newProfileName}" already exists. Do you want to overwrite it?`);
      if (!confirmOverwrite) {
        return;
      }
    }
    
    setSavedProfiles({
      ...savedProfiles,
      [newProfileName]: { ...localProfile }
    });
    
    setSelectedProfile(newProfileName);
    setNewProfileName('');
    alert(`Profile "${newProfileName}" saved successfully!`);
  };

  return (
    <Paper sx={{ p: 3, backgroundColor: '#f8f9fa', borderRadius: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ color: 'primary.main', fontWeight: 'bold' }}>
          Requirement Profile
        </Typography>
      </Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Set threshold values and tolerances for product matching criteria
      </Typography>
      
      {/* Profile Management Section */}
      <Box sx={{ 
        mb: 3, 
        p: 2, 
        backgroundColor: 'white', 
        borderRadius: 1,
        border: '1px solid #e0e0e0'
      }}>
        <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 'bold', color: 'text.secondary' }}>
          Profile Management
        </Typography>
        
        <Box sx={{ 
          display: 'flex', 
          gap: 2, 
          flexWrap: 'wrap',
          alignItems: 'center'
        }}>
          {/* Load Existing Profile Dropdown */}
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel id="profile-select-label">Use Existing Profile</InputLabel>
            <Select
              labelId="profile-select-label"
              value={selectedProfile}
              label="Use Existing Profile"
              onChange={(e) => handleLoadProfile(e.target.value)}
              sx={{ backgroundColor: 'white' }}
            >
              <MenuItem value="">
                <em>Select a profile...</em>
              </MenuItem>
              {Object.keys(savedProfiles).map((profileName) => (
                <MenuItem key={profileName} value={profileName}>
                  {profileName}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          {/* Save New Profile Section */}
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <TextField
              label="New Profile Name"
              value={newProfileName}
              onChange={(e) => setNewProfileName(e.target.value)}
              size="small"
              placeholder="Enter profile name"
              sx={{ 
                minWidth: 200,
                backgroundColor: 'white'
              }}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleSaveProfile();
                }
              }}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleSaveProfile}
              sx={{ minWidth: '120px', height: '40px' }}
            >
              Save Profile
            </Button>
          </Box>
        </Box>
      </Box>
      
      <Box sx={{ 
        display: 'flex', 
        gap: 4, 
        flexWrap: 'wrap',
        '& .MuiFormControl-root': {
          borderRadius: 1,
          height: '80px',
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
      }}>
        {/* Thickness Slider */}
        <FormControl sx={{ minWidth: 220 }}>
          <InputLabel id="t-thresh-label" sx={{ 
            fontSize: '0.75rem', 
            color: 'text.secondary',
            transform: 'translate(14px, -8px)',
            '&.Mui-focused': {
              transform: 'translate(14px, -6px) scale(0.75)'
            },
          }}>Thickness</InputLabel>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            height: '56px',
            px: 2,
            border: '0.1px solid #ccc',
            backgroundColor: 'white',
          }}>
            <Slider 
              value={localProfile.tThresh} 
              min={100} 
              max={700} 
              step={10} 
              onChange={(_, v) => handleValueChange('tThresh', v as number)} 
              valueLabelDisplay="auto"
              sx={{ flex: 1, mr: 1 }}
            />
            <TextField
              value={localProfile.tThresh}
              onChange={(e) => {
                const value = parseInt(e.target.value);
                if (!isNaN(value)) {
                  handleValueChange('tThresh', value);
                }
              }}
              onBlur={(e) => {
                const value = parseInt(e.target.value);
                if (isNaN(value) || value < 100) {
                  handleValueChange('tThresh', 100);
                } else if (value > 700) {
                  handleValueChange('tThresh', 700);
                }
              }}
              size="small"
              sx={{ 
                width: '60px',
                '& .MuiOutlinedInput-root': {
                  height: '32px',
                  fontSize: '0.75rem'
                }
              }}
            />
            <Select
              value={localProfile.tThreshOp}
              onChange={(e) => handleValueChange('tThreshOp', e.target.value as "==" | "~=" | "<" | "<=" | ">" | ">=")}
              size="small"
              sx={{ 
                minWidth: '50px',
                height: '32px',
                '& .MuiOutlinedInput-root': {
                  height: '32px',
                  fontSize: '0.75rem'
                }
              }}
            >
              <MenuItem value="==">==</MenuItem>
              <MenuItem value="~=">~=</MenuItem>
              <MenuItem value="<">&lt;</MenuItem>
              <MenuItem value="<=">&lt;=</MenuItem>
              <MenuItem value=">">&gt;</MenuItem>
              <MenuItem value=">=">&gt;=</MenuItem>
            </Select>
          </Box>
        </FormControl>

        {/* t_tol Slider */}
        <FormControl sx={{ minWidth: 180 }}>
          <InputLabel id="t-tol-label" sx={{ 
            fontSize: '0.875rem', 
            color: 'text.secondary',
            transform: 'translate(14px, -6px) scale(0.75)',
            '&.Mui-focused': {
              transform: 'translate(14px, -6px) scale(0.75)'
            }
          }}>t_tol</InputLabel>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            height: '56px',
            px: 2,
            border: '1px solid #ccc',
            borderRadius: 1,
            backgroundColor: 'white'
          }}>
            <Slider 
              value={localProfile.tTol} 
              min={0} 
              max={50} 
              step={10} 
              onChange={(_, v) => handleValueChange('tTol', v as number)} 
              valueLabelDisplay="auto"
              sx={{ flex: 1, mr: 1 }}
            />
            <TextField
              value={localProfile.tTol}
              onChange={(e) => {
                const value = parseInt(e.target.value);
                if (!isNaN(value)) {
                  handleValueChange('tTol', value);
                }
              }}
              onBlur={(e) => {
                const value = parseInt(e.target.value);
                if (isNaN(value) || value < 0) {
                  handleValueChange('tTol', 0);
                } else if (value > 50) {
                  handleValueChange('tTol', 50);
                }
              }}
              size="small"
              sx={{ 
                width: '60px',
                '& .MuiOutlinedInput-root': {
                  height: '32px',
                  fontSize: '0.75rem'
                }
              }}
            />
          </Box>
        </FormControl>

        {/* Price Slider */}
        <FormControl sx={{ minWidth: 220 }}>
          <InputLabel id="p-thresh-label" sx={{ 
            fontSize: '0.875rem', 
            color: 'text.secondary',
            transform: 'translate(14px, -6px) scale(0.75)',
            '&.Mui-focused': {
              transform: 'translate(14px, -6px) scale(0.75)'
            }
          }}>Price</InputLabel>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            height: '56px',
            px: 2,
            border: '1px solid #ccc',
            borderRadius: 1,
            backgroundColor: 'white'
          }}>
            <Slider 
              value={localProfile.pThresh} 
              min={100} 
              max={500} 
              step={10} 
              onChange={(_, v) => handleValueChange('pThresh', v as number)} 
              valueLabelDisplay="auto"
              sx={{ flex: 1, mr: 1 }}
            />
            <TextField
              value={localProfile.pThresh}
              onChange={(e) => {
                const value = parseInt(e.target.value);
                if (!isNaN(value)) {
                  handleValueChange('pThresh', value);
                }
              }}
              onBlur={(e) => {
                const value = parseInt(e.target.value);
                if (isNaN(value) || value < 100) {
                  handleValueChange('pThresh', 100);
                } else if (value > 500) {
                  handleValueChange('pThresh', 500);
                }
              }}
              size="small"
              sx={{ 
                width: '60px',
                '& .MuiOutlinedInput-root': {
                  height: '32px',
                  fontSize: '0.75rem'
                }
              }}
            />
            <Select
              value={localProfile.pThreshOp}
              onChange={(e) => handleValueChange('pThreshOp', e.target.value as "==" | "~=" | "<" | "<=" | ">" | ">=")}
              size="small"
              sx={{ 
                minWidth: '50px',
                height: '32px',
                '& .MuiOutlinedInput-root': {
                  height: '32px',
                  fontSize: '0.75rem'
                }
              }}
            >
              <MenuItem value="==">==</MenuItem>
              <MenuItem value="~=">~=</MenuItem>
              <MenuItem value="<">&lt;</MenuItem>
              <MenuItem value="<=">&lt;=</MenuItem>
              <MenuItem value=">">&gt;</MenuItem>
              <MenuItem value=">=">&gt;=</MenuItem>
            </Select>
          </Box>
        </FormControl>

        {/* p_tol Slider */}
        <FormControl sx={{ minWidth: 180 }}>
          <InputLabel id="p-tol-label" sx={{ 
            fontSize: '0.875rem', 
            color: 'text.secondary',
            transform: 'translate(14px, -6px) scale(0.75)',
            '&.Mui-focused': {
              transform: 'translate(14px, -6px) scale(0.75)'
            }
          }}>p_tol</InputLabel>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            height: '56px',
            px: 2,
            border: '1px solid #ccc',
            borderRadius: 1,
            backgroundColor: 'white'
          }}>
            <Slider 
              value={localProfile.pTol} 
              min={0} 
              max={50} 
              step={5} 
              onChange={(_, v) => handleValueChange('pTol', v as number)} 
              valueLabelDisplay="auto"
              sx={{ flex: 1, mr: 1 }}
            />
            <TextField
              value={localProfile.pTol}
              onChange={(e) => {
                const value = parseInt(e.target.value);
                if (!isNaN(value)) {
                  handleValueChange('pTol', value);
                }
              }}
              onBlur={(e) => {
                const value = parseInt(e.target.value);
                if (isNaN(value) || value < 0) {
                  handleValueChange('pTol', 0);
                } else if (value > 50) {
                  handleValueChange('pTol', 50);
                }
              }}
              size="small"
              sx={{ 
                width: '60px',
                '& .MuiOutlinedInput-root': {
                  height: '32px',
                  fontSize: '0.75rem'
                }
              }}
            />
          </Box>
        </FormControl>

        {/* U-Value Slider */}
        <FormControl sx={{ minWidth: 220 }}>
          <InputLabel id="u-thresh-label" sx={{ 
            fontSize: '0.875rem', 
            color: 'text.secondary',
            transform: 'translate(14px, -6px) scale(0.75)',
            '&.Mui-focused': {
              transform: 'translate(14px, -6px) scale(0.75)'
            }
          }}>U-Value</InputLabel>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            height: '56px',
            px: 2,
            border: '1px solid #ccc',
            borderRadius: 1,
            backgroundColor: 'white'
          }}>
            <Slider 
              value={localProfile.uThresh} 
              min={0.1} 
              max={0.3} 
              step={0.005} 
              onChange={(_, v) => handleValueChange('uThresh', v as number)} 
              valueLabelDisplay="auto"
              sx={{ flex: 1, mr: 1 }}
            />
            <TextField
              value={localProfile.uThresh.toFixed(3)}
              onChange={(e) => {
                const value = parseFloat(e.target.value);
                if (!isNaN(value)) {
                  handleValueChange('uThresh', value);
                }
              }}
              onBlur={(e) => {
                const value = parseFloat(e.target.value);
                if (isNaN(value) || value < 0.1) {
                  handleValueChange('uThresh', 0.1);
                } else if (value > 0.3) {
                  handleValueChange('uThresh', 0.3);
                }
              }}
              size="small"
              sx={{ 
                width: '60px',
                '& .MuiOutlinedInput-root': {
                  height: '32px',
                  fontSize: '0.75rem'
                }
              }}
            />
            <Select
              value={localProfile.uThreshOp}
              onChange={(e) => handleValueChange('uThreshOp', e.target.value as "==" | "~=" | "<" | "<=" | ">" | ">=")}
              size="small"
              sx={{ 
                minWidth: '50px',
                height: '32px',
                '& .MuiOutlinedInput-root': {
                  height: '32px',
                  fontSize: '0.75rem'
                }
              }}
            >
              <MenuItem value="==">==</MenuItem>
              <MenuItem value="~=">~=</MenuItem>
              <MenuItem value="<">&lt;</MenuItem>
              <MenuItem value="<=">&lt;=</MenuItem>
              <MenuItem value=">">&gt;</MenuItem>
              <MenuItem value=">=">&gt;=</MenuItem>
            </Select>
          </Box>
        </FormControl>

        {/* u_tol Slider */}
        <FormControl sx={{ minWidth: 180 }}>
          <InputLabel id="u-tol-label" sx={{ 
            fontSize: '0.875rem', 
            color: 'text.secondary',
            transform: 'translate(14px, -6px) scale(0.75)',
            '&.Mui-focused': {
              transform: 'translate(14px, -6px) scale(0.75)'
            }
          }}>u_tol</InputLabel>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            height: '56px',
            px: 2,
            border: '1px solid #ccc',
            borderRadius: 1,
            backgroundColor: 'white'
          }}>
            <Slider 
              value={localProfile.uTol} 
              min={0} 
              max={0.3} 
              step={0.01} 
              onChange={(_, v) => handleValueChange('uTol', v as number)} 
              valueLabelDisplay="auto"
              sx={{ flex: 1, mr: 1 }}
            />
            <TextField
              value={localProfile.uTol.toFixed(2)}
              onChange={(e) => {
                const value = parseFloat(e.target.value);
                if (!isNaN(value)) {
                  handleValueChange('uTol', value);
                }
              }}
              onBlur={(e) => {
                const value = parseFloat(e.target.value);
                if (isNaN(value) || value < 0) {
                  handleValueChange('uTol', 0);
                } else if (value > 0.3) {
                  handleValueChange('uTol', 0.3);
                }
              }}
              size="small"
              sx={{ 
                width: '60px',
                '& .MuiOutlinedInput-root': {
                  height: '32px',
                  fontSize: '0.75rem'
                }
              }}
            />
          </Box>
        </FormControl>
      </Box>
    </Paper>
  );
};

export default RequirementProfile;

