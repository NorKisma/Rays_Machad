import os
import re

def update_po_file(filepath, translations):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    updated_count = 0
    skipped_count = 0
    
    for msgid_parts, msgstr in translations.items():
        if isinstance(msgid_parts, tuple):
            # Multiline msgid
            msgid_str = '""\n' + '\n'.join([f'"{p}"' for p in msgid_parts])
            # Use regex to allow for potential whitespace variations
            pattern = re.escape(f'msgid {msgid_str}') + r'\s+msgstr\s+""'
            replace_str = f'msgid {msgid_str}\nmsgstr "{msgstr}"'
        else:
            # Single line msgid
            pattern = re.escape(f'msgid "{msgid_parts}"') + r'\s+msgstr\s+""'
            replace_str = f'msgid "{msgid_parts}"\nmsgstr "{msgstr}"'
        
        if re.search(pattern, content):
            content = re.sub(pattern, replace_str, content)
            print(f"Updated: {msgid_parts} -> {msgstr}")
            updated_count += 1
        else:
            # Check if it's already translated
            msgid_only = f'msgid {msgid_str}' if isinstance(msgid_parts, tuple) else f'msgid "{msgid_parts}"'
            if msgid_only in content:
                # Check if it has a non-empty msgstr
                translated_pattern = re.escape(msgid_only) + r'\s+msgstr\s+"[^"]+"'
                if re.search(translated_pattern, content):
                    skipped_count += 1
                else:
                    # Try to see if it's just formatted differently
                    pass
            else:
                pass

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Summary for {os.path.basename(filepath)}: Updated {updated_count}, Skipped {skipped_count}")

so_translations = {
    # Sidebar & Nav
    "Dashboard": "Dashboard-ka",
    "Students": "Ardayda",
    "Teachers": "Macalimiinta",
    "Classes": "Fasallada",
    "Attendance": "Imaanshaha",
    "Reports": "Warbixinnada",
    "Announcements": "Ogeysiisyada",
    "General Settings": "Dejinta Guud",
    "SaaS Master Admin": "Maamulaha Guud ee SaaS",
    
    # Roles & Profiles
    "Administrator": "Maamule",
    "Teacher": "Macallin",
    "Staff": "Shaqaale",
    "Finance": "Maaliyad",
    "Parent": "Waali",
    "Student": "Arday",
    "Security": "Amniga",
    "Change Password": "Badel Password-ka",
    "Logout": "Ka Bax",
    "My Profile": "Profile-kayga",
    "My Schedule": "Jadwalkayga",
    "My Children": "Caruurtayda",
    "Payments": "Lacagaha",
    "Rays Machad Management": "Maamulka Madrasadda",
    "Admin Dashboard": "Dashboard-ka Maamulka",
    "Select Language": "Dooro Luqadda",
    "Official Record": "Diiwaanka Rasmiga ah",

    # Dashboard & Welcome
    "Welcome back": "Ku soo dhawaaw",
    "First Term 2026": "Term-ka Koowaad 2026",
    "Add Student": "Ku dar Arday",
    "New Announcement": "Wargelin Cusub",
    "School Overview": "Guudmarka Dugsiga",
    "Real-time": "Xilligan la joogo",
    "Quick Operations": "Hawlgallo Degdeg ah",
    "Financials": "Maaliyadda",
    "Profit & Loss": "Faa'iidada & Qasaaraha",
    "Exams": "Imtixaannada",
    "Announcement": "Wargelin",
    "System Overview": "Guudmarka Nidaamka",
    "Facility": "Xarunta",
    "Session": "Kalfadhiga",
    "Database": "Xogta",
    "Synced": "Isku xiran",
    "Version": "Nuskhadda",
    "Backup": "Kayd",
    "Restore": "Soo celi",
    "Top Students": "Ardayda ugu sarreysa",
    "View All": "Eeg Dhammaan",
    "Institutional Announcements": "Wargelinta Machadka",
    "Stay updated with latest news": "La soco wararkii ugu dambeeyay",
    "No active announcements at the moment.": "Ma jiraan wargelinno firfircoon hadda.",
    "Create First Announcement": "Samee Wargelintii ugu horreysay",
    "Optimal": "Aad u wanaagsan",
    "New registration.": "Diiwaangelin cusub.",
    "Staff & Roles.": "Shaqaalaha & Doorka.",
    "Fees & expenses.": "Kharashyada & khidmadaha.",
    "Financial health.": "Bedqabka maaliyadda.",

    # Multiline
    ("Here's a real-time overview of your\\n", "                institution's performance and upcoming activities."): "Halkan ka eeg dulmarka tooska ah ee waxqabadka machadkaaga iyo hawlaha soo socda.",
    ("Total\\n", "                Students"): "Wadarta Ardayda",
    ("Total\\n", "                Teachers"): "Wadarta Macallimiinta",
    ("Total\\n", "                Classes"): "Wadarta Fasallada",
    ("System\\n", "                Health"): "Caafimaadka Nidaamka",
    ("Quick\\n", "                    Operations"): "Hawlgallo Degdeg ah",
    ("Stay updated with latest\\n", "                        news"): "La soco wararkii ugu dambeeyay",
    ("Live\\n", "                            Environment Status"): "Xaaladda deegaanka ee hadda"
}

