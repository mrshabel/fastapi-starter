import smtplib
from fastapi.logger import logger
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.core.config import AppConfig


def send_email(
    recipient: str,
    subject: str,
    content: str,
):
    """
    Send an email to the recipient

    Parameters:
        recipient (str): the recipient to the email
        subject (str): the subject of the email
        content (str): the email content as plaintext or html string
    """
    message = MIMEMultipart()

    message["From"] = f"Shabel.io <{AppConfig.SMTP_USERNAME}>"
    message["To"] = recipient
    message["Subject"] = subject

    message.attach(MIMEText(content, "html"))

    try:
        with smtplib.SMTP(AppConfig.SMTP_SERVER, AppConfig.SMTP_PORT) as server:
            # send 'server hello' to initiate connection
            server.ehlo()
            # setup tls for encrypted security
            server.starttls()
            # login to mail account
            server.login(AppConfig.SMTP_USERNAME, AppConfig.SMTP_PASSWORD)

            server.sendmail(
                from_addr=AppConfig.SMTP_USERNAME,
                to_addrs=recipient,
                msg=message.as_string(),
            )

            logger.info("Email delivered to recipient")

    except smtplib.SMTPAuthenticationError:
        logger.error(msg="Incorrect email or password", exc_info=True)
        raise
    except smtplib.SMTPConnectError:
        logger.error(
            msg="Failed to establish connection with smtp server",
            exc_info=True,
        )
        raise
    except smtplib.SMTPException:
        logger.error(msg="SMTP error", exc_info=True)
        raise
    except Exception as e:
        logger.error(msg=f"Failed to send email.\nError: {str(e)}")
        raise
