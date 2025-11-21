# How to Verify Download Buttons Are Visible

## Quick Check in Browser Console

1. **Open your browser** at http://localhost:3000
2. **Open DevTools** (F12)
3. **Click on a dashboard card** (e.g., "UPI Tracker")
4. **Go to Console tab** - You should see:
   ```
   JSONViewer rendering with dashboardId: 282 jsonData: true
   CSVViewer rendering with dashboardId: 282 csvData: true
   ```

5. **Go to Elements/Inspector tab**
6. **Search for "Download"** (Ctrl+F or Cmd+F)
7. **You should find**:
   - `<button>📥 Download JSON</button>`
   - `<button>📥 Download CSV</button>`

## Visual Check

After clicking a dashboard, you should see:

### JSON Data Section:
```
┌─────────────────────────────────────────────┐
│ JSON Data    [📥 Download JSON] [Expand]    │  ← Buttons here
├─────────────────────────────────────────────┤
│ { "dashboard_id": 282, ... }               │
└─────────────────────────────────────────────┘
```

### CSV Data Section:
```
┌─────────────────────────────────────────────┐
│ CSV Data     [📥 Download CSV]              │  ← Button here
├─────────────────────────────────────────────┤
│ Total Rows: 16    Columns: 10               │
│ [Table data...]                             │
└─────────────────────────────────────────────┘
```

## If Buttons Are in DOM But Not Visible

1. **Check computed styles** in DevTools:
   - Right-click button → Inspect
   - Check if `display: none` or `visibility: hidden`
   - Check if `opacity: 0`

2. **Check z-index** - buttons might be behind other elements

3. **Check parent container** - Header might have `overflow: hidden`

## Manual Test

In browser console, run:
```javascript
// Find download buttons
document.querySelectorAll('button').forEach(btn => {
  if (btn.textContent.includes('Download')) {
    console.log('Found button:', btn.textContent, btn);
    btn.style.border = '3px solid red'; // Make it visible
  }
});
```

This will highlight any download buttons with a red border.

