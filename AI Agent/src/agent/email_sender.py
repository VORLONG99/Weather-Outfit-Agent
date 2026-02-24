from __future__ import annotations

import smtplib
from email.mime.text import MIMEText


class EmailSender:
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        smtp_from: str,
    ) -> None:
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.smtp_from = smtp_from

    def send(self, to_email: str, subject: str, body: str) -> None:
        msg = MIMEText(body, _subtype="plain", _charset="utf-8")
        msg["Subject"] = subject
        msg["From"] = self.smtp_from
        msg["To"] = to_email

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.smtp_from, [to_email], msg.as_string())
