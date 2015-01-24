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

        while True:
            ApplePushNotification.objects.filter(state=ApplePushNotification.NEW).update(state=ApplePushNotification.PENDING)

            frame = Frame()
            identifier = 1
            expiry = time.time() + 3600
            priority = 10
            # retry_cnt = 10
            apns = APNs(use_sandbox=False, cert_file="onoo-production.pem", key_file="onoo-production-key.pem")
            # while retry_cnt > 0:
            try:
                cnt = 0
                for noti in ApplePushNotification.objects.filter(state=ApplePushNotification.PENDING):
                    cnt += 1
                    # apns.gateway_server.send_notification(noti.device_token, Payload(alert=noti.message, badge=noti.badge_count))
                    frame.add_item(noti.device_token, Payload(alert=noti.message, sound="default", badge=noti.badge_count), identifier, expiry, priority)
                if cnt > 0:
                    apns.gateway_server.send_notification_multiple(frame)
            except:
                import traceback
                traceback.print_exc()
                ApplePushNotification.objects.filter(state=ApplePushNotification.PENDING).update(state=ApplePushNotification.NEW)
                    # retry_cnt -= 1
                    # time.sleep(1)
            # for (token_hex, fail_time) in apns.feedback_server.items():
            #         # logging 하기 ...
            #         pass

            # ApplePushNotification.objects.filter(state=ApplePushNotification.PENDING).delete()
            ApplePushNotification.objects.filter(state=ApplePushNotification.PENDING).update(state=ApplePushNotification.DONE)

            time.sleep(1)
