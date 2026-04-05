# Madrasah Management System - Role Permissions Summary

## Updated: 2026-01-27 (Dynamic System)

This document outlines the **Dynamic Access Control System** implemented in the Madrasah Management System. Unlike hardcoded roles, the Admin can now manage permissions for each role dynamically through the system settings.

---

## 🎯 Dynamic Permissions Management

Administrators (Admin role) can now manage system access through:
**Settings > Role Permissions**

### **Module / Section Matrix**
You can enable/disable access for the following modules:
1. **Students** - Student dossiers and management
2. **Teachers** - Teacher directory and information
3. **Classes** - Class schedules and management
4. **Attendance** - Attendance tracking
5. **Exams** - Exam records and results
6. **Financials** - Fee structures and financial records
7. **Reports** - System reports and analytics
8. **Manage Users** - Management staff can manage system users (if granted)

---

## 🛡️ Role Access Logic

### **1. Admin (A)**
- **Full System Access**: Admins always have access to all modules.
- **Settings & Permissions**: Only Admins can manage system-wide settings and role permissions.

### **2. Manageable Roles (Teacher, Staff, Finance, Parent)**
- Access is **Dynamic**.
- Use the **Role Permissions** matrix to toggle access for these roles.
- For example: You can allow the **Finance** role to see "Financials" and "Reports" but deny them access to "Attendance".

### **3. Student (U)**
- **Strictly Limited**: Students only have access to their personal profile.
- This role is not part of the dynamic matrix for security reasons.

---

## 🌍 Multi-Language Matrix

All permission titles and descriptions are available in:
- **English** (en)
- **Arabic** (ar) - العربية
- **Somali** (so) - Soomaali

---

## 🔐 Security & Implementation

1. **Model**: `RolePermission` stores the (Role, Module, IsAllowed) relationship.
2. **Template Check**: `{% if RolePermission.check(current_user.role, 'module_name') %}` is used across the system.
3. **Database Seeding**: The system is pre-seeded with professional defaults for all roles.
4. **Admin Override**: Admin ('A') bypasses all permission checks for absolute control.

---

## 🚀 How to Manage Permissions

1. Login as an **Admin**.
2. Go to the sidebar and click **Role Permissions**.
3. Use the **Check Switches (Toggle)** to allow or deny a section for a specific role.
4. Click **Save Permissions**.
5. The changes apply instantly for all users of those roles.

---

**System:** Madrasah Management System  
**Version:** 3.0 (Dynamic RBAC)  
**Last Updated:** January 27, 2026
