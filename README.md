# 🎓 School Management System (SDMS)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Django](https://img.shields.io/badge/Framework-Django%205.0-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

> **A comprehensive, enterprise-grade solution for modern school administration.**

---

## 🌟 Overview

The **School Database Management System (SDMS)** is a high-performance, modular platform designed to streamline academic, administrative, and financial operations. Whether managing a **Nursery**, **Primary**, or **Secondary** school, SDMS provides the tools needed for excellence.

---

## 🔥 Key Features

### 🏫 Multi-Level Support
Tailored workflows for all education stages:
- **Nursery**: Early childhood development tracking.
- **Primary**: Foundational academic management.
- **Secondary**: Advanced course tracking and performance analytics.

### 👥 Role-Based Excellence
Dedicated, high-fidelity dashboards for every stakeholder:
- **🛡️ Admin**: Global oversight and system configuration.
- **🎓 Headteacher**: Strategic reporting and operational approvals.
- **📊 DOS & DOD**: Specialized monitors for Academics and Discipline.
- **👩‍🏫 Staff & Teachers**: Portals for gradebooks, attendance, and reporting.
- **👨‍👩‍👧 Parent & Student**: Mobile-responsive portals for progress and fees.

### 💰 Financial Intelligence
- **Fee Management**: Real-time tracking of expected vs. collected fees.
- **Transaction Logs**: Detailed history for every student payment.
- **Accountant Dashboard**: Read-only financial oversight for administrative transparency.

### 🛡️ Smart Operations
- **Self-Service Registration**: Modern onboarding workflow for new staff members.
- **Admin Approval Gate**: Secure entry point requiring manual verification.
- **Audit Trails**: Forensic-level logging of all administrative actions.
- **Custom Roles**: Flexible support for Animateurs, Popular Staff, and more.

---

## 🛠️ Technology Stack

- **Backend**: Django (Python)
- **Database**: PostgreSQL (Production) / SQLite (Development)
- **Styling**: Modern CSS3, HTML5
- **Security**: UUID Tokens, CSRF Protection, HTTPS-ready

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Pip & Virtualenv

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Erneste304/School-Data-Management.git
   cd School-Data-Management
   ```

2. **Setup virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirement.txt
   ```

4. **Run Migrations & Start Server**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

---

## 📈 Public Information Portal

SDMS features a **Public Access Portal** where parents and guests can view:
- 📢 Latest School Notices
- 📊 Academic Trends & Statistics
- 📅 Event Calendars

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

Developed with ❤️ by [Dr. Erneste](https://github.com/Erneste304)
