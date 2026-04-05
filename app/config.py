import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AI_API_KEY = os.environ.get('AI_API_KEY')
    MYSQLDUMP_PATH = os.environ.get('MYSQLDUMP_PATH')
    BASE_URL = os.environ.get('BASE_URL', 'https://raystechcenter.online')
    MAIN_DOMAIN = os.environ.get('MAIN_DOMAIN', 'raystechcenter.online')

    # Security Settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True') == 'True'
    SESSION_COOKIE_SAMESITE = 'Lax'
    # Important for SaaS: Do NOT set SESSION_COOKIE_DOMAIN globally unless 
    # you want users to stay logged in across subdomains. 
    # For better isolation, keep separate sessions per subdomain.
    PERMANENT_SESSION_LIFETIME = 3600 # 1 hour
    WTF_CSRF_ENABLED = True
    WTF_CSRF_CHECK_DEFAULT = True 
    WTF_CSRF_TIME_LIMIT = None # Allow tokens to last the whole session
    
    # SaaS Global Admins
    SAAS_SUPER_ADMINS = os.environ.get('SAAS_SUPER_ADMINS', 'nor.jws@gmail.com').split(',')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_DEFAULT = "60 per minute"
    
    LANGUAGES = ['en', 'ar', 'so']
    BABEL_DEFAULT_LOCALE = 'en'
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # TextBee SMS
    TEXTBEE_API_KEY = os.environ.get('TEXTBEE_API_KEY')
    TEXTBEE_DEVICE_ID = os.environ.get('TEXTBEE_DEVICE_ID')

    # WhatsApp Business API
    WHATSAPP_API_TOKEN = os.environ.get('WHATSAPP_API_TOKEN')
    WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
    WHATSAPP_VERIFY_TOKEN = os.environ.get('WHATSAPP_VERIFY_TOKEN')

    # WaafiPay (iPay) Configuration
    IPAY_MERCHANT_ID = os.environ.get('IPAY_MERCHANT_ID')
    IPAY_API_KEY = os.environ.get('IPAY_API_KEY')
    IPAY_API_USER_ID = os.environ.get('IPAY_API_USER_ID')
    
    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

