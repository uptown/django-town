# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import time
# from gcm import GCM
from gcm.gcm import GCMNotRegisteredException, GCMUnavailableException
from apns import APNs, Payload, Frame
from django_town.social.models.device import ApplePushNotification


def push_notification_raw_apple(apns, token_hex, payload):
    apns.gateway_server.send_notification(token_hex, Payload(**payload))


def push_notification_multi_raw_apple(apns, tokens_hex, payload=None, payloads=None):
    frame = Frame()
    identifier = 1
    expiry = time.time() + 3600
    priority = 10
    if payload:
        for token in tokens_hex:
            frame.add_item(token, Payload(**payload), identifier, expiry, priority)
    else:
        for token, payload in tokens_hex, payloads:
            frame.add_item(token, Payload(**payload), identifier, expiry, priority)
    apns.gateway_server.send_notification_multiple(frame)
    # Get feedback messages
    for (token_hex, fail_time) in apns.feedback_server.items():
        # do stuff with token_hex and fail_time
        pass

def push_notification_raw_android(gcm, reg_id, data):
    try:
        gcm.plaintext_request(registration_id=reg_id, data=data)
    except GCMNotRegisteredException:
        # Remove this reg_id from database
        pass
    except GCMUnavailableException:
        # Resent the message
        pass

def push_notification_multi_raw_android(gcm, reg_ids, data):
    reg_ids = ['12', '34', '69']
    response = gcm.json_request(registration_ids=reg_ids, data=data)
    # Handling errors
    if 'errors' in response:
        for error, reg_ids in response['errors'].items():
            # Check for errors and act accordingly
            if error is 'NotRegistered':
                pass
    if 'canonical' in response:
        for reg_id, canonical_id in response['canonical'].items():
            pass


class Command(BaseCommand):

    def handle(self, *args, **options):
        data = ({
            "token": "5283dfd6fa2a59389452daf5e7c8079e02cb1b16d2f1419dd540b5218057d58d",
            "alert": {
                "loc-key": "Update 해주세요".decode('utf8'),
                "loc-args": ["Jenna", "Frank"],
                "action-loc-key": "Okay"
            },
        },)
        frame = Frame()
        identifier = 1
        expiry = time.time() + 3600
        priority = 10
        apns = APNs(use_sandbox=False, cert_file="onoo-production.pem", key_file="onoo-production-key.pem")
        for noti in data:
            frame.add_item(noti['token'], Payload(alert=noti['alert'],
            custom={"need_update": True, "update_url": "itms-services://?action=download-manifest&url=https://ios-beta-deploy.b4sunset.net/kIgGzS2BEm50TbASqOA7.inst"}
            ), identifier, expiry, priority)
        apns.gateway_server.send_notification_multiple(frame)
