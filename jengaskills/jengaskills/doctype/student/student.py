# Copyright (c) 2025, Tati and contributors
# For license information, please see license.txt

from jengaskills.services.utils import send_sms
import frappe
import random
import string
from frappe.model.document import Document

class Student(Document):
    
    def before_insert(self):
        # Ensure mobile number length
        if self.mobile_no and len(self.mobile_no) > 10:
            frappe.throw("Mobile number should not be more than 10 digits.")

        # Ensure email exists
        if not self.email:
            if self.student_name:
                self.email = f"{self.student_name}@jengaskills.com"
            else:
                rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                self.email = f"{rand_str}@jengaskills.com"

        if frappe.db.exists("User", self.email):
            frappe.throw(f"A user with email {self.email} already exists.")

        # Generate registration number
        self.registration_no = self.generate_registration_no()

    def after_insert(self):
        try:
            # 1. Create Student Customer
            self.create_customer()

            # 2. Create Frappe User
            password = self.create_student_user()

            # 3. Send SMS and Email
            message = (
                f"Welcome {self.student_name}, your account has been created.\n"
                f"Login Email: {self.email}\nPassword: {password}\n"
                f"Please change your password on first login."
            )

            # Send SMS via queued job
            # frappe.enqueue(
            #     send_sms,
            #     queue="default",
            #     phone_number=self.mobile_no,
            #     message=message,
            #     now=False
            # )

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Error in creating Student records")
            frappe.throw(f"Student setup failed: {e}")

    def generate_registration_no(self):
        year = frappe.utils.now_datetime().strftime("%y")
        month = frappe.utils.now_datetime().strftime("%m")
        while True:
            digits = str(random.randint(1000, 9999))
            reg_no = f"ST{year}{month}{digits}"
            if not frappe.db.exists("Student", {"registration_no": reg_no}):
                return reg_no

    def create_customer(self):
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": self.student_name,
            "customer_group": "Individual",
            "customer_type": "Individual",
            "territory": "All Territories",
            "mobile_no": self.mobile_no,
            "email_id": self.email,
            "student_id": self.name  # optional custom field
        })
        customer.insert(ignore_permissions=True)
        frappe.db.commit()

    def create_student_user(self):
        password = str(random.randint(1000, 9999))
        user = frappe.get_doc({
            "doctype": "User",
            "email": self.email,
            "first_name": self.student_name,
            "mobile_no": self.mobile_no,
            "enabled": 1,
            "new_password": password,
            "send_welcome_email": 1,
            "roles": [{"role": "Student"}],
            "user_type": "System User",
            "module_profile": "Student",
            "ignore_password_policy": 1
        })
        user.insert(ignore_permissions=True)
        frappe.db.commit()
        return password
