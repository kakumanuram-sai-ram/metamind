# Fresh Extract vs Using Existing Metadata - Implementation Fix

**Date:** November 26, 2025  
**Status:** ✅ Complete - Ready for Testing

---

## Problem Summary

When selecting "Fresh Extract" for a dashboard with existing metadata:
1. ❌ Old files remained on disk, causing UI to show 100% progress immediately
2. ❌ Current phase wasn't populated correctly
3. ❌ Progress bars showed misleading state
4. ❌ Metadata components didn't distinguish between "Using Existing" vs "Fresh Extract"

---

## Expected Behavior

### **Scenario 1: Use Existing Metadata** (e.g., Dashboard 476)

**UI Behavior:**
- ✅ All metadata components show **100% progress** immediately
- ✅ Status: **"Using Existing"** or **"Available"**
- ✅ Files are **downloadable immediately**
- ✅ Clicking on component shows dataframe/content
- ✅ No processing phases shown (data is already there)

**Backend Behavior:**
- ✅ Extraction is **skipped** for this dashboard
- ✅ Existing files are **used as-is**
- ✅ Marked in `metadata_choices` as `use_existing=True`

---

### **Scenario 2: Start Fresh** (e.g., Fresh extraction even with existing data)

**UI Behavior:**
- ✅ Progress starts at **0%** (not 100%)
- ✅ Goes through **all phases sequentially**:
  1. Dashboard Extraction (Phase 1)
  2. Tables & Columns (Phase 2)
  3. Schema Enrichment (Phase 3)
  4. Table Metadata (Phase 4)
  5. Column Metadata (Phase 5)
  6. Joining Conditions (Phase 6)
  7. Filter Conditions (Phase 7)
  8. Term Definitions (Phase 8)
- ✅ Current phase displays: "Current Phase: Table Metadata" etc.
- ✅ Each component shows its actual status:
  - **"Waiting..."** - Pending (0% progress)
  - **"Processing..."** - Currently working (50% progress)
  - **"Completed"** - File generated (100% progress)
- ✅ Old files are **NOT shown** before processing starts

**Backend Behavior:**
- ✅ **Deletes old dashboard folder** before extraction starts
- ✅ Creates **all files from scratch**
- ✅ Goes through **all 8 phases** sequentially
- ✅ Marked in `metadata_choices` as `use_existing=False`

---

### **Scenario 3: Multiple Dashboards + Knowledge Base**

**Knowledge Base Download Availability:**
- ✅ Knowledge Base ZIP is **only available** when:
  1. **ALL dashboards** are completed (both fresh + existing)
  2. **Merge phase** is completed
  3. **KB Build phase** is completed
  4. **All 5 required files** exist for each dashboard:
     - table_metadata.csv
     - columns_metadata.csv
     - definitions.csv
     - joining_conditions.csv
     - filter_conditions.txt

**Example:**
- Dashboard 476: Use Existing ✅
- Dashboard 511: Fresh Extract (processing...)  ⏳
- **Result:** KB Download shows "Waiting for extraction to complete" until 511 is done

---

## Implementation Changes

### **1. Backend Fix: Delete Old Files (`api_server.py`)**

**File:** `scripts/api_server.py`  
**Location:** Lines 588-606 (in `run_processing()` function)

**What it does:**
- When `extract=True` and `use_existing=False` for a dashboard
- **Deletes the entire dashboard folder** before extraction starts
- Prevents UI from detecting old files

```python
# Delete old files for dashboards with fresh extract (use_existing=False)
if request.extract:
    for dashboard_id in request.dashboard_ids:
        use_existing = choices_dict.get(dashboard_id, False)
        if not use_existing:
            # Fresh extract - delete old files to prevent UI confusion
            dashboard_dir = os.path.join(metamind_dir, "extracted_meta", str(dashboard_id))
            if os.path.exists(dashboard_dir):
                try:
                    import shutil
                    shutil.rmtree(dashboard_dir)
                    print(f"🗑️  Deleted old files for dashboard {dashboard_id} (fresh extract)", flush=True)
                except Exception as e:
                    print(f"⚠️  Warning: Could not delete old files for dashboard {dashboard_id}: {e}", flush=True)
```

---

### **2. Frontend Fix: Conditional File Checking (`DashboardSection.js`)**

**File:** `frontend/src/components/DashboardSection.js`  
**Component:** `MetadataCardContent`

**What it does:**
- **Using Existing:** Immediately checks for files and shows as available
- **Fresh Extract (Pending):** Does NOT check for files (shows 0% progress)
- **Fresh Extract (Processing):** Starts polling for files as they're created

```javascript
// If using existing metadata, immediately check for files and show as available
if (useExisting) {
  const checkFileExists = async () => {
    // Check and set fileAvailable
  };
  checkFileExists();
  return;
}

// If doing fresh extract and still pending, don't check for old files
if (!useExisting && status === 'pending') {
  setFileAvailable(false);  // Don't show old files
  setCheckingFile(false);
  return;
}

// For fresh extract that's processing, check and poll
if (status === 'processing' || status === 'completed') {
  checkFileExists();
  // Poll every 3 seconds
}
```

---

### **3. Frontend Fix: Status Display (`DashboardSection.js`)**

**File:** `frontend/src/components/DashboardSection.js`  
**Function:** `getDisplayStatus()`

**What it does:**
- Shows **"Using Existing"** for existing metadata
- Shows actual phase status for fresh extracts

```javascript
const getDisplayStatus = () => {
  // If using existing metadata, show as "Using Existing"
  if (useExisting) {
    return fileAvailable ? 'Using Existing' : 'Available';
  }
  
  // For fresh extracts
  if (checkingFile) return 'Checking...';
  if (fileAvailable) return 'Completed';
  if (status === 'processing') return currentStep || 'Processing...';
  if (status === 'pending') return 'Waiting...';
  if (status === 'error') return 'Error';
  return 'Pending';
};
```

