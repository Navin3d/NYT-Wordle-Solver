import pywhatkit as pwk
import time

def send_whatsapp_message(message: str, contacts: list, delay: float = 5.0):
    """
    Send a WhatsApp message to a list of contacts.

    Args:
        message (str): The text message to send.
        contacts (list): List of phone numbers in full international format (e.g., "+919876543210").
        delay (float): Delay in seconds between messages.
    """
    for phone in contacts:
        try:
            print(f"Sending to {phone}...")
            # Send message now (no schedule)
            pwk.sendwhatmsg_instantly(
                phone_no=phone,
                message=message,
                wait_time=10,   # Wait for WhatsApp Web to load
                tab_close=True # Keep browser open
            )
            time.sleep(delay)  # Wait before next contact
        except Exception as e:
            print(f"Failed to send to {phone}: {e}")


if __name__ == "__main__":
    msg_text = "Hello from Python! This is an automated WhatsApp message."
    contact_list = [
        "+919442807217",  # Replace with actual numbers
        # Add more numbers as needed
    ]
    send_whatsapp_message(msg_text, contact_list, delay=0)