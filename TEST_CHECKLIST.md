# Kitab Platform - Deployment Testing Checklist

Use this checklist to verify all functionality after deployment.

## Pre-Deployment Verification

- [ ] All code changes committed to `kitab-poc-deployment` branch
- [ ] Branch pushed to GitHub
- [ ] Backup tag `pre-kitab-backup` created and pushed
- [ ] No uncommitted changes in working directory

---

## Task 20: Deployment Health & Logs Verification

### Railway Backend Logs

- [ ] Open Railway dashboard → Backend service → Logs tab
- [ ] Verify no errors in startup logs
- [ ] Check for successful database connection message
- [ ] Verify uvicorn started successfully
- [ ] Note: Look for "Application startup complete"

### Vercel Frontend Logs

- [ ] Open Vercel dashboard → Project → Logs tab
- [ ] Verify build completed successfully
- [ ] Check for runtime errors (should be none)
- [ ] Verify deployment status is "Ready"

### Supabase Logs

- [ ] Open Supabase dashboard → Logs
- [ ] Check for connection attempts from Railway
- [ ] Verify no authentication errors
- [ ] Check query logs for successful operations

### Celery Worker Logs

- [ ] Open Railway dashboard → Worker service → Logs tab
- [ ] Verify worker shows "ready" status
- [ ] Check for Redis connection success
- [ ] Look for: `celery@[hostname] ready`

---

## Task 21: Smoke Test Deployment

### 1. Frontend Health Check

**Test**: Visit Vercel URL

- [ ] Page loads without errors
- [ ] No JavaScript errors in browser console (F12)
- [ ] "Kitab" branding appears in navigation
- [ ] Page title shows "Kitab" in browser tab

**How to check console errors**:

1. Open browser DevTools (F12)
2. Go to Console tab
3. Refresh page
4. Should see 0 errors (warnings are OK)

### 2. Backend Health Check

**Test**: Health endpoint

```bash
curl https://your-railway-url.railway.app/api/v1/health
```

**Expected response**:

```json
{ "status": "healthy", "service": "kitab-backend" }
```

- [ ] Health endpoint returns correct response
- [ ] Response time < 2 seconds

### 3. Database Connection Test

**Test**: Register new user account

1. Go to Vercel URL
2. Click "Register" or "Sign Up"
3. Fill in:
   - Email: test@example.com
   - Password: TestPassword123!
   - Confirm Password: TestPassword123!
4. Submit form

**Verification**:

- [ ] Registration succeeds (no errors)
- [ ] Redirected to login or dashboard
- [ ] User appears in Supabase dashboard (Authentication → Users)
- [ ] No database errors in Railway logs

### 4. Redis Connection Test

**Test**: Check Railway logs

- [ ] Railway backend logs show "Connected to Redis" (or similar)
- [ ] Celery worker logs show "ready" status
- [ ] No Redis connection errors

### 5. Authentication Flow Test

**Test**: Complete login flow

1. Login with test account created above
2. Verify JWT token is issued (check Network tab in DevTools)
3. Access protected route (dashboard)
4. Verify user stays logged in after page refresh

**Verification**:

- [ ] Login succeeds
- [ ] Dashboard loads
- [ ] User info displayed correctly
- [ ] Session persists after refresh

### 6. Document Upload Test (Critical - Tests Celery)

**Test**: Upload a small PDF document

1. Login to dashboard
2. Navigate to Documents section
3. Click "Upload Documents"
4. Select a small PDF file (< 5MB)
5. Click Upload

**Verification**:

- [ ] Upload initiates successfully
- [ ] Celery worker logs show processing task
- [ ] Document appears in documents list
- [ ] Document status changes to "processed"
- [ ] File appears in Supabase Storage bucket

**Check Celery logs for**:

```
Task app.tasks.process_document[...] received
Task app.tasks.process_document[...] succeeded
```

### 7. Chat Functionality Test

**Test**: Start a new chat

1. Navigate to Researcher/Chat section
2. Start new chat
3. Send message: "Who are you?"
4. Wait for response

**Verification**:

- [ ] Chat interface loads
- [ ] Message sends successfully
- [ ] AI response is generated
- [ ] Response identifies as "Kitab" (not "SurfSense")
- [ ] Response time < 10 seconds

### 8. Search Functionality Test

**Test**: Perform search query

1. Navigate to search/researcher
2. Enter query: "test search"
3. Submit search

**Verification**:

- [ ] Search executes
- [ ] Results are returned (or "no results" message)
- [ ] Citations are properly formatted
- [ ] No errors in console

---

## Task 22: Text Rebranding Verification

### Homepage Audit

Visit homepage (Vercel URL):

- [ ] Navigation bar shows "Kitab"
- [ ] Browser tab title shows "Kitab"
- [ ] Hero section text correct
- [ ] Footer shows "Kitab"
- [ ] No "SurfSense" references visible

