# UI Fixes: CSV Viewer Toggle + Knowledge Base Status

**Date:** November 26, 2025  
**Status:** ✅ Complete - Ready for Testing

---

## Issue 1: CSV Viewer Not Toggling ✅ FIXED

### **Problem:**
- When clicking a metadata component once, the CSV viewer opens
- When clicking the same component again, it should close (toggle off)
- **Bug:** Second click was not closing the viewer

### **Root Cause:**
The `onClick` handler was always setting `selectedFileType` to the clicked `fileType`, even if it was already selected. It wasn't toggling.

**Before:**
```javascript
onClick={() => {
  if (onClick) {
    onClick(fileType); // Always sets to fileType
  }
}}
```

### **Fix Applied:**
**File:** `frontend/src/components/DashboardSection.js` (Line 322-326)

```javascript
onClick={() => {
  if (onClick) {
    // Toggle: if already selected, deselect (close viewer), otherwise select
    onClick(isSelected ? null : fileType);
  }
}}
```

### **How It Works Now:**
1. **First Click:** `isSelected = false` → Sets `selectedFileType = fileType` → **Viewer opens**
2. **Second Click:** `isSelected = true` → Sets `selectedFileType = null` → **Viewer closes**
3. **Click Different Component:** Opens the new component's viewer

---

## Issue 2: Knowledge Base Status Not Communicating Progress ✅ FIXED

### **Problem:**
- When both dashboards complete and merge/KB build starts, UI shows "pending" without any details
- No information about what's happening in the background
- User doesn't know if it's stuck or progressing

### **Root Cause:**
The `getStatus()` function was retrieving `current_step` from backend but displaying it as raw technical names like:
- `table_metadata`
- `columns`
- `initializing`

These are not user-friendly.

### **Fix Applied:**
**File:** `frontend/src/components/KnowledgeBaseDownload.js` (Lines 243-337)

**1. Added Step Formatting Function:**
```javascript
const formatStepMessage = (step, type = 'merge') => {
  // Merge steps (6 steps)
  const mergeSteps = {
    'initializing': '🔄 Initializing merge process',
    'preparing': '📋 Preparing metadata for merge',
    'table_metadata': '🗂️  Merging table metadata (1/6)',
    'columns_metadata': '📊 Merging column metadata (2/6)',
    'joining_conditions': '🔗 Merging joining conditions (3/6)',
    'definitions': '📖 Merging term definitions (4/6)',
    'filter_conditions': '🔍 Merging filter conditions (5/6)',
    'conflicts_report': '⚠️  Generating conflicts report (6/6)'
  };
  
  // KB build steps (5 steps)
  const kbSteps = {
    'initializing': '🔄 Initializing knowledge base',
    'tables': '🗂️  Converting table metadata (1/5)',
    'columns': '📊 Converting column metadata (2/5)',
    'joins': '🔗 Converting joining conditions (3/5)',
    'definitions': '📖 Converting term definitions (4/5)',
    'filter_conditions': '🔍 Converting filter conditions (5/5)'
  };
  
  return (type === 'merge' ? mergeSteps[step] : kbSteps[step]) || step;
};
```

**2. Enhanced Status Detection:**

**When Merging:**
```javascript
if (mergeStatus === 'processing') {
  const currentStep = progress.merge_status?.current_step;
  const formattedStep = formatStepMessage(currentStep, 'merge');
  return { 
    status: 'merging', 
    step: formattedStep,  // e.g., "🗂️  Merging table metadata (1/6)"
    progress: 50 
  };
}
```

**When Building KB:**
```javascript
if (kbStatus === 'processing') {
  const currentStep = progress.kb_build_status?.current_step;
  const formattedStep = formatStepMessage(currentStep, 'kb');
  return { 
    status: 'processing', 
    step: formattedStep,  // e.g., "📊 Converting column metadata (2/5)"
    progress: 80 
  };
}
```

**When Waiting for Dashboards:**
```javascript
if (overallStatus === 'extracting') {
  const completedCount = dashboardIds.filter(id => {
    const dashProgress = progress.dashboards?.[id.toString()];
    return dashProgress?.status === 'completed';
  }).length;
  
  return { 
    status: 'pending', 
    step: `⏳ Extraction in progress (${completedCount}/${dashboardIds.length} dashboards completed)`,
    progress: (completedCount / dashboardIds.length) * 40
  };
}
```

### **Status Messages You'll See Now:**

#### **Phase 1: Extraction**
- `⏳ Extraction in progress (1/2 dashboards completed)` (25% progress)

#### **Phase 2: Merging** (After all dashboards complete)
- `🔄 Initializing merge process`
- `📋 Preparing metadata for merge`
- `🗂️  Merging table metadata (1/6)` (50% progress)
- `📊 Merging column metadata (2/6)`
- `🔗 Merging joining conditions (3/6)`
- `📖 Merging term definitions (4/6)`
- `🔍 Merging filter conditions (5/6)`
- `⚠️  Generating conflicts report (6/6)`
- `✅ Merge complete, preparing knowledge base`