---

### **4. Frontend Fix: Progress Bar (`DashboardSection.js`)**

**File:** `frontend/src/components/DashboardSection.js`  
**Component:** `MetadataCardContent`

**What it does:**
- **Using Existing:** 100% if file exists, 0% otherwise
- **Fresh Extract:** 0% → 50% (processing) → 100% (completed)

```javascript
let isCompleted, progressPercent;

if (useExisting) {
  // Using existing metadata - always show as completed if file exists
  isCompleted = fileAvailable;
  progressPercent = fileAvailable ? 100 : 0;
} else {
  // Fresh extract - show actual progress based on file availability
  isCompleted = fileAvailable;
  progressPercent = isCompleted ? 100 : (status === 'processing' ? 50 : 0);
}
```

---

### **5. Knowledge Base Download Logic (Already Correct)**

**File:** `frontend/src/components/KnowledgeBaseDownload.js`  
**Function:** `getStatus()`

**What it does:**
- Checks that **ALL dashboards** are completed
- Verifies **all 5 required files** exist for each dashboard
- Only shows "Ready for download" when everything is complete

```javascript
// Only mark as completed when all 5 files are ready AND KB is built AND ALL dashboards match
if (kbStatus === 'completed' && zipAvailable && allFilesReady && allDashboardsMatch) {
  // Double-check that all dashboards are actually completed
  const allDashboardsCompleted = dashboardIds.every(id => {
    const dashProgress = progress.dashboards?.[id.toString()];
    return dashProgress?.status === 'completed';
  });
  
  if (allDashboardsCompleted) {
    return { status: 'completed', step: 'Ready for download', progress: 100 };
  }
}
```

---

## Testing Checklist

### **Test Case 1: Use Existing Metadata Only**

1. ✅ Select Dashboard 476
2. ✅ In modal, choose **"Use Existing Metadata"**
3. ✅ Click **"Proceed with Extraction"**

**Expected Result:**
- All metadata components show **100% progress** immediately
- Status shows **"Using Existing"**
- Files are **downloadable immediately**
- Clicking shows dataframe/content
- No "Current Phase" displayed
- KB Download available immediately (if only this dashboard)

---

### **Test Case 2: Fresh Extract Only**

1. ✅ Select Dashboard 476 (with existing data)
2. ✅ In modal, choose **"Start Fresh"**
3. ✅ Click **"Proceed with Extraction"**

**Expected Result:**
- All metadata components start at **0% progress**
- Status shows **"Waiting..."**
- Current Phase displays: **"Phase 1: Dashboard Extraction"** → **"Phase 2: Tables & Columns"** → etc.
- Progress bars update as each file is generated:
  - 0% → 50% (processing) → 100% (completed)
- Old files are **deleted** (not shown)
- KB Download available after ALL phases complete

---

### **Test Case 3: Mixed - One Existing + One Fresh**

1. ✅ Select Dashboard 476 AND Dashboard 511
2. ✅ In modal:
   - Dashboard 476: **"Use Existing Metadata"**
   - Dashboard 511: **"Start Fresh"**
3. ✅ Click **"Proceed with Extraction"**

**Expected Result:**
- **Dashboard 476:**
  - Immediately shows 100% for all components
  - Status: "Using Existing"
  - Files downloadable immediately
- **Dashboard 511:**
  - Starts at 0%, goes through all phases
  - Shows actual phase progress
  - Files appear as they're generated
- **KB Download:**
  - Shows "Waiting..." until Dashboard 511 completes
  - Only available when **BOTH** dashboards are complete

---

### **Test Case 4: Fresh Extract (Second Time)**

1. ✅ Extract Dashboard 476 fresh (generates files)
2. ✅ Extract Dashboard 476 fresh **again**

**Expected Result:**
- Old files are **deleted** before second extraction
- UI shows **0% progress** at start (not 100%)
- Goes through all phases again from scratch
- No confusion with old files

---

## Files Modified

1. ✅ `scripts/api_server.py` - Delete old files for fresh extracts
2. ✅ `frontend/src/components/DashboardSection.js` - Conditional file checking, status display, progress bars
3. ✅ `frontend/src/components/KnowledgeBaseDownload.js` - (Already correct, no changes needed)

---

## Verification Commands

### Check if old files are deleted:
```bash
# Before fresh extract - files exist
ls -la extracted_meta/476/

# Start fresh extract
# (Click "Start Fresh" in UI)

# During/after fresh extract - old files should be gone, new files created
ls -la extracted_meta/476/
```

### Monitor backend logs:
```bash
# You should see this log when fresh extract starts:
# 🗑️  Deleted old files for dashboard 476 (fresh extract)
```

### Check frontend console:
```javascript
// For fresh extract (pending), you should see:
// fileAvailable: false, status: 'pending', progress: 0%

// For using existing, you should see:
// fileAvailable: true, status: 'Using Existing', progress: 100%
```

---

## Summary

| Scenario | Progress at Start | Status Display | Files | Backend Action |
|----------|------------------|----------------|-------|----------------|
| **Use Existing** | 100% | "Using Existing" | Show immediately | Skip extraction |
| **Fresh Extract** | 0% | "Waiting..." → "Processing..." → "Completed" | Created from scratch | Delete old → Extract all phases |
| **KB Download** | - | "Waiting..." until ALL dashboards complete | - | Check all dashboards completed |

---

**Status:** ✅ Implementation Complete  
**Next Step:** Kill backend/frontend, restart, and test all scenarios


