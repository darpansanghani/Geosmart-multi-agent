import React, { useState } from 'react';
import axios from 'axios';

const ComplaintForm = ({ selectedLocation, onComplaintSubmitted }) => {
  const [formData, setFormData] = useState({
    text: '',
    address: ''
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file size (5MB)
      if (file.size > 5242880) {
        setError('File size must be less than 5MB');
        return;
      }

      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        setError('Only image files (JPEG, PNG, GIF, WebP) are allowed');
        return;
      }

      setSelectedFile(file);
      setError(null);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveImage = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!selectedLocation) {
      setError('Please select a location on the map');
      return;
    }

    if (formData.text.trim().length < 10) {
      setError('Complaint description must be at least 10 characters');
      return;
    }

    setIsSubmitting(true);

    try {
      // Create FormData for file upload
      const submitData = new FormData();
      submitData.append('text', formData.text);
      submitData.append('latitude', selectedLocation.lat);
      submitData.append('longitude', selectedLocation.lng);
      if (formData.address) {
        submitData.append('address', formData.address);
      }
      if (selectedFile) {
        submitData.append('image', selectedFile);
      }

      const response = await axios.post('/api/complaints', submitData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data.success) {
        // Reset form
        setFormData({ text: '', address: '' });
        setSelectedFile(null);
        setPreviewUrl(null);
        
        // Notify parent component
        onComplaintSubmitted(response.data.data);
        
        // Show success message briefly
        setError(null);
      }
    } catch (err) {
      console.error('Error submitting complaint:', err);
      setError(err.response?.data?.message || 'Failed to submit complaint. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">Submit Complaint</h3>
        <p className="card-description">
          Click on the map to select a location, then describe the issue
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        {/* Location Status */}
        <div className="form-group">
          <label className="form-label">Location</label>
          {selectedLocation ? (
            <div style={{
              padding: 'var(--space-3)',
              background: 'rgba(52, 211, 153, 0.1)',
              border: '1px solid rgba(52, 211, 153, 0.3)',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.875rem',
              color: 'var(--accent-400)'
            }}>
              ✓ Location selected: {selectedLocation.lat.toFixed(5)}, {selectedLocation.lng.toFixed(5)}
            </div>
          ) : (
            <div style={{
              padding: 'var(--space-3)',
              background: 'rgba(156, 163, 175, 0.1)',
              border: '1px solid rgba(156, 163, 175, 0.3)',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.875rem',
              color: 'var(--text-tertiary)'
            }}>
              Click on the map to select a location
            </div>
          )}
        </div>

        {/* Complaint Text */}
        <div className="form-group">
          <label className="form-label" htmlFor="complaint-text">
            Complaint Description *
          </label>
          <textarea
            id="complaint-text"
            className="form-textarea"
            placeholder="Describe the issue in detail..."
            value={formData.text}
            onChange={(e) => setFormData({ ...formData, text: e.target.value })}
            required
            disabled={isSubmitting}
          />
          <p className="form-hint">
            Minimum 10 characters. Be specific about the issue.
          </p>
        </div>

        {/* Address */}
        <div className="form-group">
          <label className="form-label" htmlFor="address">
            Address (Optional)
          </label>
          <input
            type="text"
            id="address"
            className="form-input"
            placeholder="e.g., Road No 14, Banjara Hills"
            value={formData.address}
            onChange={(e) => setFormData({ ...formData, address: e.target.value })}
            disabled={isSubmitting}
          />
        </div>

        {/* Image Upload */}
        <div className="form-group">
          <label className="form-label" htmlFor="image">
            Upload Image (Optional)
          </label>
          
          {/* Image Preview */}
          {previewUrl && (
            <div style={{
              marginBottom: 'var(--space-3)',
              position: 'relative',
              borderRadius: 'var(--radius-md)',
              overflow: 'hidden',
              border: '1px solid var(--border-color)'
            }}>
              <img 
                src={previewUrl} 
                alt="Preview" 
                style={{
                  width: '100%',
                  maxHeight: '200px',
                  objectFit: 'cover'
                }}
              />
              <button
                type="button"
                onClick={handleRemoveImage}
                style={{
                  position: 'absolute',
                  top: 'var(--space-2)',
                  right: 'var(--space-2)',
                  background: 'rgba(0, 0, 0, 0.7)',
                  color: 'white',
                  border: 'none',
                  borderRadius: 'var(--radius-full)',
                  width: '28px',
                  height: '28px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1rem'
                }}
              >
                ×
              </button>
            </div>
          )}

          <input
            type="file"
            id="image"
            accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
            onChange={handleFileChange}
            disabled={isSubmitting}
            style={{
              width: '100%',
              padding: 'var(--space-3)',
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text-primary)',
              fontSize: '0.875rem',
              cursor: 'pointer'
            }}
          />
          <p className="form-hint">
            Max size: 5MB. Formats: JPEG, PNG, GIF, WebP
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div style={{
            padding: 'var(--space-3)',
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.875rem',
            color: 'var(--error-400)',
            marginBottom: 'var(--space-4)'
          }}>
            {error}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          className="btn btn-primary btn-full"
          disabled={isSubmitting || !selectedLocation}
        >
          {isSubmitting ? (
            <>
              <span className="loading-spinner"></span>
              Processing with AI Agents...
            </>
          ) : (
            <>
              🤖 Submit & Process with Multi-Agent AI
            </>
          )}
        </button>

        {isSubmitting && (
          <p style={{
            fontSize: '0.75rem',
            color: 'var(--text-tertiary)',
            textAlign: 'center',
            marginTop: 'var(--space-2)'
          }}>
            Coordinating 5+ specialized agents...
          </p>
        )}
      </form>
    </div>
  );
};

export default ComplaintForm;
