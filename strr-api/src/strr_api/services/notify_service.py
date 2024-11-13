from flask import current_app
from strr_api.enums.enum import AuthHeaderType, ContentType
from strr_api.services.auth_service import AuthService
from strr_api.services.rest_service import RestService


class NotifyService:
    """Service to invoke rest calls to notify-api."""

    @classmethod
    def send_email_from_service_client(cls, recipients: list[str], subject: str, body: str) -> bool:
        """Send the email notification using the service client token (for anonymous users for example)."""
        token = AuthService.get_service_client_token()
        return cls.send_email(recipients, subject, body, token)

    @classmethod
    def send_email(cls, recipients: list[str], subject: str, body: str, token) -> bool:
        """Send the email notification."""
        # Note if we send HTML in the body, we aren't sending through GCNotify
        notify_url = current_app.config.get("NOTIFY_API_ENDPOINT") + "notify/"
        current_app.logger.info(f">send_email to recipients: {recipients}")
        for recipient in recipients:
            notify_body = {
                "recipients": recipient,
                "content": {"subject": subject, "body": body},
            }

            try:
                notify_response = RestService.post(
                    notify_url,
                    token=token,
                    auth_header_type=AuthHeaderType.BEARER,
                    content_type=ContentType.JSON,
                    data=notify_body,
                )
                current_app.logger.info("<send_email notify_response")
                if notify_response:
                    current_app.logger.info(f"Successfully sent email to {recipient}")
                    return True
            except Exception as e:  # NOQA pylint:disable=broad-except
                current_app.logger.error(f"Error sending email to {recipient}: {e}")

        return False
