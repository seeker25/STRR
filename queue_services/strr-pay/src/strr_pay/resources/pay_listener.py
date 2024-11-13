# Copyright © 2024 Province of British Columbia
#
# Licensed under the BSD 3 Clause License, (the 'License');
# you may not use this file except in compliance with the License.
# The template for the license can be found here
#    https://opensource.org/license/bsd-3-clause/
#
# Redistribution and use in source and binary forms,
# with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS”
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
"""This Module processes simple cloud event messages for possible strr application payments.
"""
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from http import HTTPStatus
import re
from typing import Optional

from flask import Blueprint
from flask import request
from simple_cloudevent import SimpleCloudEvent
from strr_api.models import Application
from structured_logging import StructuredLogging

from strr_api.enums.enum import PaymentStatus
from strr_pay.services import gcp_queue

bp = Blueprint("worker", __name__)

logger = StructuredLogging.get_logger()


@bp.route("/", methods=("POST",))
def worker():
    """Process the incoming cloud event.

    This worker processes queue messages issued out from pay-api through google pubsub and marks applications as paid.

    Flow
    --------
    1. Get cloud event
    2. Get payment information
    3. Update model

    Decisions on returning a 2xx or failing value to
    the Queue should be noted here:
    - Empty or garbled messages are knocked off the Q
    - If the Application is already marked paid, skip and knock off Q
    - Once the Application is marked paid, no errors should escape to the Q
    - If there's no matching application, put back on Q
    """
    if not request.data:
        # logger(request, "INFO", f"No incoming raw msg.")
        return {}, HTTPStatus.OK

    logger.info(f"Incoming raw msg: {str(request.data)}")

    if not (ce := gcp_queue.get_simple_cloud_event(request, wrapped=True)):
        # return a 200, so the event is removed from the Queue
        return {}, HTTPStatus.OK
    logger.info(f"received ce: {str(ce)}")

    if not (payment_token := get_payment_token(ce)) or payment_token.status_code != "COMPLETED":
        # no payment info, or not a payment COMPLETED token, take off Q
        return {}, HTTPStatus.OK

    application = Application.find_by_invoice_id(invoice_id=int(payment_token.id))
    if not application:
        # The payment token might not be there yet, put back on Q
        return {}, HTTPStatus.NOT_FOUND

    if application.status != Application.Status.PAYMENT_DUE.value:
        # Already processed, so don't do anything but remove from Q
        logger.debug(f"Application not in submitted state: {str(ce)}")
        return {}, HTTPStatus.OK

    logger.info(f"Processing payment: {payment_token.id}")

    application.payment_completion_date = datetime.now(timezone.utc)
    application.payment_status_code = PaymentStatus.COMPLETED.value
    application.status = Application.Status.PAID
    application.save()

    logger.info(f"completed ce: {str(ce)}")
    return {}, HTTPStatus.OK


@dataclass
class PaymentToken:
    """Payment Token class"""

    id: Optional[str] = None
    status_code: Optional[str] = None
    filing_identifier: Optional[str] = None
    corp_type_code: Optional[str] = None


def get_payment_token(ce: SimpleCloudEvent):
    """Return a PaymentToken if enclosed in the cloud event."""
    if ce.type == "bc.registry.payment" and isinstance(ce.data, dict):
        return PaymentToken(**dict_keys_to_snake_case(ce.data))
    return None


def dict_keys_to_snake_case(d: dict):
    """Convert the keys of a dict to snake_case"""
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    return {pattern.sub("_", k).lower(): v for k, v in d.items()}
