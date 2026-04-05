import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.setting import SystemSetting

app = create_app()
with app.app_context():
    phone_id = SystemSetting.get_setting('whatsapp_phone_number_id')
    print(f"Current WhatsApp Phone Number ID in DB: {phone_id}")
