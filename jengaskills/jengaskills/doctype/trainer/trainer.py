# Copyright (c) 2025, Tati and contributors
# For license information, please see license.txt


import frappe
import random
import string
from frappe.model.document import Document
from jengaskills.services.utils import send_sms  # assuming your SMS helper

class Trainer(Document):

    def before_insert(self):
        # Assign default email if not provided
        if not self.email:
            if self.trainer_name:
                self.email = f"{self.trainer_name}@jengaskills.com"
            else:
                rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
                self.email = f"{rand_str}@jengaskills.com"

        # Ensure email is unique
        if frappe.db.exists("User", self.email):
            frappe.throw(f"A user with email {self.email} already exists.")

    def after_insert(self):
        try:
            password = self.create_trainer_user()
            self.send_credentials(password)
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Error creating Trainer User")
            frappe.throw(f"Trainer setup failed: {e}")

    def create_trainer_user(self):
        """Create a User with Trainer role and Trainer module profile"""
        password = ''.join(random.choices(string.digits, k=6))
        user = frappe.get_doc({
            "doctype": "User",
            "email": self.email,
            "first_name": self.trainer_name,
            "mobile_no": self.mobile_no,
            "enabled": 1,
            "new_password": password,
            "send_welcome_email": 1,
            "roles": [{"role": "Trainer"}],
            "module_profile": "Trainer",
            "ignore_password_policy": 1
        })
        user.insert(ignore_permissions=True)
        frappe.db.commit()
        return password

    def send_credentials(self, password):
        """Send login credentials via email and SMS"""
        message = (
            f"Welcome {self.trainer_name}, your Trainer account has been created.\n"
            f"Login Email: {self.email}\nPassword: {password}\n"
            f"Please change your password on first login."
        )

        # SMS (enqueue for async)
        # if self.mobile_no:
        #     frappe.enqueue(
        #         send_sms,
        #         queue="default",
        #         phone_number=self.mobile_no,
        #         message=message,
        #         now=False
        #     )

        # Email (send via Frappe email system)
        frappe.sendmail(
            recipients=[self.email],
            subject="Your Trainer Account Credentials",
            message=message
        )
