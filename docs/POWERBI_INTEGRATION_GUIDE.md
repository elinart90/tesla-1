# VRA File Management System
## Power BI Integration Guide
### Volta River Authority

---

## Overview

The VRA-FMS integrates with **Microsoft Power BI** to embed live dashboards and reports directly within the application. The integration uses the **Power BI Embed API** with **Azure Active Directory (AAD) service principal authentication**, enabling secure, token-based report embedding.

---

## Architecture

```
VRA-FMS Django App
        │
        ▼ (Client Credentials Grant)
Azure Active Directory
        │
        ▼ (Access Token)
Power BI REST API
        │
        ▼ (Embed Token)
Power BI JavaScript SDK (client browser)
        │
        ▼
Embedded Report (iFrame in dashboard)
```

---

## Prerequisites

- Microsoft 365 / Power BI Pro or Premium Per User license
- Azure AD access (Global Admin or Application Admin role)
- Power BI report published to a workspace
- VRA system admin access

---

## Step-by-Step Integration

---

### Step 1: Register an Azure AD Application

1. Go to: https://portal.azure.com
2. Navigate to: **Azure Active Directory → App Registrations → New Registration**
3. Fill in:
   - **Name**: `VRA-FMS Power BI`
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI**: Leave blank (we use client credentials)
4. Click **Register**
5. Note down:
   - **Application (client) ID** → `POWERBI_CLIENT_ID`
   - **Directory (tenant) ID** → `POWERBI_TENANT_ID`

---

### Step 2: Create a Client Secret

1. In your App Registration → **Certificates & Secrets**
2. Click **New client secret**
3. Description: `VRA-FMS Secret`
4. Expiry: `24 months` (recommended)
5. Click **Add**
6. **Copy the secret Value immediately** → `POWERBI_CLIENT_SECRET`
   > ⚠️ You cannot view this value again after leaving the page.

---

### Step 3: Configure API Permissions

1. In App Registration → **API Permissions**
2. Click **Add a permission → Power BI Service**
3. Select **Application permissions**
4. Add these permissions:
   - `Report.ReadWrite.All`
   - `Dataset.ReadWrite.All`
   - `Workspace.Read.All`
5. Click **Grant admin consent for [your organization]**
6. Confirm all permissions show ✅ **Granted**

---

### Step 4: Create a Power BI Workspace

1. Go to: https://app.powerbi.com
2. **Workspaces → Create a workspace**
3. Name: `VRA File Management Reports`
4. Click **Save**
5. Note the Workspace ID from the URL:  
   `https://app.powerbi.com/groups/{WORKSPACE_ID}/...`
   → `POWERBI_WORKSPACE_ID`

---

### Step 5: Add Service Principal to Workspace

1. In your Power BI workspace → **Settings → Access**
2. Search for your Azure AD app name: `VRA-FMS Power BI`
3. Set role to **Member** or **Admin**
4. Click **Add**

> ⚠️ Without this step, the app cannot access the workspace.

---

### Step 6: Enable Service Principal in Power BI Admin Portal

1. Go to: https://app.powerbi.com/admin-portal/tenantSettings
2. Find: **Developer settings**
3. Enable: **Allow service principals to use Power BI APIs**
4. Apply to: **Specific security groups** (add your AAD app or All)
5. Click **Apply**

---

### Step 7: Create & Publish a Report

#### Option A: Connect to VRA PostgreSQL Database

1. Open **Power BI Desktop**
2. **Get Data → PostgreSQL Database**
3. Server: `your-vra-db-server`
4. Database: `vra_fms_db`
5. Import tables:
   - `files_managedfile`
   - `files_fileretrievallog`
   - `notifications_notification`
   - `reminders_filereminder`
   - `auth_user`

#### Recommended Report Pages:

| Page | Visualizations |
|------|---------------|
| **Overview** | KPI cards: Total Files, Retrieved, Pending, Reminders |
| **Upload Trends** | Line/bar chart of daily uploads |
| **File Status** | Doughnut chart by status |
| **Retrieval Activity** | Table of recent retrievals with user/date |
| **Notification Log** | Table/bar of sent vs failed notifications |
| **Department Analysis** | Stacked bar – uploads by department |

---

### Step 8: Publish Report to Power BI Service

1. In Power BI Desktop: **File → Publish → Publish to Power BI**
2. Select workspace: `VRA File Management Reports`
3. After publish, go to the workspace in the browser
4. Click on your report → note Report ID from URL:
   `https://app.powerbi.com/groups/{workspace_id}/reports/{REPORT_ID}/...`
   → `POWERBI_REPORT_ID`

---

### Step 9: Configure Dataset Scheduled Refresh

1. Workspace → **Datasets → Your Dataset → Settings**
2. Under **Data source credentials**: configure PostgreSQL credentials
3. Under **Scheduled refresh**:
   - Enable refresh
   - Set frequency: Every day / Every hour
   - Set times aligned with VRA working hours

---

### Step 10: Set Environment Variables

In your `.env` file:

```env
POWERBI_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
POWERBI_CLIENT_SECRET=your-client-secret-value
POWERBI_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
POWERBI_WORKSPACE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
POWERBI_REPORT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
POWERBI_DATASET_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

### Step 11: Test the Integration

Start your server and navigate to:
```
http://127.0.0.1:8000/dashboard/reports/
```

The report should load embedded in the VRA-FMS interface.

---

## Embed Token Flow (Technical)

```python
# 1. Get Azure AD token
POST https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token
Body: grant_type=client_credentials
      client_id={client_id}
      client_secret={client_secret}
      scope=https://analysis.windows.net/powerbi/api/.default

# 2. Get Power BI embed token
POST https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/{report_id}/GenerateToken
Header: Authorization: Bearer {access_token}
Body: {"accessLevel": "View"}

# 3. Embed in browser using powerbi-client JS SDK
```

---

## Troubleshooting

| Error | Solution |
|-------|---------|
| `AADSTS700016: Application not found` | Wrong Client ID or Tenant ID |
| `Unauthorized` | Client secret expired or wrong |
| `Capacity not assigned` | Workspace needs Premium capacity or Pro license |
| `Service principal not in workspace` | Add app to workspace (Step 5) |
| `Token expired` | Re-generate embed token (tokens expire in ~60 min) |
| `Service principals not allowed` | Enable in Power BI Admin Portal (Step 6) |
| Report shows blank | Check browser console for JS errors; verify embed URL |

---

## Security Best Practices

- Rotate `POWERBI_CLIENT_SECRET` every 12-24 months
- Use **Row-Level Security (RLS)** in Power BI for department-level data isolation
- Store all credentials in `.env` — never hardcode in source code
- Use HTTPS in production to protect embed tokens

---

## Power BI REST API Reference

| Endpoint | Purpose |
|----------|---------|
| `GET /v1.0/myorg/groups` | List workspaces |
| `GET /v1.0/myorg/groups/{id}/reports` | List reports |
| `POST /v1.0/myorg/groups/{id}/reports/{id}/GenerateToken` | Generate embed token |
| `GET /v1.0/myorg/groups/{id}/datasets` | List datasets |
| `POST /v1.0/myorg/datasets/{id}/refreshes` | Trigger data refresh |

Full reference: https://docs.microsoft.com/en-us/rest/api/power-bi/

---

*VRA File Management System – Power BI Integration Guide*  
*Volta River Authority, Ghana*
