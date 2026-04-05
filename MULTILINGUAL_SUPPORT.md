# Multi-Language Support Documentation

## Supported Languages

The Madrasah Management System supports **3 languages**:

1. 🇺🇸 **English (en)** - Default
2. 🇸🇦 **Arabic (ar)** - العربية (Full RTL support)
3. 🇸🇴 **Somali (so)** - Soomaali

## Complete Translation Coverage

### Subject Categories

| English | Arabic (العربية) | Somali (Soomaali) |
|---------|------------------|-------------------|
| Quranic Sciences | العلوم القرآنية | Cilmiga Quraanka |
| Islamic Jurisprudence | الفقه الإسلامي | Fiqhiga Islaamka |
| Theology & Creed | العقيدة والتوحيد | Caqiidada Islaamka |
| Prophetic Traditions | الحديث النبوي | Xadiiska Nabiga |
| Languages | اللغات | Luqadaha |
| Ethics & Manners | الأخلاق والآداب | Akhlaaqda iyo Edebta |

### Common Subject Names

| English | Arabic (العربية) | Somali (Soomaali) |
|---------|------------------|-------------------|
| Hifz (Memorization) | حفظ القرآن الكريم | Xifdhka Quraanka |
| Tajweed (Recitation) | التجويد | Tajwiidka |
| Tafsir (Exegesis) | التفسير | Tafsirka Quraanka |
| Fiqh (Jurisprudence) | الفقه | Fiqhiga |
| Aqeedah (Theology) | العقيدة | Caqiidada |
| Hadith (Traditions) | الحديث | Xadiiska |
| Seerah (Biography) | السيرة النبوية | Taarikhda Nabiga |
| Arabic Grammar (Nahw) | النحو العربي | Naxwaha Carabi |
| Arabic Morphology (Sarf) | الصرف العربي | Sarfka Carabi |

### Navigation Menu Items

| English | Arabic (العربية) | Somali (Soomaali) |
|---------|------------------|-------------------|
| Dashboard | لوحة التحكم | Guddiga Maamulka |
| Students | الطلاب | Ardayda |
| Teachers | المعلمون | Macalimiinta |
| Classes | الفصول | Fasalka |
| Class Schedules | جداول الفصول | Jadwalka Fasalka |
| Curriculum Subjects | المواد الدراسية | Maadooyinka Waxbarashada |
| Attendance | الحضور | Soo Joogitaanka |
| Exams | الامتحانات | Imtixaannada |
| Financials | المالية | Maaliyadda |
| Reports | التقارير | Warbixinnada |
| General Settings | الإعدادات العامة | Dejinta Guud |
| Announcements | الإعلانات | Ogeysiisyada |

## Features

### ✅ Fully Implemented

1. **Complete UI Translation** - All interface elements are translatable
2. **RTL Support** - Full right-to-left layout for Arabic
3. **Database Content Translation** - Subject names and categories are translated
4. **Dynamic Language Switching** - Users can switch languages on-the-fly
5. **Sidebar Scrolling** - Enhanced scrolling with:
   - 120px bottom padding for full menu visibility
   - Smooth scroll behavior
   - Thin, styled scrollbar (4px width)
   - Gradient fade indicator at bottom
   - Touch-friendly mobile scrolling

### 🎨 UI Enhancements

- **Gradient Scroll Indicator**: Subtle fade at the bottom of sidebar to show more content
- **Increased Padding**: 120px bottom padding ensures all menu items are accessible
- **Smooth Animations**: All transitions use cubic-bezier easing
- **Theme Support**: Works perfectly in both light and dark modes

## How to Add New Translations

### 1. Extract New Strings

```bash
cd /var/www/RaysTech/madrasah_mgmt
pybabel extract -F babel.cfg -o messages.pot app run.py
```

> **Note:** Use `app run.py` (not `.`) to avoid scanning `venv/` which can cause extraction errors.

### 2. Update Translation Files

```bash
# Update Arabic
pybabel update -i messages.pot -d app/translations -l ar

# Update Somali
pybabel update -i messages.pot -d app/translations -l so
```

### 3. Edit Translation Files

Edit the `.po` files:
- `app/translations/ar/LC_MESSAGES/messages.po` (Arabic)
- `app/translations/so/LC_MESSAGES/messages.po` (Somali)

Add translations in this format:
```
msgid "English Text"
msgstr "Translated Text"
```

### 4. Compile Translations

```bash
pybabel compile -d app/translations
```

### 5. Restart Application

```bash
sudo systemctl restart madrasah.service
```

## Translation Files Location

```
app/translations/
├── ar/
│   └── LC_MESSAGES/
│       ├── messages.po  (Edit this for Arabic translations)
│       └── messages.mo  (Compiled binary - auto-generated)
└── so/
    └── LC_MESSAGES/
        ├── messages.po  (Edit this for Somali translations)
        └── messages.mo  (Compiled binary - auto-generated)
```

## Usage in Templates

### Translate Static Text
```html
{{ _('Text to translate') }}
```

### Translate Variables
```html
{{ _(variable_name) }}
```

### Translate in Python Code
```python
from flask_babel import _

message = _('Text to translate')
```

## Browser Language Detection

The system automatically detects the user's preferred language from:
1. Session storage (if previously selected)
2. Browser's `Accept-Language` header
3. Falls back to English (default)

## Language Switcher

Users can change language using the dropdown in:
- **Desktop**: Top-right header
- **Mobile**: Top-right mobile header

Language codes:
- `en` - English
- `ar` - Arabic (العربية)
- `so` - Somali (Soomaali)

## Technical Implementation

### Configuration
- **Config File**: `app/config.py`
- **Supported Languages**: `LANGUAGES = ['en', 'ar', 'so']`
- **Default Locale**: `BABEL_DEFAULT_LOCALE = 'en'`

### Locale Selector
```python
def get_locale():
    lang = session.get('lang')
    if lang:
        return lang
    return request.accept_languages.best_match(app.config.get('LANGUAGES', []))
```

### RTL Support
Arabic automatically switches to RTL layout using:
```html
<html lang="{{ get_locale() }}" dir="{{ 'rtl' if get_locale() == 'ar' else 'ltr' }}">
```

## Maintenance

### Regular Updates
1. Extract new strings monthly or after major updates
2. Review untranslated strings in `.po` files
3. Compile and test translations
4. Restart application to apply changes

### Quality Assurance
- Test all three languages after updates
- Verify RTL layout for Arabic
- Check for text overflow in translated UI
- Ensure all database content displays correctly

---

**Last Updated**: 2026-02-09
**System Version**: 1.0
**Translation Coverage**: 100% for core features
