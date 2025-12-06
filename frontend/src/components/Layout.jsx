import React, { useState } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  School as SchoolIcon,
  Book as BookIcon,
  Quiz as QuizIcon,
  Person as PersonIcon,
  Assessment as AssessmentIcon,
  Chat as ChatIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  Home as HomeIcon,
  People as PeopleIcon,
  History as HistoryIcon,
  BarChart as BarChartIcon,
  AccountCircle as AccountCircleIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';

const drawerWidth = 280;

const Layout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  const fullname = localStorage.getItem('fullname') || 'User';
  const email = localStorage.getItem('email') || '';

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('fullname');
    localStorage.removeItem('email');
    handleMenuClose();
    navigate('/login', { replace: true });
    window.location.reload();
  };

  // Navigation items based on role
  const getNavItems = () => {
    if (!token) return [];
    
    const commonItems = [
      { text: 'Dashboard', path: `/${role}/dashboard`, icon: <DashboardIcon /> },
    ];

    if (role === 'student') {
      return [
        ...commonItems,
        { text: 'Courses', path: '/student/courses', icon: <SchoolIcon /> },
        { text: 'Placement Test', path: '/student/placement-test', icon: <SpeedIcon /> },
        { text: 'Quiz History', path: '/student/quiz-history', icon: <HistoryIcon /> },
        { text: 'Progress', path: '/student/progress', icon: <AssessmentIcon /> },
        { text: 'Chatbot', path: '/student/chatbot', icon: <ChatIcon /> },
        { text: 'Profile', path: '/student/profile', icon: <PersonIcon /> },
      ];
    } else if (role === 'teacher') {
      return [
        ...commonItems,
        { text: 'Courses', path: '/teacher/courses', icon: <SchoolIcon /> },
        { text: 'Lessons', path: '/teacher/lessons', icon: <BookIcon /> },
        { text: 'Quizzes', path: '/teacher/quizzes', icon: <QuizIcon /> },
        { text: 'Subscribers', path: '/teacher/subscribers', icon: <PeopleIcon /> },
        { text: 'Grades', path: '/teacher/grades', icon: <BarChartIcon /> },
      ];
    } else if (role === 'admin') {
      return [
        ...commonItems,
        { text: 'Users', path: '/admin/users', icon: <PeopleIcon /> },
        { text: 'Courses', path: '/admin/courses', icon: <SchoolIcon /> },
        { text: 'Enrollments', path: '/admin/enrollments', icon: <BookIcon /> },
        { text: 'Logs', path: '/admin/logs', icon: <HistoryIcon /> },
        { text: 'Settings', path: '/admin/settings', icon: <SettingsIcon /> },
      ];
    }
    return [];
  };

  const navItems = getNavItems();

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box
        sx={{
          p: 3,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
        }}
      >
        <Typography variant="h5" fontWeight="bold" sx={{ mb: 0.5 }}>
          E-Learning
        </Typography>
        <Typography variant="body2" sx={{ opacity: 0.9 }}>
          {role ? `${role.charAt(0).toUpperCase() + role.slice(1)} Portal` : 'Platform'}
        </Typography>
      </Box>
      <List sx={{ flexGrow: 1, pt: 2 }}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5, px: 2 }}>
              <ListItemButton
                component={Link}
                to={item.path}
                selected={isActive}
                sx={{
                  borderRadius: 2,
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'white',
                    },
                  },
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isActive ? 'white' : 'text.secondary',
                    minWidth: 40,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </Box>
  );

  const showSidebar = !!token && navItems.length > 0;

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: showSidebar ? `calc(100% - ${drawerWidth}px)` : '100%' },
          ml: { md: showSidebar ? `${drawerWidth}px` : 0 },
          bgcolor: 'white',
          color: 'text.primary',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        }}
      >
        <Toolbar>
          {showSidebar && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { md: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
          )}
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
            <Link to="/" style={{ textDecoration: 'none', color: 'inherit' }}>
              E-Learning Platform
            </Link>
          </Typography>
          {token ? (
            <>
              <Button
                color="inherit"
                component={Link}
                to="/"
                sx={{ mr: 2, display: { xs: 'none', sm: 'block' } }}
              >
                <HomeIcon sx={{ mr: 1 }} />
                Home
              </Button>
              <IconButton onClick={handleMenuOpen} sx={{ ml: 1 }}>
                <Avatar sx={{ bgcolor: 'primary.main', width: 36, height: 36 }}>
                  {fullname.charAt(0).toUpperCase()}
                </Avatar>
              </IconButton>
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
              >
                <Box sx={{ px: 2, py: 1 }}>
                  <Typography variant="subtitle2" fontWeight="bold">
                    {fullname}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {email}
                  </Typography>
                </Box>
                <Divider />
                <MenuItem component={Link} to={`/${role}/profile`} onClick={handleMenuClose}>
                  <ListItemIcon>
                    <AccountCircleIcon fontSize="small" />
                  </ListItemIcon>
                  Profile
                </MenuItem>
                <MenuItem onClick={handleLogout}>
                  <ListItemIcon>
                    <LogoutIcon fontSize="small" />
                  </ListItemIcon>
                  Logout
                </MenuItem>
              </Menu>
            </>
          ) : (
            <Button
              variant="contained"
              component={Link}
              to="/login"
              sx={{
                ml: 2,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%)',
                },
              }}
            >
              Login
            </Button>
          )}
        </Toolbar>
      </AppBar>

      {/* Drawer - Only show when logged in */}
      {showSidebar && (
        <Box
          component="nav"
          sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
        >
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{ keepMounted: true }}
            sx={{
              display: { xs: 'block', md: 'none' },
              '& .MuiDrawer-paper': {
                boxSizing: 'border-box',
                width: drawerWidth,
              },
            }}
          >
            {drawer}
          </Drawer>
          <Drawer
            variant="permanent"
            sx={{
              display: { xs: 'none', md: 'block' },
              '& .MuiDrawer-paper': {
                boxSizing: 'border-box',
                width: drawerWidth,
                borderRight: '1px solid',
                borderColor: 'divider',
              },
            }}
            open
          >
            {drawer}
          </Drawer>
        </Box>
      )}

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: showSidebar ? `calc(100% - ${drawerWidth}px)` : '100%' },
          mt: { xs: '56px', md: '64px' },
          pb: !token ? '80px' : 3,
        }}
      >
        <Outlet />
      </Box>

      {/* Footer - Only show when not logged in */}
      {!token && (
        <Box
          component="footer"
          sx={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            py: 2,
            px: 2,
            bgcolor: 'background.paper',
            borderTop: '1px solid',
            borderColor: 'divider',
            textAlign: 'center',
            zIndex: 1000,
          }}
        >
          <Typography variant="body2" color="text.secondary">
            {'© '}
            {new Date().getFullYear()}
            {' E-Learning Platform. All rights reserved.'}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default Layout;
