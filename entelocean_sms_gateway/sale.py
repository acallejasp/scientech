from odoo import fields, models, api, _
import requests
import json

TIMEOUT = 30

from odoo.exceptions import UserError

URL = 'https://touch.entelocean.com'

class Sale(models.Model):
    _inherit = 'sale.order'

    def twilio_send_sms(self, delete_all=False, raise_exception=False):
        param_obj = self.env['ir.config_parameter']
        entelocean_email = param_obj.sudo().get_param('entelocean_sms_gateway.entelocean_email')
        entelocean_password = param_obj.sudo().get_param('entelocean_sms_gateway.entelocean_password')
        entelocean_overwrite_odoo_sms = param_obj.sudo().get_param('entelocean_sms_gateway.entelocean_overwrite_odoo_sms')
        AuthUrl = URL + '/api/auth/authenticate'
        # data = {'email': entelocean_email,'password': entelocean_password }
        data = {'email': entelocean_email,'password': entelocean_password}
        AuthResponse = requests.post(AuthUrl, json=data,timeout=TIMEOUT,headers={'Content-Type': 'application/json'})
        if AuthResponse.status_code != 200:
            raise UserError(_("Server error"))
        access_token = AuthResponse.json()['token']
        SmsUrl = URL + '/api/sms-channel/send-sms'
        params = {
            "campaign":{
                "name":"bono febrero",
                "type_campaign_id":"2340",
                "type_action":"1",
                "registers":[
                    {
                        "id":"1",
                        "name":"+56983604997",
                        "phone":"+56983604997",
                        "message":"SOLO HASTA MAÑANA Perfume de 100 ml. inspirado en Yes I am de Cacharel a  $5.990. Exclusivo para Socias de Alan Privee de Yves. Pide el tuyo al +56957125755"
                    }
                ]
            }
            }
        
        # params = 
        request = requests.post(SmsUrl, json=params,timeout=TIMEOUT, headers={'Authorization': 'Bearer %s' % access_token, 'Content-Type': 'application/json'})


        # request = requests.get(url, params=params, headers={'Authorization': 'Bearer %s' % access_token})

        # client = Client(twilio_account_sid, twilio_auth_token)

        