### Dashboard Audit

Login and check dashboard:

- [ ] Sidebar shows "Kitab" logo/name
- [ ] Page titles show "Kitab"
- [ ] Settings pages show "Kitab"
- [ ] All button labels correct
- [ ] No "SurfSense" references visible

### Error Messages Test

Trigger errors to check branding:

- [ ] Visit /nonexistent (404 page)
- [ ] Submit empty form (validation error)
- [ ] Check error messages reference "Kitab" appropriately

### AI Agent Response Test

Ask agent about identity:

- [ ] Send message: "Who are you?"
- [ ] Response says "I am Kitab" (not "SurfSense")
- [ ] Check multiple responses for consistency

### Social Media Sharing Test

Share a link:

- [ ] Share Vercel URL on Twitter/LinkedIn
- [ ] Check Open Graph preview
- [ ] Preview shows "Kitab" branding
- [ ] Image and description correct

### Codebase Verification

Run grep searches:

```bash
# Frontend check
grep -r "SurfSense" surfsense_web/messages/
grep -r "SurfSense" surfsense_web/components/
grep -r "SurfSense" surfsense_web/app/

# Backend check
grep -r "SurfSense" surfsense_backend/app/agents/
grep -r "SurfSense" surfsense_backend/app/schemas/
```

**Verification**:

- [ ] Zero unintentional "SurfSense" references in user-facing text
- [ ] Only comments or technical references remain (acceptable)

---

## Task 23: Performance Baseline Measurement

### Page Load Time

Use browser DevTools → Network tab:

**Homepage**:

- [ ] Load time: **\_** seconds (target: < 2s)
- [ ] Total size: **\_** MB
- [ ] Number of requests: **\_**

**Dashboard**:

- [ ] Load time: **\_** seconds (target: < 3s)
- [ ] Total size: **\_** MB
- [ ] Number of requests: **\_**

### API Response Time

Test endpoints:

**Chat endpoint**:

```bash
# Time a simple chat request
time curl -X POST https://your-railway-url/api/v1/chats \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

- [ ] Response time: **\_** seconds (target: < 5s)

**Search endpoint**:

- [ ] Response time: **\_** seconds (target: < 2s)

### Document Processing Time

Upload 1MB PDF and measure:

- [ ] Upload initiation: **\_** seconds (target: < 1s)
- [ ] Processing time: **\_** seconds (baseline: 30-60s)
- [ ] Total time to "processed" status: **\_** seconds

### Performance Report

Create simple report:

```
Homepage load: X seconds
Dashboard load: X seconds
Chat response: X seconds
Search response: X seconds
Document processing: X seconds

Notes:
- Any significant slowdowns compared to local?
- Any optimization opportunities identified?
```

---

## Critical Issues Checklist

If any of these fail, deployment has critical issues:

- [ ] Backend health endpoint responds
- [ ] Frontend loads without errors
- [ ] User registration works
- [ ] User login works
- [ ] Database connection successful
- [ ] No CORS errors
- [ ] Celery worker is running
- [ ] Document upload triggers processing

---

## Optional Tests

### Email Functionality (if configured)

- [ ] Password reset email sends
- [ ] Email contains correct branding

### Multiple User Test

- [ ] Create second user account
- [ ] Both users can login simultaneously
- [ ] Data isolation works correctly

### Load Test (basic)

- [ ] Multiple concurrent requests succeed
- [ ] No rate limiting issues
- [ ] Response times remain consistent

---

## Post-Testing Actions

After all tests pass:

1. **Document Issues**:
   - [ ] Create GitHub issues for any bugs found
   - [ ] Note any performance concerns
   - [ ] Document workarounds if needed

2. **Update Documentation**:
   - [ ] Add deployment-specific notes
   - [ ] Document any configuration changes
   - [ ] Update README if needed

3. **Monitoring Setup**:
   - [ ] Set up error tracking (optional)
   - [ ] Configure uptime monitoring (optional)
   - [ ] Set up log aggregation (optional)

4. **Backup Strategy**:
   - [ ] Document database backup process
   - [ ] Test restore procedure
   - [ ] Schedule regular backups

---

## Test Results Summary

**Date**: ******\_******
**Tester**: ******\_******
**Environment**: Production (Railway + Vercel + Supabase)

**Overall Status**: ⬜ PASS | ⬜ PASS WITH ISSUES | ⬜ FAIL

**Critical Tests**: **_/8 passed
**Branding Tests**: _**/6 passed
**Performance Tests**: \_\_\_/4 passed

**Issues Found**: **\_**
**Blockers**: **\_**
**Notes**: **\_**

---

## Sign-off

- [ ] All critical tests passed
- [ ] All issues documented
- [ ] Deployment guide updated with learnings
- [ ] Ready for production use

**Approved by**: ******\_******
**Date**: ******\_******
