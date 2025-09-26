import frappe
import requests
import calendar
from datetime import datetime


import africastalking
import requests
import frappe


def format_mobile_number(mobile):
    """
    Convert mobile to international format assuming Kenya (+254).
    Example: '0746774389' -> '+254746774389'
    """
    if mobile.startswith('0'):
        return '+254' + mobile[1:]
    elif mobile.startswith('+'):
        return mobile  # already international format
    else:
        return '+254' + mobile
    
def format_mobile_number_stk(mobile_number):
    mobile_number = str(mobile_number).strip()

    if mobile_number.startswith("+"):
        mobile_number = mobile_number[1:]
    if mobile_number.startswith("0"):
        mobile_number = "254" + mobile_number[1:]
    elif mobile_number.startswith("7") and len(mobile_number) == 9:
        mobile_number = "254" + mobile_number
    return mobile_number



@frappe.whitelist(allow_guest=True)
def send_sms(message, site_name, mobile):
    try:
        sms_config = frappe.get_all(
            "SMS Configurations",
            filters={"site_name": site_name, "sms_company": "africastalking"},
            fields=["username", "api_key", "sender_id"]
        )

        if not sms_config:
            return {"status": "failed", "error": f"No Africa's Talking SMS configuration found for site: {site_name}"}

        config = sms_config[0]

        # Convert mobile to international format (assumes Kenya country code +254)
        # # Example: input '0746774389' => output '+254746774389'
        # if mobile.startswith('0'):
        #     mobile = '+254' + mobile[1:]
        # elif mobile.startswith('+'):
        #     pass  # assume already international format
        # else:
        #     # You can add other cases if needed
        #     mobile = '+254' + mobile
        mobile = format_mobile_number(mobile)

        print("\nSending SMS to:", mobile)

        # Initialize Africa's Talking
        africastalking.initialize(config["username"], config["api_key"])
        sms = africastalking.SMS
        recipients = [mobile]

        # Send the message
        response = sms.send(message, recipients, config["sender_id"])
        message_objects = response['SMSMessageData']['Recipients']

        # Save message status
        for message_object in message_objects:
            message_status = frappe.get_doc({
                "doctype": "Message Status",
                "cost": message_object.get('cost'),
                "message_id": message_object.get('messageId'),
                "pages": message_object.get('messageParts'),
                "mobile_number": message_object.get('number'),
                "status": message_object.get('status'),
                "status_code": message_object.get('statusCode'),
                "message_sent": message
            })
            message_status.insert(ignore_permissions=True)

        frappe.db.commit()
        return {"status": "Message sent successfully", "details": response}

    except Exception as e:
        frappe.log_error(message=frappe.get_traceback(), title="SMS Sending Error")
        return {"error": str(e)}, 400
