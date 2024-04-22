import smtplib
from .utilities import notify_vna_operator_of_new_task
from email.mime.text import MIMEText
from django.core.mail import send_mail

def send_email_notification(subject, message, recipient_email):
    # Example function to send email notification
    sender_email = 'your_email@example.com'  # Update with your sender email
    smtp_server = 'smtp.example.com'  # Update with your SMTP server

    # Create a MIMEText object with the message content
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    # Connect to the SMTP server
    with smtplib.SMTP(smtp_server) as server:
        # Send the email
        server.sendmail(sender_email, [recipient_email], msg.as_string())

def send_urgent_notification(location):
    # Logic for sending urgent notifications based on location status
    
    if location.status == 'low_stock':
        send_email_notification("Low Stock Notification", f"Low stock for location {location.id}", "recipient@example.com")
    
    elif location.status == 'urgent_replenish':
        send_email_notification("Replenishment Notification", f"Replenishment needed for location {location.id}", "recipient@example.com")
    
    elif location.status == 'urgent_pick':
        send_email_notification("Urgent Picking Notification", f"Urgent picking required for location {location.id}", "recipient@example.com")
    
    else:
        # Handle other status cases or do nothing
        pass
    
def send_verification_required_notification(location):
    # Logic for sending a verification required notification based on location status
    
    if not location:
        return  # Return if location is empty
    
    if location.status == 'vor':
        send_email_notification("Verification Required Notification", f"Verification required for location {location.id}", "recipient@example.com")
    
    elif location.status == 'weight_mismatch':
        send_email_notification("Weight Mismatch Notification", f"Weight mismatch for location {location.id}", "recipient@example.com")
    
    elif location.status == 'faulty_sensor':
        send_email_notification("Faulty Sensor Notification", f"Faulty sensor for location {location.id}", "recipient@example.com")
    
    else:
        # Handle other status cases or do nothing
        pass
    
def send_email_notification(subject, message, recipient_email):
    # Existing email sending logic
    send_mail(
        subject,
        message,
        'from@example.com',
        [recipient_email],
        fail_silently=False,
    )

def send_realtime_notification_to_vna(operator, task):
    """
    Send a real-time task notification to a VNA operator.
    This function is an entry point for sending notifications through different channels (e.g., email, WebSocket).
    
    :param operator: The operator to notify.
    :param task: The task details to send.
    """
    # Assuming operator has an email and you want to send both email and real-time notification
    email_subject = f"New VNA Task Assigned: {task.inbound.product.name}"
    email_body = f"You have been assigned a new VNA task for {task.inbound.product.name} to be putaway to {task.final_location}. Please check your RDT for more details."
    send_email_notification(email_subject, email_body, operator.email)
    
    # Send real-time notification
    notify_vna_operator_of_new_task(operator, task)