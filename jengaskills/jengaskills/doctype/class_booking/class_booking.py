# # Copyright (c) 2025, Tati and contributors
# # For license information, please see license.txt

# from datetime import datetime, timedelta, time
# import frappe
# from frappe.model.document import Document

# class ClassBooking(Document):
#     def before_save(self):
#         # Generate sessions automatically when saving
#         generate_class_sessions(self)


# def parse_time(t):
#     """
#     Convert string or timedelta to datetime.time object
#     """
#     if isinstance(t, str):
#         return datetime.strptime(t, "%H:%M:%S").time()
#     elif isinstance(t, timedelta):
#         # Convert timedelta to time
#         total_seconds = t.total_seconds()
#         hours = int(total_seconds // 3600)
#         minutes = int((total_seconds % 3600) // 60)
#         seconds = int(total_seconds % 60)
#         return time(hour=hours, minute=minutes, second=seconds)
#     elif isinstance(t, time):
#         return t
#     else:
#         frappe.throw(f"Invalid time format: {t}")


# def generate_class_sessions(doc):
#     if doc.sessions_generated:
#         return  # Avoid duplicate generation

#     # 1. Convert fetched fields to proper numeric types
#     hours_per_session = float(doc.hours_per_session or 0)
#     total_course_hours = float(doc.total_course_hours or 0)
#     number_of_sessions = int(doc.number_of_sessions or 0)

#     if number_of_sessions <= 0 or hours_per_session <= 0:
#         frappe.throw("Invalid number of sessions or hours per session.")

#     # 2. Fetch trainer availability
#     trainer_doc = frappe.get_doc("Trainer", doc.trainer)
#     trainer_slots = [
#         {
#             "day": slot.day,
#             "start_time": parse_time(slot.from_time),
#             "end_time": parse_time(slot.to_time),
#             "location_type": slot.location_type,
#             "location_address": slot.location_address
#         } 
#         for slot in trainer_doc.get("availability_schedule")
#     ]

#     # 3. Fetch student availability
#     student_slots = [
#         {
#             "day": slot.days,
#             "start_time": parse_time(slot.start_time),
#             "end_time": parse_time(slot.end_time)
#         }
#         for slot in doc.get("student_availability")
#     ]

#     # 4. Generate sessions
#     sessions_created = 0
#     current_date = datetime.today()

#     while sessions_created < number_of_sessions:
#         weekday = current_date.strftime("%A")

#         # Filter slots for this weekday
#         student_day_slots = [s for s in student_slots if s["day"] == weekday]
#         trainer_day_slots = [t for t in trainer_slots if t["day"] == weekday and t["location_type"] == doc.class_type]

#         for s_slot in student_day_slots:
#             for t_slot in trainer_day_slots:
#                 # Compute overlapping start and end times
#                 start_dt = datetime.combine(current_date.date(), max(s_slot["start_time"], t_slot["start_time"]))
#                 end_dt = datetime.combine(current_date.date(), min(s_slot["end_time"], t_slot["end_time"]))
#                 session_length = timedelta(hours=hours_per_session)

#                 if end_dt - start_dt >= session_length:
#                     doc.append("class_session", {
#                         "session_number": sessions_created + 1,
#                         "scheduled_datetime": start_dt,
#                         "end_datetime": start_dt + session_length,
#                         "status": "Scheduled",
#                         "location": t_slot.get("location_address") if doc.class_type == "Physical" else None
#                     })
#                     sessions_created += 1
#                     if sessions_created >= number_of_sessions:
#                         break
#             if sessions_created >= number_of_sessions:
#                 break

#         current_date += timedelta(days=1)

#     # 5. Set lesson_end_date
#     if doc.class_session:
#         last_session = doc.class_session[-1]
#         doc.lesson_end_date = last_session.scheduled_datetime.date()

#     # 6. Calculate total fee
#     # Calculate fee from trainer's rate per hour * total course hours
#     if doc.class_mode == "Group Class":
#         trainer_rate = trainer_doc.rate_per_hour_group or 0
#     else:  # Personal Class
#         trainer_rate = trainer_doc.rate_per_hour_personal or 0

