# Download Buttons Guide

## Where to Find Download Buttons

The download buttons appear **after you click on a dashboard card** in the "Available Dashboards" section.

### Steps to See Download Buttons:

1. **Open the app**: http://localhost:3000
2. **Click on any dashboard card** (e.g., "UPI Tracker" or "UPI SuperCash Burn Report")
3. **Scroll down** - You'll see two sections:
   - **JSON Data** section - Has "📥 Download JSON" button (orange)
   - **CSV Data** section - Has "📥 Download CSV" button (cyan)

### Button Locations:

```
┌─────────────────────────────────────────┐
│ JSON Data          [📥 Download JSON] [Expand] │
├─────────────────────────────────────────┤
│ { JSON content here... }                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ CSV Data           [📥 Download CSV]    │
├─────────────────────────────────────────┤
│ Total Rows: 16    Columns: 10          │
│ [Table with data...]                    │
└─────────────────────────────────────────┘
```

### If You Don't See Buttons:

1. **Hard refresh your browser**:
   - Windows/Linux: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

2. **Check browser console** (F12) for errors

3. **Make sure you clicked on a dashboard** - The buttons only appear when viewing dashboard details

4. **Clear browser cache** if hard refresh doesn't work

### Button Colors:

- **Download JSON**: Orange button (`#FF6F00`) - Paytm secondary color
- **Download CSV**: Cyan button (`#00BAF2`) - Paytm accent color

### What Gets Downloaded:

- **JSON**: `dashboard_{id}_info.json` - Complete dashboard metadata
- **CSV**: `dashboard_{id}_metadata.csv` - Tabular data with SQL queries

