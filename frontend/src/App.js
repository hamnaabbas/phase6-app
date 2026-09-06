import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import Items from './components/Items';
import Profile from './components/Profile';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    if (token && userData) {
      setIsAuthenticated(true);
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogin = (token, userData) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setIsAuthenticated(true);
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <Router>
      <div className="app">
        {isAuthenticated && (
          <nav className="nav">
            <div className="nav-brand">Phase 4 Dashboard</div>
            <div className="nav-links">
              <Link to="/dashboard">Dashboard</Link>
              <Link to="/items">Items</Link>
              <Link to="/profile">Profile</Link>
              <a href="#" onClick={(e) => { e.preventDefault(); handleLogout(); }}>Logout</a>
            </div>
          </nav>
        )}
        
        <Routes>
          <Route 
            path="/login" 
            element={
              <Login 
                onLogin={handleLogin} 
                isAuthenticated={isAuthenticated} 
              />
            } 
          />
          <Route 
            path="/register" 
            element={
              <Register 
                isAuthenticated={isAuthenticated} 
              />
            } 
          />
          <Route 
            path="/dashboard" 
            element={
              isAuthenticated ? 
                <Dashboard user={user} /> : 
                <Navigate to="/login" />
            } 
          />
          <Route 
            path="/items" 
            element={
              isAuthenticated ? 
                <Items /> : 
                <Navigate to="/login" />
            } 
          />
          <Route 
            path="/profile" 
            element={
              isAuthenticated ? 
                <Profile user={user} /> : 
                <Navigate to="/login" />
            } 
          />
          <Route 
            path="/" 
            element={
              <Navigate to={isAuthenticated ? "/dashboard" : "/login"} />
            } 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;