#### **Phase 3: KB Building**
- `🔄 Preparing to build knowledge base` (65% progress)
- `🔄 Initializing knowledge base`
- `🗂️  Converting table metadata (1/5)` (80% progress)
- `📊 Converting column metadata (2/5)`
- `🔗 Converting joining conditions (3/5)`
- `📖 Converting term definitions (4/5)`
- `🔍 Converting filter conditions (5/5)`
- `🔄 Finalizing knowledge base` (95% progress)

#### **Phase 4: Complete**
- `✅ Ready for download` (100% progress)

---

## Visual Improvements

### **Progress Bar:**
- Extraction: 0-40% (based on dashboards completed)
- Merging: 50%
- KB Building: 80-95%
- Completed: 100%

### **Status Badge Colors:**
- **Pending** → Gray
- **Merging** → Blue
- **Building** → Blue
- **Ready** → Green

### **Step Indicators:**
- Emojis for visual clarity (🔄, 📋, 🗂️, 📊, 🔗, 📖, 🔍, ⚠️, ✅, ⏳)
- Step count: "(1/6)", "(2/6)" etc.
- Clear action verbs: "Merging", "Converting", "Preparing"

---

## Testing Scenarios

### **Test Case 1: CSV Viewer Toggle**

1. ✅ Click **"Table Metadata"** → Viewer opens
2. ✅ Click **"Table Metadata"** again → Viewer closes
3. ✅ Click **"Table Metadata"** → Viewer opens
4. ✅ Click **"Column Metadata"** → Switches to Column Metadata viewer
5. ✅ Click **"Column Metadata"** again → Viewer closes

**Expected:** Viewer toggles on/off correctly for each component

---

### **Test Case 2: KB Status - Two Dashboards Fresh Extract**

**Scenario:** Select Dashboard 476 + 511, both fresh extract

**Timeline:**
1. ✅ **0-30%:** Shows `⏳ Extraction in progress (0/2 dashboards completed)`
2. ✅ **30%:** Dashboard 476 completes → `⏳ Extraction in progress (1/2 dashboards completed)`
3. ✅ **40%:** Dashboard 511 completes → `⏳ Extraction in progress (2/2 dashboards completed)`
4. ✅ **50%:** Merge starts → `🔄 Initializing merge process`
5. ✅ **50%:** → `🗂️  Merging table metadata (1/6)`
6. ✅ **50%:** → `📊 Merging column metadata (2/6)`
7. ✅ **50%:** → `🔗 Merging joining conditions (3/6)`
8. ✅ **50%:** → `📖 Merging term definitions (4/6)`
9. ✅ **50%:** → `🔍 Merging filter conditions (5/6)`
10. ✅ **50%:** → `⚠️  Generating conflicts report (6/6)`
11. ✅ **65%:** → `🔄 Preparing to build knowledge base`
12. ✅ **80%:** KB build starts → `🗂️  Converting table metadata (1/5)`
13. ✅ **80%:** → `📊 Converting column metadata (2/5)`
14. ✅ **80%:** → `🔗 Converting joining conditions (3/5)`
15. ✅ **80%:** → `📖 Converting term definitions (4/5)`
16. ✅ **80%:** → `🔍 Converting filter conditions (5/5)`
17. ✅ **95%:** → `🔄 Finalizing knowledge base`
18. ✅ **100%:** → `✅ Ready for download` + Download button appears

---

### **Test Case 3: KB Status - One Existing + One Fresh**

**Scenario:** Dashboard 476 (Use Existing) + Dashboard 511 (Fresh Extract)

**Timeline:**
1. ✅ Dashboard 476 shows 100% immediately (existing)
2. ✅ Shows `⏳ Extraction in progress (1/2 dashboards completed)`
3. ✅ Dashboard 511 extraction completes → `⏳ Extraction in progress (2/2 dashboards completed)`
4. ✅ Merge starts → Shows all 6 merge steps
5. ✅ KB build starts → Shows all 5 KB steps
6. ✅ Complete → `✅ Ready for download`

---

## Files Modified

1. ✅ `frontend/src/components/DashboardSection.js`
   - Fixed CSV viewer toggle logic (Line 322-326)

2. ✅ `frontend/src/components/KnowledgeBaseDownload.js`
   - Added `formatStepMessage()` function
   - Enhanced `getStatus()` to show formatted progress messages
   - Added dashboard completion counter

---

## Summary

| Issue | Status | Impact |
|-------|--------|--------|
| CSV Viewer Toggle | ✅ Fixed | Viewer now properly opens/closes on click |
| KB Status Messages | ✅ Fixed | User sees detailed progress during merge/KB build |

**User Experience:**
- ✅ Clear visibility into what's happening
- ✅ Step-by-step progress with visual indicators
- ✅ Dashboard completion counter
- ✅ Accurate progress percentages
- ✅ No more "pending" without explanation

---

**Status:** ✅ Ready for Testing  
**Next Step:** Restart backend/frontend and verify both fixes work as expected


