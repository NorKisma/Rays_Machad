import openai
from flask import current_app

class NotificationBot:
    def __init__(self):
        self.api_key = current_app.config.get('AI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key

    def generate_monthly_report(self, parent_name, student_name, data):
        """
        Generate a comprehensive monthly report message for parents.
        data dict: {
            'month': str,
            'attendance': float,
            'juz': int,
            'surah': str,
            'fee_status': str,
            'balance': float,
            'lang': str
        }
        """
        month = data.get('month', 'this month')
        attendance = data.get('attendance', 0)
        juz = data.get('juz', 1)
        surah = data.get('surah', 'N/A')
        fee_status = data.get('fee_status', 'Unpaid')
        balance = data.get('balance', 0)
        lang = data.get('lang', 'en')

        if not self.api_key:
            from app.models.setting import SystemSetting
            rays_machad_name = SystemSetting.get_setting('rays_machad_name', 'Rays Tech Center')
            rays_machad_phone = SystemSetting.get_setting('rays_machad_phone', '617...')
            
            # High-quality Fallback Template
            if lang == 'so':
                return (f"Assalamu Calaykum {parent_name},\n\n"
                        f"Waxaan halkaan ku soo gudbinaynaa warbixinta bisha {month} ee ardayga {student_name}:\n\n"
                        f"Joogitaanka (Attendance): {attendance}%\n"
                        f"Hifdinta Qur’aanka: Juz {juz} ({surah})\n"
                        f"Xaaladda Lacagta: {fee_status} (Lacag harsan: ${balance})\n\n"
                        f"Fadlan lacagta bisha soo bixi kuna soo dir Tel: {rays_machad_phone},\n"
                        f"nala soo socodsii marka aad bixiso.\n\n"
                        f"Mahadsanid.\n"
                        f"{rays_machad_name}")
            elif lang == 'ar':
                return (f"السلام عليكم {parent_name}، إليكم تقرير شهر {month} للطالب {student_name}.\n"
                        f"- الحضور: {attendance}%\n"
                        f"- التقدم في الحفظ: جزء {juz} ({surah})\n"
                        f"- الحالة المالية: {fee_status} (${balance})\n"
                        f"شكراً لكم، Rays Tech Center.")
            return (f"Assalamu Alaykum {parent_name}, here is the monthly report for {month} for student {student_name}.\n"
                    f"- Attendance: {attendance}%\n"
                    f"- Hifz Progress: Juz {juz} ({surah})\n"
                    f"- Financial Status: {fee_status} (Balance: ${balance})\n"
                    f"Thank you, Rays Tech Center.")

        prompt = (f"Act as a professional Rays Machad administrator. Generate a warm, personalized monthly report message "
                  f"for parent {parent_name} regarding their child {student_name} for the month of {month}. "
                  f"Include: Attendance {attendance}%, Hifz Progress (Juz {juz}, last surah {surah}), "
                  f"and Fee Status ({fee_status}, Outstanding Balance: ${balance}). "
                  f"Keep it concise for WhatsApp. Language: {lang}.")

        try:
            # Simple mock for now since we don't have the client initialized
            return f"Assalamu Alaykum {parent_name}, we are pleased to share {student_name}'s progress for {month}... (AI Generated)"
        except Exception as e:
            return f"Report for {student_name} - {month}"

    def generate_progress_update(self, parent_name, student_name, juz, surah, aya, lang='en'):
        """
        Generate a warm progress update message for parents.
        """
        from app.models.setting import SystemSetting
        rays_machad_name = SystemSetting.get_setting('rays_machad_name', 'Rays Tech Center')
        
        if lang == 'so':
             return (f"Assalamu Calaykum {parent_name},\n\n"
                    f"Waxaan kuugu farxinaynaa horumarka ardayga {student_name} ee barashada Qur'aanka.\n\n"
                    f"📌 Juzka: {juz}\n"
                    f"📖 Suurada: {surah}\n"
                    f"✨ Ayada: {aya}\n\n"
                    f"Allaah ha u barakeeyo cilmiga, hana ka dhigo kii ku intifaaca. Aamiin.\n\n"
                    f"Mahadsanid,\n"
                    f"{rays_machad_name}")
                    
        return (f"Assalamu Alaykum {parent_name},\n\n"
                f"We are pleased to share {student_name}'s progress in Quranic studies.\n\n"
                f"📌 Juz: {juz}\n"
                f"📖 Surah: {surah}\n"
                f"✨ Aya: {aya}\n\n"
                f"May Allah bless them with knowledge and wisdom. Ameen.\n\n"
                f"Best regards,\n"
                f"{rays_machad_name}")

    def generate_fee_reminder(self, parent_name, student_name, month, balance, lang='en'):
        """
        Generate a polite fee reminder message.
        """
        from app.models.setting import SystemSetting
        rays_machad_name = SystemSetting.get_setting('rays_machad_name', 'Rays Tech Center')
        rays_machad_phone = SystemSetting.get_setting('rays_machad_phone', '')

        if lang == 'so':
            return (f"Assalamu Calaykum {parent_name},\n\n"
                    f"Kani waa xasuusin ku saabsan lacagta bisha {month} ee ardayga {student_name}.\n\n"
                    f"💰 Lacagta hartay: ${balance}\n\n"
                    f"Fadlan lacagta ku soo dir Tel: {rays_machad_phone}.\n"
                    f"Haddii aad bixisay, fadlan iska ilow farriintan.\n\n"
                    f"Mahadsanid,\n"
                    f"{rays_machad_name}")
                    
        return (f"Assalamu Alaykum {parent_name},\n\n"
                f"This is a friendly reminder regarding the fees for {month} for {student_name}.\n\n"
                f"💰 Balance Due: ${balance}\n\n"
                f"Please make the payment to: {rays_machad_phone}.\n"
                f"If you have already paid, please ignore this message.\n\n"
                f"Thank you,\n"
                f"{rays_machad_name}")

    def suggest_notifications(self, user_activity):
        """
        Suggest notifications to send based on user activity/inactivity.
        """
        return []
