# School Database Management System(SDMS)

Built with Django (Python)

This document outlines the architecture and core components of the SDMS, designed to manage all academic, administrative, and financial operations within a school environment.

1. Architectural Overview

The system utilizes a modular, multi-application structure where each primary function (Users, Academics, Finance) is contained within its own Django app. Authentication is centralized and relies on Django's extensible AbstractUser model to handle the complex, multi-role hierarchy.
Security Principles:

CSRF Protection: Standard Django protection ({% csrf_token %}) is enforced on all state-changing POST requests.

Token Management (UUID): UUIDs are used for secure, non-sequential tokens, primarily for:

Password Reset Links: Ensuring unique, hard-to-guess, and time-sensitive links.

Temporary Invitation Links: For initial sign-up of parents/students by the admin.

2. Core User Roles and Permissions

All users are built upon a custom User model, extended by a Profile model that defines the specific role and necessary metadata.
Role

Primary App Access

Core Responsibilities

Admin

All Apps

System setup, user account management, app configuration, data migration.

Headteacher

Academics, Communication, Finance (Read-Only)

Strategic oversight, performance reporting, approving Teacher/Course changes.

Teacher

Academics, Communication

Course management, assigning grades, attendance tracking, resource sharing.
Student

Academics, Communication

Viewing grades, attendance record, accessing course materials, submitting assignments.

Accountant

Finance

Fee management, transaction logging, payroll processing, issuing invoices/receipts.

Parent

Academics (Read-Only), Communication

Monitoring their child's grades, attendance, and fee status.

3. Application Structure (Django Apps)

The system is logically divided into four main Django applications:

A. users App (Authentication & Profiles)

Models: CustomUser (Extends AbstractUser), Profile (OneToOne with CustomUser to hold role, associated_class, etc.), RoleGroup.

Functionality: Handles sign-up, login, logout, password reset (using UUID tokens), and role-based access control (RBAC).

B. academics App (Classes & Grades)

Models: Course, Class (e.g., Grade 10A), Subject, Enrollment (links Student to Class/Subject), Assignment, Grade.

Functionality: Timetable management, grade entry, attendance records, and generating student report cards.

C. finance App (Fees & Accounting)

Models: FeeStructure (defines tuition, library fee, etc.), Invoice, Transaction (links invoice to payment), PaymentMethod.

Functionality: Invoice generation, payment tracking, balance reporting for parents, and basic payroll.

D. communication App (Messaging & Announcements)

Models: Announcement (for Admin/Headteacher), Message (simple internal messaging between Teachers/Parents).

Functionality: Pushing school-wide or class-specific announcements; secure, direct messaging between authorized users.

4. Role-Based Routing

The system uses a single domain, with routing based on the authenticated user's role, ensuring they only see relevant data and actions.

User Role

Dashboard Route

Example Data Views

Admin/Headteacher

/dashboard/admin/

System Health, Strategic Reports, User Registration Requests.

Teacher

/dashboard/teacher/

List of assigned classes, quick links for grading/attendance.

Student

/dashboard/student/

Current course load, recent grades, upcoming assignments.

Parent

/dashboard/parent/

Child's attendance, report card summary, outstanding fee balance.

Accountant

/dashboard/finance/

Pending invoices, payment history, transaction filters.

5. Deployment Notes

Environment: Production environment must be configured with HTTPS and secure cookie settings.

Database: PostgreSQL is recommended for robust production use.

Performance: Optimize database queries for complex reports (e.g., fetching all student grades for a term).
