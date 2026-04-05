import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.setting import SystemSetting

app = create_app()
with app.app_context():
    # Correct Phone Number ID from your screenshot
    correct_phone_id = "899875649886643"
    SystemSetting.set_setting('whatsapp_phone_number_id', correct_phone_id)
    print(f"WhatsApp Phone Number ID has been corrected to: {correct_phone_id}")
