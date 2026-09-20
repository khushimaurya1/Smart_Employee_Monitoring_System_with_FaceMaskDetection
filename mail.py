import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from employee_data import COMPANY


# ==========================
# Gmail Credentials
# ==========================

EMAIL = "foreignfights247@gmail.com"

APP_PASSWORD = "jnkq kzzk xysd zedm"


# ==========================
# Send Normal Email
# ==========================

def send_email(receiver_email, employee_name):

    subject = "Mask Warning"

    body = f"""
    <h2>{COMPANY["name"]}</h2>

    <p>Dear <b>{employee_name}</b>,</p>

    <p>
    Our AI Monitoring System detected that you were
    not wearing a face mask.
    </p>

    <p>
    Please wear your mask immediately.
    </p>

    <br>

    <p>
    Thank You
    <br>
    HR Department
    </p>
    """

    return send_html_email(
        receiver_email,
        subject,
        body
    )


# ==========================
# Send HR Email
# ==========================

def send_hr_email(receiver, employee_name, warning_count, screenshot_path):

    subject = f"{employee_name} Mask Violation"

    body = f"""

    <h2>Mask Violation Report</h2>

    <p>

    Employee :

    <b>{employee_name}</b>

    </p>

    <p>

    Employee crossed warning limit.

    Screenshot Attached.

    </p>

    """

    return send_html_email(

        receiver,

        subject,

        body,

        screenshot_path

    )


# ==========================
# HTML Email Function
# ==========================

def send_html_email(

        receiver,

        subject,

        html_body,

        attachment=None

):

    try:

        message = MIMEMultipart()

        message["From"] = EMAIL

        message["To"] = receiver

        message["Subject"] = subject

        message.attach(

            MIMEText(

                html_body,

                "html"

            )

        )

        if attachment is not None:

            if os.path.exists(attachment):

                file = open(

                    attachment,

                    "rb"

                )

                part = MIMEBase(

                    "application",

                    "octet-stream"

                )

                part.set_payload(

                    file.read()

                )

                encoders.encode_base64(part)

                part.add_header(

                    "Content-Disposition",

                    f"attachment; filename={os.path.basename(attachment)}"

                )

                message.attach(part)

                file.close()

        server = smtplib.SMTP(

            "smtp.gmail.com",

            587

        )

        server.starttls()

        server.login(

            EMAIL,

            APP_PASSWORD

        )

        server.send_message(message)

        server.quit()

        print(

            "Email Sent Successfully"

        )

        return True

    except Exception as e:

        print(

            "Email Error :",

            e

        )
        return False