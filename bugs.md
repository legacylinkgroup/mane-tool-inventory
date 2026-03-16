# Bugs & Issues Tracker

**Purpose:** Track bugs, issues, and learnings during development to prevent recurring problems.

---

## Active Issues

_No active issues yet. Development starting Phase 1._

---

## Resolved Issues

_No resolved issues yet._

---

## Known Limitations

### Phase 1
- Supabase Storage requires manual bucket creation (not automated in SQL migration)
- RLS (Row-Level Security) must be manually disabled for single-user mode
- Vercel Python runtime has cold start delays (1-2s first request)

---

## Technical Debt

_Items to address in future phases:_

1. **Input validation:** Add more robust validation for URLs (currently accepts any string)
2. **Error messages:** Standardize error messages across all endpoints
3. **Rate limiting:** Not implemented in Phase 1 (add in Phase 5)
4. **Logging:** Using print statements initially, switch to proper logging module

---

## Lessons Learned

_Track architectural decisions and gotchas:_

### Database Design
- **Composite unique constraint:** Using `UNIQUE (name, box_id)` enforces merge strategy at database level (better than application-level checks)
- **Triggers for timestamps:** More reliable than manual updates in application code

### FastAPI
- _Lessons will be added as we encounter them_

### Supabase
- _Lessons will be added as we encounter them_

---

## Testing Notes

_Track flaky tests, edge cases, test data issues:_

_No tests written yet._

---

## Template for New Bug Entry

```markdown
## Bug: [Short Description]

**Date:** YYYY-MM-DD
**Status:** Active | In Progress | Resolved
**Severity:** Critical | High | Medium | Low
**Phase:** Phase N
**Component:** API | Database | Frontend | Deployment

### Description
[Detailed description of the bug]

### Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Root Cause
[Analysis of why this happened]

### Solution
[How it was fixed]

### Prevention
[How to prevent this in the future - design rule, test case, etc.]

### Related Files
- `path/to/file.py:line`
- `path/to/other/file.py:line`
```

---

## Issue Labels

Use these labels when tracking issues:
- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `documentation` - Documentation needed
- `question` - Further information needed
- `wontfix` - This will not be worked on
- `duplicate` - This issue already exists
