from odoo import models, fields, api, _
import requests
import json

from odoo.exceptions import UserError


class SendContactMessage(models.TransientModel):
    _name = 'whatsapp.wizard.contact'

    user_id = fields.Many2one('res.partner', string="Recipient Name", default=lambda self: self.env[self._context.get('active_model')].browse(self.env.context.get('active_ids')))
    mobile_number = fields.Char(related='user_id.mobile', required=True)
    message = fields.Text(string="Message", required=True)
    origin = fields.Char(default=lambda self: self.env[self._context.get('active_model')].browse(self.env.context.get('active_ids')).name)


    def send_custom_contact_message(self):
        ACCESS_TOKEN = self.env['res.company'].browse(1).graph_api_token
        graph_api_url = self.env['res.company'].browse(1).graph_api_url
        graph_api_instance = self.env['res.company'].browse(1).graph_api_instance
        graph_api_bussiness = self.env['res.company'].browse(1).graph_api_bussiness
        headers = {
            'Authorization': 'Bearer '+ ACCESS_TOKEN,
            'Content-Type': 'application/json',
        }
        if self.message:
            message_string = self.message
            if not self.user_id.mobile[0] == "+":
                raise UserError("Mobile nos should begins with +.")
            TO_PHONE_NUMBER = self.user_id.mobile[1:]
            data = json.dumps({ "messaging_product": "whatsapp",
                     "to": TO_PHONE_NUMBER,
                      "type": "text", 
                      "text": { "body": str(message_string) } })
            url = '%s/%s/%s' % (graph_api_url, graph_api_instance, 'messages')
            response = requests.post(url, headers=headers, data=data)
            if response:
                self.env['whatsapp.history'].create({
                                'user_id': self.user_id.id,
                                'mobile_number': TO_PHONE_NUMBER,
                                'message': message_string,
                                'status': 'success',
                               'origin': self.origin,
                        })
            model_id = self.env[self._context.get('active_model')].browse(self.env.context.get('active_ids'))
                # body = '%d Debit note(s) created' % debit_count
            model_id.message_post(body=message_string)
            