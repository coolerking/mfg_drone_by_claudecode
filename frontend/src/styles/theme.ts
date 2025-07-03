import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0d6efd',
      light: '#4d8dff',
      dark: '#004cbf',
    },
    secondary: {
      main: '#6c757d',
      light: '#8e9aa9',
      dark: '#495057',
    },
    success: {
      main: '#198754',
      light: '#4db378',
      dark: '#0d5230',
    },
    warning: {
      main: '#ffc107',
      light: '#ffd54f',
      dark: '#bf8f00',
    },
    error: {
      main: '#dc3545',
      light: '#e57373',
      dark: '#c62828',
    },
    info: {
      main: '#0dcaf0',
      light: '#4dd4f0',
      dark: '#087990',
    },
    background: {
      default: '#f8f9fa',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Segoe UI", "Roboto", "Arial", sans-serif',
    h1: {
      fontWeight: 600,
      fontSize: '2.5rem',
    },
    h2: {
      fontWeight: 600,
      fontSize: '2rem',
    },
    h3: {
      fontWeight: 600,
      fontSize: '1.75rem',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
          borderRadius: 12,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: '1px solid #e9ecef',
        },
      },
    },
  },
})