import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'https://web-production-b3b40.up.railway.app';

function Dashboard({ user }) {
  const [stats, setStats] = useState({ item_count: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_URL}/api/profile`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setStats(response.data);
      } catch (err) {
        console.error('Failed to fetch stats:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="container">
      <div className="card">
        <h2>Welcome, {user?.username}!</h2>
        <p style={{ color: '#666', marginBottom: '2rem' }}>
          You're logged in to Phase 4 Dashboard
        </p>
        
        {loading ? (
          <div className="loading">Loading stats...</div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div className="card" style={{ background: '#3498db', color: 'white', marginBottom: 0 }}>
              <h3 style={{ marginBottom: '0.5rem' }}>Total Items</h3>
              <p style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>{stats.item_count}</p>
            </div>
            
            <div className="card" style={{ background: '#2ecc71', color: 'white', marginBottom: 0 }}>
              <h3 style={{ marginBottom: '0.5rem' }}>Account Status</h3>
              <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>Active</p>
            </div>
            
            <div className="card" style={{ background: '#9b59b6', color: 'white', marginBottom: 0 }}>
              <h3 style={{ marginBottom: '0.5rem' }}>Member Since</h3>
              <p style={{ fontSize: '1.2rem' }}>
                {new Date(user?.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        )}
      </div>
      
      <div className="card">
        <h3>Quick Actions</h3>
        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
          <a href="/items" className="btn btn-primary">View Items</a>
          <a href="/profile" className="btn btn-primary">View Profile</a>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
