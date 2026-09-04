import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function Items() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [newItem, setNewItem] = useState({ name: '', description: '' });
  const [editingId, setEditingId] = useState(null);

  const token = localStorage.getItem('token');
  const headers = { Authorization: `Bearer ${token}` };

  const fetchItems = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/items`, { headers });
      setItems(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load items');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (editingId) {
        await axios.put(`${API_URL}/api/items/${editingId}`, newItem, { headers });
        setEditingId(null);
      } else {
        await axios.post(`${API_URL}/api/items`, newItem, { headers });
      }
      
      setNewItem({ name: '', description: '' });
      setShowForm(false);
      fetchItems();
    } catch (err) {
      setError('Failed to save item');
    }
  };

  const handleEdit = (item) => {
    setNewItem({ name: item.name, description: item.description });
    setEditingId(item.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this item?')) return;
    
    try {
      await axios.delete(`${API_URL}/api/items/${id}`, { headers });
      fetchItems();
    } catch (err) {
      setError('Failed to delete item');
    }
  };

  const cancelForm = () => {
    setNewItem({ name: '', description: '' });
    setEditingId(null);
    setShowForm(false);
  };

  return (
    <div className="container">
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2>My Items</h2>
          <button 
            className="btn btn-primary" 
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? 'Cancel' : 'Add New Item'}
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        {showForm && (
          <form onSubmit={handleSubmit} style={{ marginBottom: '2rem' }}>
            <div className="form-group">
              <label>Item Name</label>
              <input
                type="text"
                value={newItem.name}
                onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                required
                placeholder="Enter item name"
              />
            </div>
            
            <div className="form-group">
              <label>Description</label>
              <input
                type="text"
                value={newItem.description}
                onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                placeholder="Enter description (optional)"
              />
            </div>
            
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button type="submit" className="btn btn-primary">
                {editingId ? 'Update' : 'Create'}
              </button>
              <button type="button" className="btn btn-danger" onClick={cancelForm}>
                Cancel
              </button>
            </div>
          </form>
        )}

        {loading ? (
          <div className="loading">Loading items...</div>
        ) : items.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666' }}>
            No items yet. Click "Add New Item" to create one.
          </p>
        ) : (
          <div className="items-list">
            {items.map((item) => (
              <div key={item.id} className="item-card">
                <div className="item-info">
                  <h3>{item.name}</h3>
                  {item.description && <p>{item.description}</p>}
                  <p style={{ fontSize: '0.8rem', color: '#999', marginTop: '0.5rem' }}>
                    Created: {new Date(item.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="item-actions">
                  <button 
                    className="btn btn-primary btn-sm" 
                    onClick={() => handleEdit(item)}
                  >
                    Edit
                  </button>
                  <button 
                    className="btn btn-danger btn-sm" 
                    onClick={() => handleDelete(item.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Items;