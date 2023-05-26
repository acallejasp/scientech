from odoo import models, fields
import threading

import requests
import json

import sys
import requests
import json
import logging
import time

from odoo.exceptions import UserError


class EntelSMS(models.Model):
    _inherit = 'sms.sms'

    error_message = fields.Text('Error Message', copy=False, readonly=1)

    def send(self, delete_all=False, auto_commit=False, raise_exception=False):
        """ Main API method to send SMS.

          :param delete_all: delete all SMS (sent or not); otherwise delete only
            sent SMS;
          :param auto_commit: commit after each batch of SMS;
          :param raise_exception: raise if there is an issue contacting IAP;
        """
        for batch_ids in self._split_batch():
            self.browse(batch_ids).entelocean_send_sms()
            # auto-commit if asked except in testing mode

            if auto_commit is True and not getattr(threading.currentThread(), 'testing', False):
                self._cr.commit()

    def entelocean_sms_token(self, server_url, client_id, client_secret):
        auth_server_url = server_url + 'oauth2/token'
        token_req_payload = {'grant_type': 'client_credentials'}
        requests.packages.urllib3.disable_warnings()
        token_response = requests.post(auth_server_url, data=token_req_payload, verify=False, allow_redirects=False, auth=(client_id, client_secret))
        if token_response.status_code !=200:
            raise UserError(_("Server error"))
        tokens = json.loads(token_response.text)
        return tokens['access_token']

    def entelocean_sms_api(self, auth_server_url, phone,name, msg, token):
        headers = {
              'Authorization': 'Bearer %s' %token,
              'Content-Type': 'application/json'
            }
        url = auth_server_url + "api/sms-channel/send-sms"
        payload = json.dumps({
              "campaign": {
                "name": "SMS ENTEL TEST",
                "type_campaign_id": "2577",
                "type_action": "1",
                "registers": [
                  {
                    "id": "1",
                    "name": name,
                    "phone": phone,
                    "message": msg,
                  }
                ]
              }
            })
        requests.packages.urllib3.disable_warnings()
        response = requests.request("POST", url, headers=headers, data=payload)
        return response


    def entelocean_send_sms(self, delete_all=False, raise_exception=False):
        # todo: fix send sms option

        param_obj = self.env['ir.config_parameter']
        auth_server_url = param_obj.sudo().get_param('entelocean_sms_gateway.auth_server_url')
        client_id = param_obj.sudo().get_param('entelocean_sms_gateway.client_id')
        client_secret = param_obj.sudo().get_param('entelocean_sms_gateway.client_secret')

        token = self.entelocean_sms_token(auth_server_url, client_id, client_secret)
        for rec in self:
            phone = rec.partner_id.phone if rec.partner_id else rec.number
            name = rec.partner_id.name if rec.partner_id else ''
            msg = rec.body
            try:
                client = self.entelocean_sms_api(auth_server_url, phone,name, msg, token)
                if  client.status_code == 401:
                    token = self.entelocean_sms_token(auth_server_url, client_id, client_secret)
                    state = 'error'
                    error_message = client.error_message
                else:
                    state = 'sent'
                    error_message = None
            except Exception as e:
                state = 'error'
                error_message = e.msg or e.__str__()
            rec.write({'error_message': error_message, 'state': state})