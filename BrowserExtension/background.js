// Background service worker for TruthGuard Extension
// Allows analyzing text directly from the right-click context menu

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "analyze-truthguard",
    title: "Verify with TruthGuard AI",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "analyze-truthguard") {
    // We cannot easily show a popup from the background worker without complex messaging,
    // so we inject an alert directly into the page for the context menu option.
    const selectedText = info.selectionText;
    
    if(selectedText.length < 10) {
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => alert("TruthGuard AI: Please select a longer piece of text.")
        });
        return;
    }

    fetch('http://127.0.0.1:5000/api/v1/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        api_key: 'extension_key_123',
        text: selectedText
      })
    })
    .then(r => r.json())
    .then(data => {
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: (data) => {
                alert(`TruthGuard AI Analysis:\n\nResult: ${data.prediction} (${data.confidence.toFixed(1)}% confidence)\n\nReason: ${data.reason}`);
            },
            args: [data]
        });
    })
    .catch(err => {
        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => alert("TruthGuard AI: Failed to connect to verification servers.")
        });
    });
  }
});
