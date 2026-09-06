import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function Profile({ user }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_URL}/api/profile`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setProfile(response.data);
      } catch (err) {
        console.error('Failed to fetch profile:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <div className="loading">Loading profile...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card">
        <h2>My Profile</h2>
        
        <div style={{ display: 'grid', gap: '1rem', maxWidth: '600px' }}>
          <div>
            <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '0.25rem' }}>Username</label>
            <p style={{ padding: '0.75rem', background: '#f8f9fa', borderRadius: '4px' }}>
              {user?.username}
            </p>
          </div>
          
          <div>
            <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '0.25rem' }}>Email</label>
            <p style={{ padding: '0.75rem', background: '#f8f9fa', borderRadius: '4px' }}>
              {user?.email}
            </p>
          </div>
          
          <div>
            <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '0.25rem' }}>Member Since</label>
            <p style={{ padding: '0.75rem', background: '#f8f9fa', borderRadius: '4px' }}>
              {new Date(user?.created_at).toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </p>
          </div>
          
          <div>
            <label style={{ fontWeight: 'bold', display: 'block', marginBottom: '0.25rem' }}>Total Items</label>
            <p style={{ padding: '0.75rem', background: '#f8f9fa', borderRadius: '4px' }}>
              {profile?.item_count || 0}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;