#     doc.fee = float(trainer_rate) * float(total_course_hours or 0)

#     # 7. Mark sessions as generated
#     doc.sessions_generated = 1




# Copyright (c) 2025, Tati and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, timedelta, time
from frappe.model.document import Document
from jengaskills.services.google_calendar import create_google_meet_event

class ClassBooking(Document):
    def before_save(self):
        # Generate sessions automatically when saving
        generate_class_sessions(self)


def parse_time(t):
    """
    Convert string or timedelta to datetime.time object
    """
    if isinstance(t, str):
        return datetime.strptime(t, "%H:%M:%S").time()
    elif isinstance(t, timedelta):
        total_seconds = t.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        return time(hour=hours, minute=minutes, second=seconds)
    elif isinstance(t, time):
        return t
    else:
        frappe.throw(f"Invalid time format: {t}")


def generate_class_sessions(doc):
    if doc.sessions_generated:
        return  # Avoid duplicate generation

    hours_per_session = float(doc.hours_per_session or 0)
    total_course_hours = float(doc.total_course_hours or 0)
    number_of_sessions = int(doc.number_of_sessions or 0)

    if number_of_sessions <= 0 or hours_per_session <= 0:
        frappe.throw("Invalid number of sessions or hours per session.")

    trainer_doc = frappe.get_doc("Trainer", doc.trainer)
    trainer_slots = [
        {
            "day": slot.day,
            "start_time": parse_time(slot.from_time),
            "end_time": parse_time(slot.to_time),
            "location_type": slot.location_type,
            "location_address": slot.location_address
        } 
        for slot in trainer_doc.get("availability_schedule")
    ]

    student_slots = [
        {
            "day": slot.days,
            "start_time": parse_time(slot.start_time),
            "end_time": parse_time(slot.end_time)
        }
        for slot in doc.get("student_availability")
    ]

    sessions_created = 0
    current_date = datetime.today()

    while sessions_created < number_of_sessions:
        weekday = current_date.strftime("%A")

        student_day_slots = [s for s in student_slots if s["day"] == weekday]
        trainer_day_slots = [t for t in trainer_slots if t["day"] == weekday and t["location_type"] == doc.class_type]

        for s_slot in student_day_slots:
            for t_slot in trainer_day_slots:
                start_dt = datetime.combine(current_date.date(), max(s_slot["start_time"], t_slot["start_time"]))
                end_dt = datetime.combine(current_date.date(), min(s_slot["end_time"], t_slot["end_time"]))
                session_length = timedelta(hours=hours_per_session)

                if end_dt - start_dt >= session_length:
                    meet_link = None

                    if doc.class_type == "Online":
                        attendees = []
                        # Optionally, add student/trainer emails if stored
                        if hasattr(trainer_doc, "email"):
                            attendees.append({"email": trainer_doc.email})
                        student_doc = frappe.get_doc("Student", doc.student)
                        if hasattr(student_doc, "email"):
                            attendees.append({"email": student_doc.email})

                        _, meet_link = create_google_meet_event(
                            summary=f"{doc.skill} Session {sessions_created + 1}",
                            start_time=start_dt,
                            end_time=start_dt + session_length,
                            attendees=attendees
                        )

                    doc.append("class_session", {
                        "session_number": sessions_created + 1,
                        "scheduled_datetime": start_dt,
                        "end_datetime": start_dt + session_length,
                        "status": "Scheduled",
                        "location": (
                            t_slot.get("location_address") 
                            if doc.class_type == "Physical" 
                            else meet_link
                        )
                    })

                    sessions_created += 1
                    if sessions_created >= number_of_sessions:
                        break
            if sessions_created >= number_of_sessions:
                break

        current_date += timedelta(days=1)

    # Set end date and fees
    if doc.class_session:
        last_session = doc.class_session[-1]
        doc.lesson_end_date = last_session.scheduled_datetime.date()

    if doc.class_mode == "Group Class":
        trainer_rate = trainer_doc.rate_per_hour_group or 0
    else:
        trainer_rate = trainer_doc.rate_per_hour_personal or 0

    doc.fee = float(trainer_rate) * float(total_course_hours or 0)
    doc.sessions_generated = 1
