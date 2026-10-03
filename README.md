# **Fits 🦍** [![LGPL License](https://img.shields.io/badge/license-LGPL-green.svg)](https://www.gnu.org/licenses/lgpl-3.0)  [![Docker](https://img.shields.io/badge/Docker-Fits-blue?logo=docker)](https://hub.docker.com/r/fits/fits)

**Fits** is a Free and Open Source HRMS (Human Resource Management System) Software designed to streamline HR processes and enhance organizational efficiency.

![Fits Screenshot](https://github.com/fits-opensource/fits/assets/131998600/1317bd0a-03a8-40be-8fb2-ecb655bb5c13)

---

## **Installation**

Fits can be installed on your system by following the steps below. Ensure you have **Python**, **Django**, and a **database** (preferably PostgreSQL) installed as prerequisites.

---

## **Prerequisites**

### **1. Python Installation**

#### **Ubuntu**
1. Open the terminal and install Python:
   ```bash
   sudo apt-get install python3
   ```
2. Verify the installation:
   ```bash
   python3 --version
   ```

#### **Windows**
1. Download Python from the [official website](https://www.python.org/downloads/windows/).
2. During installation, ensure you select **"Add Python to PATH"**.
3. Verify the installation:
   ```bash
   python --version
   ```

#### **macOS**
1. Install Homebrew (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```bash
   brew install python
   ```
3. Verify the installation:
   ```bash
   python3 --version
   ```

---


### **2. PostgreSQL Installation**

#### **Ubuntu**
1. **Update System Packages**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install PostgreSQL**:
   ```bash
   sudo apt install postgresql postgresql-contrib -y
   ```

3. **Start and Enable PostgreSQL**:
   ```bash
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```

4. **Verify Installation**:
   ```bash
   psql --version
   ```

5. **Configure PostgreSQL Database and User**:
   - Switch to the `postgres` user:
     ```bash
     sudo su postgres
     psql
     ```
   - Create a new role and database:
     ```sql
     CREATE ROLE fits LOGIN PASSWORD 'fits';
     CREATE DATABASE fits_main OWNER fits;
     \q
     ```
   - Exit the `postgres` user:
     ```bash
     exit
     ```

---

#### **Windows**
1. **Download PostgreSQL**:
   - Download the installer from the [PostgreSQL Official Site](https://www.postgresql.org/download/windows/).

2. **Install PostgreSQL**:
   - Follow the setup wizard and set a password for the PostgreSQL superuser.

3. **Verify Installation**:
   ```powershell
   psql -U postgres
   ```

4. **Configure PostgreSQL Database and User**:
   - Access PostgreSQL:
     ```powershell
     psql -U postgres
     ```
   - Create a new role and database:
     ```sql
     CREATE ROLE fits LOGIN PASSWORD 'fits';
     CREATE DATABASE fits_main OWNER fits;
     \q
     ```

---

#### **macOS**
1. **Install PostgreSQL via Homebrew**:
   ```bash
   brew install postgresql
   ```

2. **Start PostgreSQL**:
   ```bash
   brew services start postgresql
   ```

3. **Verify Installation**:
   ```bash
   psql --version
   ```

4. **Configure PostgreSQL Database and User**:
   - Create a database and user:
     ```bash
     createdb fits_main
     createuser fits
     psql -c "ALTER USER fits WITH PASSWORD 'fits';"
     ```

---

## **Install Fits**

Follow the steps below to install **Fits** on your system. Fits is compatible with **Ubuntu**, **Windows**, and **macOS**.

---

### **1. Clone the Repository**

#### **Ubuntu**
```bash
sudo git init
sudo git remote add fits https://fits-opensource@github.com/fits-opensource/fits.git
sudo git pull fits master
```

#### **Windows**
```powershell
git init
git remote add fits https://fits-opensource@github.com/fits-opensource/fits.git
git pull fits master
```

#### **macOS**
```bash
git init
git remote add fits https://fits-opensource@github.com/fits-opensource/fits.git
git pull fits master
```

### **2. Set Up Python Virtual Environment**

#### **Ubuntu**
1. Install `python3-venv`:
   ```bash
   sudo apt-get install python3-venv
   ```
2. Create and activate the virtual environment:
   ```bash
   python3 -m venv fitsvenv
   source fitsvenv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

#### **Windows**
1. Create and activate the virtual environment:
   ```powershell
   python -m venv fitsvenv
   .\fitsvenv\Scripts\activate
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

#### **macOS**
1. Create and activate the virtual environment:
   ```bash
   python3 -m venv fitsvenv
   source fitsvenv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```


### **3. Configure Environment Variables**

1. Rename the environment file:
   ```bash
   mv .env.dist .env
   ```

2. Edit the `.env` file and set the following values:
   ```env
   DEBUG=True
   TIME_ZONE=Asia/Kolkata
   SECRET_KEY=django-insecure-j8op9)1q8$1&@^s&p*_0%d#pr@w9qj@lo=3#@d=a(^@9@zd@%j
   ALLOWED_HOSTS=www.example.com,example.com,*
   DB_INIT_PASSWORD=d3f6a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=fits_main
   DB_USER=fits
   DB_PASSWORD=fits
   DB_HOST=localhost
   DB_PORT=5432
   ```

---

### **4. Run Django Migrations**

Follow these steps to run migrations and set up the database.

#### **Ubuntu/macOS**
1. Apply migrations:
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   ```

#### **Windows**
1. Apply migrations:
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```
---

### **5. Enable Translation**

To enable translations and breadcrumbs text, compile the translations using the following commands.

#### **Ubuntu/macOS**
```bash
python3 manage.py compilemessages
```

#### **Windows**
```powershell
python manage.py compilemessages
```

---

### **6. Run the Project**

To run the project locally, execute the following commands.

#### **Ubuntu/macOS**
```bash
python3 manage.py runserver
```

#### **Windows**
```powershell
python manage.py runserver
```

---

### **Accessing Fits**

If everything is configured correctly, you should be able to access your Fits app at **http://localhost:8000**.
![Initialize Database in Fits HRMS](https://www.fits.com/wp-content/uploads/2024/12/how-to-initialize-the-database-in-fits-hrms-step-by-step-1-1024x576.png)


#### **Initial Setup**
From the login page, you will have two options:
1. **Initialize Database**: Use this option to initialize the Fits database by creating a super admin, headquarter company, department, and job position. Authenticate using the `DB_INIT_PASSWORD` specified in the `.env` file.
2. **Load Demo Data**: Use this option if you want to work with demo data. Authenticate using the `DB_INIT_PASSWORD` specified in the `.env` file.

#### **Running on a Custom Port**
If you wish to run the Fits application on a different port, specify the port number after the `runserver` command. For example:
```bash
python3 manage.py runserver 8080  # For Ubuntu/macOS
python manage.py runserver 8080   # For Windows
```


## **Features**

- **Recruitment**
- **Onboarding**
- **Employee Management**
- **Attendance Tracking**
- **Leave Management**
- **Asset Management**
- **Payroll**
- **Performance Management System**
- **Offboarding**
- **Helpdesk**

---

## **🎉 Recent Updates - UI & Button Functionality Audit (March 2026)**

### ✅ Comprehensive Button & Form Fixes Completed

A complete audit of all HCMS modules has been conducted to identify and fix non-working buttons and forms. **All identified issues have been resolved and the system is production-ready.**

#### **Issues Fixed Summary**
| Module | Issues | Status |
|--------|--------|--------|
| **Payroll - GL Integration** | 6 | ✅ COMPLETE |
| **Payroll - ICBS Integration** | 4 | ✅ COMPLETE |
| **Learning - External Integrations** | 4 | ✅ COMPLETE |
| **Talent - Sidebar** | 1 | ✅ COMPLETE |
| **All Other Modules** | 0 | ✅ VERIFIED |
| **TOTAL** | **15** | **✅ 100% FIXED** |

#### **Key Improvements**

**Payroll Module - GL Integration**
- ✅ Fixed "Add New Mapping" button with proper form creation view
- ✅ Implemented GL mapping edit functionality
- ✅ Added GL mapping deletion with confirmation
- ✅ Created complete GL mapping form template with validation

**Payroll Module - ICBS Integration**
- ✅ Fixed "Process All via ICBS" button with bulk processing handler
- ✅ Implemented individual payment processing
- ✅ Added ICBS configuration update form with proper POST handling
- ✅ All forms now have CSRF protection

**Learning Module - External Integrations**
- ✅ Fixed LinkedIn Learning connection form submission
- ✅ Fixed Udemy for Business connection form submission
- ✅ Implemented external catalog sync functionality
- ✅ Added proper form validation and error handling

**All 16+ Modules Verified**
- ✅ Verified 450+ templates for button/form integrity
- ✅ Confirmed 200+ URL patterns properly registered
- ✅ Validated 100+ view functions for completeness
- ✅ Zero outstanding button functionality issues

#### **Documentation**
For detailed information about all fixes and verification, see:
- 📋 **[FINAL_COMPLETE_AUDIT_REPORT.md](docs/FINAL_COMPLETE_AUDIT_REPORT.md)** - Complete audit findings
- 🔍 **[COMPREHENSIVE_MODULE_ANALYSIS.md](docs/COMPREHENSIVE_MODULE_ANALYSIS.md)** - Technical analysis
- ✅ **[BUTTON_FIXES_IMPLEMENTATION_REPORT.md](docs/BUTTON_FIXES_IMPLEMENTATION_REPORT.md)** - Implementation details
- 📊 **[VALIDATION_CHECKLIST.md](docs/VALIDATION_CHECKLIST.md)** - Testing guide

---

## **Roadmap**

- **Calendar App** - Development Under Process
- **Project Management** - Development Under Process
- **Chat App** - Development Under Process
- **More to come...**

---

## **Languages and Tools Used**

<p align="left">
  <a href="https://getbootstrap.com" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/bootstrap/bootstrap-plain-wordmark.svg" alt="bootstrap" width="40" height="40"/>
  </a>
  <a href="https://www.chartjs.org" target="_blank" rel="noreferrer">
    <img src="https://www.chartjs.org/media/logo-title.svg" alt="chartjs" width="40" height="40"/>
  </a>
  <a href="https://www.w3schools.com/css/" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/css3/css3-original-wordmark.svg" alt="css3" width="40" height="40"/>
  </a>
  <a href="https://www.djangoproject.com/" target="_blank" rel="noreferrer">
    <img src="https://cdn.worldvectorlogo.com/logos/django.svg" alt="django" width="40" height="40"/>
  </a>
  <a href="https://git-scm.com/" target="_blank" rel="noreferrer">
    <img src="https://www.vectorlogo.zone/logos/git-scm/git-scm-icon.svg" alt="git" width="40" height="40"/>
  </a>
  <a href="https://www.w3.org/html/" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/html5/html5-original-wordmark.svg" alt="html5" width="40" height="40"/>
  </a>
  <a href="https://www.linux.org/" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/linux/linux-original.svg" alt="linux" width="40" height="40"/>
  </a>
  <a href="https://www.postgresql.org" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original-wordmark.svg" alt="postgresql" width="40" height="40"/>
  </a>
  <a href="https://www.python.org" target="_blank" rel="noreferrer">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/>
  </a>
</p>

---

## **Authors**

[Cybrosys Technologies](https://www.cybrosys.com/)

---

## **About**

[Fits](https://www.fits.com/) is an open-source HRMS solution designed to simplify HR operations and improve organizational efficiency.

---

This README provides a comprehensive guide to installing and setting up Fits on various platforms. If you encounter any issues, feel free to reach out to the Fits community for support. Happy coding! 🚀


---

## Recruitment & Manpower Module — Feature Map

All URLs are prefixed with `http://127.0.0.1:8000`.

| # | Feature | Sidebar Menu | Button Name | URL |
|---|---------|-------------|------------|-----|
| 1 | Candidate Dashboard | Recruitment → **Candidates** | — | `/recruitment/candidates/dashboard/` |
| 1a | Bulk CV Upload (drag-drop) | on dashboard page | **Upload** | `/recruitment/candidates/cv-upload/bulk/` |
| 1b | Single CV Upload | Recruitment → **CV Upload** | **Create Candidate** | `/recruitment/candidates/cv-upload/` |
| 1c | Search Candidates | on dashboard page | **Search** | `/recruitment/candidates/dashboard/?q=` |
| 2 | New Manpower Request | Recruitment → **Manpower Requests** | **+ New Request** | `/recruitment/manpower/create/` |
| 2a | View All Requests | Recruitment → **Manpower Requests** | **View** (per row) | `/recruitment/manpower/` |
| 2b | Submit for Approval | on request detail page | **Submit for Approval** | `/recruitment/manpower/<id>/submit/` |
| 3 | Approvals Inbox | Recruitment → **Pending Approvals** | **✓ Approve** / **✗ Reject** | `/recruitment/approvals/inbox/` |
| 4 | Create Approval Rule | Recruitment → **Approval Rules** | **+ New Rule** / **Save Rule** | `/recruitment/approvals/rules/create/` |
| 4a | View Approval Rules | Recruitment → **Approval Rules** | — | `/recruitment/approvals/rules/` |
| 5 | Bulk Import Candidates | Recruitment → **Bulk Import Candidates** | **Download template** / **Preview** / **Import Now** | `/recruitment/bulk-import/candidates/` |
| 5a | Candidate CSV Template | on bulk import page | **Download template** | `/recruitment/bulk-import/candidates/template/` |
| 6 | Bulk Import Manpower | Recruitment → **Bulk Import Manpower** | **Download template** / **Preview** / **Import Now** | `/recruitment/bulk-import/manpower/` |
| 6a | Manpower CSV Template | on bulk import page | **Download template** | `/recruitment/bulk-import/manpower/template/` |
| 7 | Public Careers Page | Recruitment → **Career Page** | **View & Apply** | `/recruitment/careers/` |
| 7a | Job Detail | on careers page | **Apply Now** | `/recruitment/careers/<slug>/` |
| 7b | Apply for Job | on job detail page | **Submit Application** | `/recruitment/careers/<slug>/apply/` |
| 7c | Job Feed (JSON) | — (share with portals) | — | `/recruitment/careers/feed.json` |
| 8 | Offer & Onboarding Tracking | Recruitment → **Offer Tracking** | **Update** (per row) | `/recruitment/offer-tracking/` |
| 8a | Update Clearance Status | on tracking page | **Save** | `/recruitment/offer-tracking/<id>/update/` |
| 9 | Reports Dashboard | Recruitment → **Reports** | — | `/recruitment/reports/` |
| 9a | Download Candidates CSV | on reports page | **⬇ Candidates CSV** | `/recruitment/reports/export/candidates/` |
| 9b | Download Manpower CSV | on reports page | **⬇ Manpower CSV** | `/recruitment/reports/export/manpower/` |
| 10 | CV Screening (AI) | Recruitment → **CV Screening** | — | `/recruitment/cv-screening/` |
