document.getElementById('analyzeBtn').addEventListener('click', async () => {
  const btn = document.getElementById('analyzeBtn');
  const resultDiv = document.getElementById('result');
  
  btn.disabled = true;
  btn.textContent = 'Analyzing...';
  resultDiv.style.display = 'none';

  try {
    // 1. Get selected text from active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    const injectionResults = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: () => window.getSelection().toString()
    });
    
    const selectedText = injectionResults[0].result;
    
    if (!selectedText || selectedText.length < 10) {
      throw new Error("Please select at least a sentence of text on the page first.");
    }

    // 2. Send to our API Endpoint
    // Note: In production, URL would be https://api.truthguard.ai/v1/analyze
    const response = await fetch('http://127.0.0.1:5000/api/v1/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        api_key: 'extension_key_123',
        text: selectedText
      })
    });
    
    if (!response.ok) throw new Error("Analysis failed. Server might be down.");
    
    const data = await response.json();
    
    // 3. Display Results
    document.getElementById('prediction').textContent = data.prediction;
    
    if(data.prediction.toLowerCase().includes('fake')) {
        document.getElementById('prediction').className = 'status-fake';
    } else if (data.prediction.toLowerCase().includes('real')) {
        document.getElementById('prediction').className = 'status-real';
    } else {
        document.getElementById('prediction').className = 'status-unknown';
    }
    
    document.getElementById('confidence').textContent = `Confidence: ${data.confidence.toFixed(1)}%`;
    document.getElementById('reason').textContent = data.reason;
    
    resultDiv.style.display = 'block';
    
  } catch (error) {
    resultDiv.style.display = 'block';
    resultDiv.innerHTML = `<div style="color: #ef4444;">${error.message}</div>`;
  } finally {
    btn.disabled = false;
    btn.textContent = 'Analyze Selected Text';
  }
});
