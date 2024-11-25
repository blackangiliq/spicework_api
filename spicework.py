import requests
from datetime import datetime
import json
import re

class SpiceworksAPI:
    def __init__(self):
        self.base_url = "https://on.spiceworks.com"
        self.auth_url = "https://accounts.spiceworks.com"
        self.session = requests.Session()
        self.csrf_token = None
        self.user_data = None

    def get_csrf_token(self):
        """الحصول على CSRF token"""
        try:
            response = self.session.get(f"{self.base_url}/tickets")
            match = re.search(r'csrf-token.*?content="(.*?)"', response.text)
            if match:
                self.csrf_token = match.group(1)
                return True
        except Exception as err:
            print(f"خطأ في الحصول على CSRF token: {err}")
        return False

    def login(self, email, password):
        """دالة تسجيل الدخول"""
        try:
            login_url = f"{self.auth_url}/api/public/v1/users/login"
            
            payload = {
                "email": email,
                "password": password,
                "policy": "hosted_help_desk"
            }
            
            response = self.session.post(login_url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            self.user_data = data['data'][0]
            
            if self.get_csrf_token():
                print("تم تسجيل الدخول والحصول على CSRF token بنجاح!")
                print("بيانات المستخدم:", json.dumps(self.user_data, indent=2, ensure_ascii=False))
                return True
            
            return False
            
        except Exception as err:
            print(f"حدث خطأ في تسجيل الدخول: {err}")
            return False

    def create_ticket(self, summary, description, assignee_id=1403152, priority=2):
        """دالة إنشاء تذكرة جديدة"""
        if not self.user_data or not self.csrf_token:
            print("يجب تسجيل الدخول أولاً!")
            return None

        url = f"{self.base_url}/api/main/tickets"
        
        # تحضير البيانات بالشكل المطلوب
        ticket_data = {
            "ticket": {
                "assignee_id": assignee_id,
                "creator_id": self.user_data.get('id'),  # استخدام ID المستخدم الحالي
                "creator_type": "User",
                "custom_values": [],
                "description": description,
                "initial_upload_ids": [],
                "organization_id": 1047306,
                "priority": priority,
                "summary": summary,
                "ticket_category_id": None
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Origin': self.base_url,
            'Referer': f"{self.base_url}/tickets",
            'X-CSRF-TOKEN': self.csrf_token
        }

        try:
            print("\nإرسال طلب إنشاء تذكرة...")
            print("URL:", url)
            print("Headers:", json.dumps(headers, indent=2))
            print("Data:", json.dumps(ticket_data, indent=2))
            
            response = self.session.post(url, json=ticket_data, headers=headers)
            print("\nStatus Code:", response.status_code)
            
            if response.text:
                print("Response Content:", json.dumps(response.json(), indent=2, ensure_ascii=False))
            
            response.raise_for_status()
            
            if response.text:
                ticket = response.json()
                print("\nتم إنشاء التذكرة بنجاح!")
                return ticket
            return None
            
        except Exception as err:
            print(f"\nحدث خطأ في إنشاء التذكرة: {err}")
            if hasattr(err, 'response') and err.response is not None:
                print("تفاصيل الخطأ:", err.response.text)
            return None

    def get_ticket_details(self, ticket_id):
        """الحصول على تفاصيل تذكرة معينة"""
        try:
            url = f"{self.base_url}/api/main/tickets/{ticket_id}"
            
            headers = {
                'Accept': 'application/json',
                'X-CSRF-TOKEN': self.csrf_token
            }

            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as err:
            print(f"حدث خطأ في الحصول على تفاصيل التذكرة: {err}")
            return None

def main():
    api = SpiceworksAPI()
    
    # معلومات تسجيل الدخول
    email = "user@gmail.com"
    password = "12345"
    
    if api.login(email, password):
        # إنشاء تذكرة جديدة
        ticket = api.create_ticket(
            summary="تجربة تذكرة جديدة",
            description="هذه تذكرة تجريبية لاختبار النظام",
            assignee_id=1403152,  # معرف الموظف المعين
            priority=2
        )
        
        if ticket:
            ticket_id = ticket.get('ticket', {}).get('id')
            if ticket_id:
                print(f"\nتم إنشاء التذكرة برقم: {ticket_id}")
                
                # الحصول على تفاصيل التذكرة
                ticket_details = api.get_ticket_details(ticket_id)
                if ticket_details:
                    print("\nتفاصيل التذكرة الكاملة:", 
                          json.dumps(ticket_details, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
