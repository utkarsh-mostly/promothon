document.addEventListener('DOMContentLoaded', function() {
    // Enhanced feature display handler with better error recovery
    function displayFeatures(features) {
        if (features === null || features === undefined) {
            return 'No features available';
        }
        
        try {
            // Handle all possible feature formats
            let featureList;
            if (Array.isArray(features)) {
                featureList = features;
            } else if (typeof features === 'string') {
                // Try to parse as JSON first
                try {
                    const parsed = JSON.parse(features);
                    featureList = Array.isArray(parsed) ? parsed : [parsed];
                } catch (e) {
                    // If not JSON, split by commas
                    featureList = features.split(',')
                        .map(item => item.trim())
                        .filter(item => item.length > 0);
                }
            } else {
                // Handle numbers or other types
                featureList = [String(features)];
            }
            
            // Format the output
            return featureList.length > 0 ? 
                featureList.join(', ') : 
                'No features specified';
                
        } catch (e) {
            console.error('Feature display error:', e);
            return 'Could not display features';
        }
    }

    // Improved error display with more context
    function showError(element, message, responseData = null) {
        let errorHtml = `
            <div class="error-card">
                <p class="error-message">${message}</p>
                <div class="error-tips">
                    <p>Tips for better results:</p>
                    <ul>
                        <li>Use clear, well-lit product photos</li>
                        <li>Ensure product packaging is visible</li>
                        <li>Try different angles if needed</li>
                    </ul>
                </div>
        `;
        
        // Include raw response data if available (truncated for security)
        if (responseData && responseData.raw_response) {
            errorHtml += `
                <div class="debug-info">
                    <p>Technical details:</p>
                    <code>${responseData.raw_response.substring(0, 150)}...</code>
                </div>
            `;
        }
        
        errorHtml += `</div>`;
        element.innerHTML = errorHtml;
    }

    // Image Upload Handler with comprehensive error handling
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const statusElement = document.getElementById('uploadStatus');
            const detailsElement = document.getElementById('productDetails');
            
            // Reset UI state
            statusElement.textContent = 'Analyzing image...';
            statusElement.style.color = 'blue';
            detailsElement.innerHTML = '<div class="loading-spinner"></div>';
            
            // Validate file input
            const fileInput = document.getElementById('imageInput');
            if (!fileInput.files || fileInput.files.length === 0) {
                statusElement.textContent = 'Please select an image file';
                statusElement.style.color = 'red';
                detailsElement.innerHTML = '';
                return;
            }

            try {
                // Prepare form data
                const formData = new FormData();
                formData.append('image', fileInput.files[0]);

                // Show upload progress
                const progressElement = document.createElement('div');
                progressElement.className = 'upload-progress';
                detailsElement.appendChild(progressElement);
                
                // Make the request
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                // Remove progress indicator
                detailsElement.removeChild(progressElement);
                
                // Handle HTTP errors
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({
                        error: `Server error: ${response.status}`
                    }));
                    throw new Error(errorData.error || 'Upload failed');
                }

                // Process response
                const data = await response.json();
                
                // Validate response structure
                if (!data || (!data.product && !data.raw_text)) {
                    throw new Error('Invalid response format from server');
                }

                // Handle both JSON and text responses
                if (data.raw_text) {
                    // Display raw text description
                    detailsElement.innerHTML = `
                        <div class="product-card">
                            <h3>Basic Product Information</h3>
                            <div class="product-description">
                                <p>${data.raw_text}</p>
                                <p class="notice">Note: Full specifications not available</p>
                            </div>
                        </div>
                    `;
                } else {
                    // Display structured product data
                    detailsElement.innerHTML = `
                        <div class="product-card">
                            <h3>${data.product.product_name || 'Unknown Product'}</h3>
                            <div class="product-detail">
                                <span class="detail-label">Brand:</span>
                                <span>${data.product.brand || 'N/A'}</span>
                            </div>
                            ${data.product.price && data.product.price !== "Not available" ? `
                            <div class="product-detail">
                                <span class="detail-label">Price:</span>
                                <span>${data.product.price}</span>
                            </div>
                            ` : ''}
                            <div class="product-detail">
                                <span class="detail-label">Features:</span>
                                <span>${displayFeatures(data.product.features)}</span>
                            </div>
                            ${data.product.dimensions ? `
                            <div class="product-detail">
                                <span class="detail-label">Dimensions:</span>
                                <span>${data.product.dimensions}</span>
                            </div>
                            ` : ''}
                        </div>
                    `;
                }

                statusElement.textContent = 'Analysis complete!';
                statusElement.style.color = 'green';

            } catch (error) {
                console.error('Upload error:', error);
                statusElement.textContent = 'Error processing image';
                statusElement.style.color = 'red';
                
                // Show appropriate error message
                showError(
                    detailsElement,
                    error.message || 'An unexpected error occurred',
                    error.response ? error.response.data : null
                );
            }
        });
    }

    // Get Product by ID Handler with improved caching
    const getProductForm = document.getElementById('getProductForm');
    if (getProductForm) {
        getProductForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const statusElement = document.getElementById('productDetailsById');
            const productId = document.getElementById('productId').value.trim();
            
            // Validate input
            if (!productId) {
                statusElement.innerHTML = '<p class="error-message">Please enter a product ID</p>';
                return;
            }

            // Show loading state
            statusElement.innerHTML = '<div class="loading-spinner"></div>';
            
            try {
                // Make the request with cache control
                const response = await fetch(`/product/${productId}`, {
                    headers: {
                        'Cache-Control': 'no-cache'
                    }
                });
                
                // Handle errors
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({
                        error: `Server error: ${response.status}`
                    }));
                    throw new Error(errorData.error || 'Product not found');
                }

                // Process response
                const data = await response.json();
                
                if (!data) {
                    throw new Error('Invalid product data received');
                }

                // Display product
                statusElement.innerHTML = `
                    <div class="product-card">
                        <h3>${data.product_name || 'Unknown Product'}</h3>
                        <div class="product-detail">
                            <span class="detail-label">ID:</span>
                            <span>${data.id}</span>
                        </div>
                        <div class="product-detail">
                            <span class="detail-label">Brand:</span>
                            <span>${data.brand || 'N/A'}</span>
                        </div>
                        <div class="product-detail">
                            <span class="detail-label">Price:</span>
                            <span>${data.price || 'N/A'}</span>
                        </div>
                        <div class="product-detail">
                            <span class="detail-label">Features:</span>
                            <span>${displayFeatures(data.features)}</span>
                        </div>
                        ${data.dimensions ? `
                        <div class="product-detail">
                            <span class="detail-label">Dimensions:</span>
                            <span>${data.dimensions}</span>
                        </div>
                        ` : ''}
                        <div class="product-meta">
                            <small>Last updated: ${new Date().toLocaleString()}</small>
                        </div>
                    </div>
                `;
            } catch (error) {
                console.error('Fetch error:', error);
                showError(
                    statusElement,
                    error.message || 'Failed to fetch product details'
                );
            }
        });
    }

    // Update Product Handler with validation
    const updateProductForm = document.getElementById('updateProductForm');
    if (updateProductForm) {
        updateProductForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const statusElement = document.getElementById('updateStatus');
            const productId = document.getElementById('productIdToUpdate').value.trim();
            
            // Validate input
            if (!productId) {
                statusElement.textContent = 'Please enter a product ID';
                statusElement.style.color = 'red';
                return;
            }

            // Prepare data
            const productData = {
                product_name: document.getElementById('newProductName').value.trim(),
                price: document.getElementById('newPrice').value.trim(),
                features: document.getElementById('newFeatures').value
                    .split(',')
                    .map(item => item.trim())
                    .filter(item => item),
                brand: document.getElementById('newBrand')?.value.trim() || '',
                dimensions: document.getElementById('newDimensions')?.value.trim() || ''
            };

            // Validate at least one field is being updated
            if (!productData.product_name && !productData.price && 
                productData.features.length === 0 && !productData.brand && 
                !productData.dimensions) {
                statusElement.textContent = 'Please provide at least one field to update';
                statusElement.style.color = 'red';
                return;
            }

            // Show loading state
            statusElement.textContent = 'Updating product...';
            statusElement.style.color = 'blue';

            try {
                // Make the request
                const response = await fetch(`/product/${productId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(productData)
                });

                // Handle errors
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({
                        error: `Update failed: ${response.status}`
                    }));
                    throw new Error(errorData.error || 'Failed to update product');
                }

                // Show success
                statusElement.textContent = 'Product updated successfully!';
                statusElement.style.color = 'green';
                
                // Clear form
                document.getElementById('updateProductForm').reset();
                
            } catch (error) {
                console.error("Update failed:", error);
                statusElement.textContent = `Error: ${error.message}`;
                statusElement.style.color = 'red';
            }
        });
    }

    // Delete Product Handler with confirmation
    const deleteProductForm = document.getElementById('deleteProductForm');
    if (deleteProductForm) {
        deleteProductForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const statusElement = document.getElementById('deleteStatus');
            const productId = document.getElementById('productIdToDelete').value.trim();
            
            // Validate input
            if (!productId) {
                statusElement.textContent = 'Please enter a product ID';
                statusElement.style.color = 'red';
                return;
            }

            // Confirm deletion
            if (!confirm(`Are you sure you want to delete product #${productId}?`)) {
                return;
            }

            // Show loading state
            statusElement.textContent = 'Deleting product...';
            statusElement.style.color = 'blue';

            try {
                // Make the request
                const response = await fetch(`/product/${productId}`, {
                    method: 'DELETE'
                });

                // Handle errors
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({
                        error: `Delete failed: ${response.status}`
                    }));
                    throw new Error(errorData.error || 'Failed to delete product');
                }

                // Show success
                statusElement.textContent = 'Product deleted successfully!';
                statusElement.style.color = 'green';
                
                // Clear form
                document.getElementById('deleteProductForm').reset();
                
            } catch (error) {
                console.error("Delete failed:", error);
                statusElement.textContent = `Error: ${error.message}`;
                statusElement.style.color = 'red';
            }
        });
    }
});