ar_translations = {
    # Sidebar & Nav
    "Dashboard": "لوحة التحكم",
    "Students": "الطلاب",
    "Teachers": "المعلمون",
    "Classes": "الصفوف الدراسية",
    "Attendance": "الحضور",
    "Reports": "التقارير",
    "Announcements": "الإعلانات",
    "General Settings": "الإعدادات العامة",
    "SaaS Master Admin": "مدير النظام العام",

    # Roles & Profiles
    "Administrator": "مدير النظام",
    "Teacher": "معلم",
    "Staff": "موظف",
    "Finance": "مالية",
    "Parent": "ولي أمر",
    "Student": "طالب",
    "Security": "الأمان",
    "Change Password": "تغيير كلمة المرور",
    "Logout": "تسجيل الخروج",
    "My Profile": "ملفي الشخصي",
    "My Schedule": "جدولي",
    "My Children": "أطفالي",
    "Payments": "المدفوعات",
    "Rays Machad Management": "إدارة المدرسة",
    "Admin Dashboard": "لوحة تحكم المسؤول",
    "Select Language": "اختر اللغة",
    "Official Record": "سجل رسمي",

    # Dashboard & Welcome
    "Welcome back": "مرحباً بعودتك",
    "First Term 2026": "الفصل الأول 2026",
    "Add Student": "إضافة طالب",
    "New Announcement": "إعلان جديد",
    "School Overview": "نظرة عامة على المدرسة",
    "Real-time": "الوقت الحقيقي",
    "Quick Operations": "عمليات سريعة",
    "Financials": "المالية",
    "Profit & Loss": "الأرباح والخسائر",
    "Exams": "الامتحانات",
    "Announcement": "إعلان",
    "System Overview": "نظرة عامة على النظام",
    "Facility": "المرافق",
    "Session": "الجلسة",
    "Database": "قاعدة البيانات",
    "Synced": "متزامن",
    "Version": "الإصدار",
    "Backup": "نسخ احتياطي",
    "Restore": "استعادة",
    "Top Students": "أعلى الطلاب",
    "View All": "عرض الكل",
    "Institutional Announcements": "إعلانات المؤسسة",
    "Stay updated with latest news": "ابق على اطلاع بآخر الأخبار",
    "No active announcements at the moment.": "لا توجد إعلانات نشطة في الوقت الحالي.",
    "Create First Announcement": "إنشاء الإعلان الأول",
    "Optimal": "ممتاز",
    "New registration.": "تسجيل جديد.",
    "Staff & Roles.": "الموظفين والأدوار.",
    "Fees & expenses.": "الرسوم والمصاريف.",
    "Financial health.": "الوضع المالي.",

     # Multiline
    ("Here's a real-time overview of your\\n", "                institution's performance and upcoming activities."): "إليك نظرة عامة في الوقت الفعلي على أداء مؤسستك والأنشطة القادمة.",
    ("Total\\n", "                Students"): "إجمالي الطلاب",
    ("Total\\n", "                Teachers"): "إجمالي المعلمين",
    ("Total\\n", "                Classes"): "إجمالي الفصول",
    ("System\\n", "                Health"): "حالة النظام",
    ("Quick\\n", "                    Operations"): "عمليات سريعة",
    ("Stay updated with latest\\n", "                        news"): "ابق على اطلاع بآخر الأخبار",
    ("Live\\n", "                            Environment Status"): "حالة البيئة الحية"
}

if __name__ == "__main__":
    print("Updating Somali translations...")
    update_po_file('app/translations/so/LC_MESSAGES/messages.po', so_translations)

    print("\nUpdating Arabic translations...")
    update_po_file('app/translations/ar/LC_MESSAGES/messages.po', ar_translations)
