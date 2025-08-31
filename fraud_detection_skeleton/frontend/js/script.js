document.addEventListener('DOMContentLoaded', function() {
    // Check if Papa Parse is loaded
    if (typeof Papa === 'undefined') {
        console.error('Papa Parse library is not loaded. Please check your internet connection or include the library manually.');
        alert('Error: Required CSV parsing library is not available. Please check your internet connection and reload the page.');
        return;
    }
    // API endpoint configuration
    const API_URL = 'http://localhost:5000/api';
    
    // Check if API server is running
    fetch(`${API_URL}/health`)
        .then(response => {
            if (!response.ok) throw new Error('API server is not responding');
            return response.json();
        })
        .then(data => {
            if (!data.model_loaded) {
                console.error('Model not loaded in the backend');
                alert('Warning: The fraud detection model is not loaded in the backend. Please ensure the model is properly trained and available.');
            }
        })
        .catch(error => {
            console.error('API connection error:', error);
            alert('Error: Cannot connect to the API server. Please ensure the Flask backend is running on port 5000.');
        });
    
    // Tab switching functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            
            // Update active tab button
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Show selected tab content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${tabId}-tab`) {
                    content.classList.add('active');
                }
            });
        });
    });
    
    // Hour range slider value display
    const hourSlider = document.getElementById('hour');
    const hourValue = document.getElementById('hour-value');
    
    hourSlider.addEventListener('input', () => {
        hourValue.textContent = hourSlider.value;
    });
    
    // Single transaction form submission
    const transactionForm = document.getElementById('transaction-form');
    const resultCard = document.getElementById('result-card');
    const fraudIndicator = document.getElementById('fraud-indicator');
    const fraudProbability = document.getElementById('fraud-probability');
    const fraudPrediction = document.getElementById('fraud-prediction');
    
    transactionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Validate form inputs
        const amount = parseFloat(document.getElementById('amount').value);
        const distance = parseFloat(document.getElementById('distance').value);
        
        // Validation checks
        if (isNaN(amount) || amount < 0) {
            alert('Please enter a valid positive amount');
            return;
        }
        
        if (isNaN(distance) || distance < 0) {
            alert('Please enter a valid positive distance');
            return;
        }
        
        // Show loading state
        const submitBtn = transactionForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.textContent;
        submitBtn.textContent = 'Processing...';
        submitBtn.disabled = true;
        
        try {
            // Collect form data
            const formData = {
                user_id: 1234, // Default user ID
                amount: parseFloat(document.getElementById('amount').value),
                hour: parseInt(document.getElementById('hour').value),
                day_of_week: parseInt(document.getElementById('day-of-week').value),
                merchant_category: document.getElementById('merchant-category').value,
                device_type: document.getElementById('device-type').value,
                distance_from_home_km: parseFloat(document.getElementById('distance').value),
                is_foreign: parseInt(document.getElementById('is-foreign').value),
                is_high_risk_merchant: parseInt(document.getElementById('is-high-risk').value),
                has_history_of_chargeback: parseInt(document.getElementById('has-history').value)
            };
            
            // Send API request
            const response = await fetch(`${API_URL}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                throw new Error('API request failed');
            }
            
            const data = await response.json();
            
            // Display results
            const probability = data.fraud_probability;
            const isFraud = data.is_fraud;
            
            // Update UI with results
            fraudProbability.textContent = `${(probability * 100).toFixed(2)}%`;
            
            if (isFraud) {
                fraudIndicator.className = 'indicator fraud';
                fraudIndicator.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
                fraudPrediction.textContent = '🚨 FRAUD';
                fraudPrediction.className = 'value fraud';
            } else {
                fraudIndicator.className = 'indicator legitimate';
                fraudIndicator.innerHTML = '<i class="fas fa-check"></i>';
                fraudPrediction.textContent = '✅ Legitimate';
                fraudPrediction.className = 'value legitimate';
            }
            
            // Show result card
            resultCard.style.display = 'block';
            
            // Scroll to results
            resultCard.scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while processing your request. Please try again.');
        } finally {
            // Reset button state
            submitBtn.textContent = originalBtnText;
            submitBtn.disabled = false;
        }
    });
    
    // Batch processing functionality
    const batchForm = document.getElementById('batch-form');
    const csvFileInput = document.getElementById('csv-file');
    const fileNameDisplay = document.getElementById('file-name');
    const batchResultCard = document.getElementById('batch-result-card');
    const resultsTable = document.getElementById('results-table');
    const resultsBody = document.getElementById('results-body');
    const downloadBtn = document.getElementById('download-results');
    
    // Update file name display when file is selected
    csvFileInput.addEventListener('change', () => {
        if (csvFileInput.files.length > 0) {
            fileNameDisplay.textContent = csvFileInput.files[0].name;
        } else {
            fileNameDisplay.textContent = 'No file chosen';
        }
    });
    
    // Process batch CSV file
    batchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!csvFileInput.files.length) {
            alert('Please select a CSV file');
            return;
        }
        
        // Show loading state
        const submitBtn = batchForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.textContent;
        submitBtn.textContent = 'Processing...';
        submitBtn.disabled = true;
        
        try {
            const file = csvFileInput.files[0];
            
            // Parse CSV file
            Papa.parse(file, {
                header: true,
                dynamicTyping: true,
                complete: async function(results) {
                    try {
                        // Check for required columns
                        const requiredColumns = ['amount', 'merchant_category', 'device_type', 'distance_from_home_km', 'is_foreign', 'is_high_risk_merchant', 'has_history_of_chargeback'];
                        const missingColumns = requiredColumns.filter(col => !results.meta.fields.includes(col));
                        
                        if (missingColumns.length) {
                            throw new Error(`Missing required columns: ${missingColumns.join(', ')}. Please ensure your CSV file contains all required columns.`);
                        }
                        
                        // Validate data types
                        const numericColumns = ['amount', 'distance_from_home_km'];
                        const binaryColumns = ['is_foreign', 'is_high_risk_merchant', 'has_history_of_chargeback'];
                        
                        // Check for empty rows
                        const validData = results.data.filter(row => {
                            // Skip empty rows
                            if (Object.values(row).every(val => val === null || val === undefined || val === '')) {
                                return false;
                            }
                            return true;
                        });
                        
                        if (validData.length === 0) {
                            throw new Error('No valid data rows found in the CSV file.');
                        }
                        
                        // Send data to API
                        const response = await fetch(`${API_URL}/batch-predict`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(validData)
                        });
                        
                        if (!response.ok) {
                            throw new Error('API request failed');
                        }
                        
                        const data = await response.json();
                        
                        // Clear previous results
                        resultsBody.innerHTML = '';
                        
                        // Display results in table
                        data.forEach(item => {
                            const row = document.createElement('tr');
                            
                            // Create table cells
                            const userIdCell = document.createElement('td');
                            userIdCell.textContent = item.user_id || 'Auto-generated';
                            
                            const amountCell = document.createElement('td');
                            amountCell.textContent = item.amount ? `₹${item.amount.toFixed(2)}` : 'N/A';
                            
                            const merchantCell = document.createElement('td');
                            merchantCell.textContent = item.merchant_category || 'N/A';
                            
                            const probCell = document.createElement('td');
                            probCell.textContent = `${(item.fraud_probability * 100).toFixed(2)}%`;
                            
                            const predictionCell = document.createElement('td');
                            if (item.is_fraud) {
                                predictionCell.textContent = '🚨 FRAUD';
                                predictionCell.className = 'fraud';
                            } else {
                                predictionCell.textContent = '✅ Legitimate';
                                predictionCell.className = 'legitimate';
                            }
                            
                            // Add cells to row
                            row.appendChild(userIdCell);
                            row.appendChild(amountCell);
                            row.appendChild(merchantCell);
                            row.appendChild(probCell);
                            row.appendChild(predictionCell);
                            
                            // Add row to table
                            resultsBody.appendChild(row);
                        });
                        
                        // Store processed data for download
                        window.processedData = data;
                        
                        // Show results
                        batchResultCard.style.display = 'block';
                        batchResultCard.scrollIntoView({ behavior: 'smooth' });
                        
                    } catch (error) {
                        console.error('Error:', error);
                        alert(`Error: ${error.message}`);
                    } finally {
                        // Reset button state
                        submitBtn.textContent = originalBtnText;
                        submitBtn.disabled = false;
                    }
                },
                error: function(error) {
                    console.error('CSV Parse Error:', error);
                    alert('Error parsing CSV file. Please check the format.');
                    submitBtn.textContent = originalBtnText;
                    submitBtn.disabled = false;
                }
            });
            
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while processing your request. Please try again.');
            submitBtn.textContent = originalBtnText;
            submitBtn.disabled = false;
        }
    });
    
    // Download results as CSV
    downloadBtn.addEventListener('click', () => {
        if (!window.processedData || !window.processedData.length) {
            alert('No data to download');
            return;
        }
        
        // Convert data to CSV
        const csv = Papa.unparse(window.processedData);
        
        // Create download link
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.setAttribute('href', url);
        link.setAttribute('download', 'fraud_detection_results.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
});