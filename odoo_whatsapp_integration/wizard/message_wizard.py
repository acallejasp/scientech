from odoo import models, fields, api, _
import html2text
import urllib.parse as parse
import json
import requests
  

class MessageError(models.TransientModel):
    _name='display.error.message'
    _description = 'History'

    def get_message(self):
        if self.env.context.get("message", False):
            return self.env.context.get('message')
        return False
    name = fields.Text(string="Message", readonly=True, default=get_message)

class SendMessage(models.TransientModel):
    _name = 'whatsapp.wizard'
    _description = 'History'

    user_id = fields.Many2one('res.partner', string="Recipient Name", default=lambda self: self.env[self._context.get('active_model')].browse(self.env.context.get('active_ids')).partner_id)
    mobile_number = fields.Char(related='user_id.mobile', required=True)
    message = fields.Text(string="Message")
    model = fields.Char('mail.template.model_id')
    template_id = fields.Many2one('mail.template', 'Use template', index=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'whatsapp_compose_message_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')
    origin = fields.Char(default=lambda self: self.env[self._context.get('active_model')].browse(self.env.context.get('active_ids')).name)

    @api.onchange('template_id')
    def onchange_template_id_wrapper(self):
        self.ensure_one()
        res_id = self._context.get('active_id') or 1
        values = self.onchange_template_id(self.template_id.id, self.model, res_id)['value']
        for fname, value in values.items():
            setattr(self, fname, value)

    def onchange_template_id(self, template_id, model, res_id):
        if template_id:
            values = self.generate_email_for_composer(template_id, [res_id])[res_id]
        else:
            default_values = self.with_context(default_model=model, default_res_id=res_id).default_get(
                ['model', 'res_id', 'partner_ids', 'message'])
            values = dict((key, default_values[key]) for key in
                          ['body', 'partner_ids']
                          if key in default_values)
        values = self._convert_to_write(values)
        return {'value': values}

    def generate_email_for_composer(self, template_id, res_ids, fields=None):
        multi_mode = True
        if isinstance(res_ids, int):
            multi_mode = False
            res_ids = [res_ids]
        if fields is None:
            fields = ['body_html']
        returned_fields = fields + ['partner_ids']
        values = dict.fromkeys(res_ids, False)
        template_values = self.env['mail.template'].with_context(tpl_partners_only=True).browse(template_id).generate_email(res_ids, fields=fields)
        for res_id in res_ids:
            res_id_values = dict((field, template_values[res_id][field]) for field in returned_fields if
                                 template_values[res_id].get(field))
            res_id_values['message'] = html2text.html2text(res_id_values.pop('body_html', ''))
            values[res_id] = res_id_values
        return multi_mode and values or values[res_ids[0]]

    def send_custom_message(self):
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
            TO_PHONE_NUMBER = self.user_id.mobile.split('+')[1]
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
            # import pdb;pdb.set_trace();
            model_id = self.env[self._context.get('active_model')].browse(self.env.context.get('active_ids'))
                # body = '%d Debit note(s) created' % debit_count
            model_id.message_post(body=message_string)
        if self.attachment_ids:
            
            # attachment = self.env['ir.attachment'].search([('res_model', '=', 'whatsapp.wizard'), ('res_id', '=', self.id)])
            for attachment in self.attachment_ids:
                
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                local_url = self.env['ir.attachment'].browse(attachment.id)
                if base_url and local_url:
                    URL = base_url + '/web/content/' + str(attachment.id) + '/' + attachment.name
                    # base_url + '/web/content/' + str(record.id) + '/example.png'
                    print (URL)

                    data = json.dumps({
                          "messaging_product": "whatsapp",
                          "recipient_type": "individual",
                          "to": TO_PHONE_NUMBER,
                          "type": "document",
                           "document": { 
                            "link": URL,
                            "filename": attachment.name,
                            }
                        })
                    url = '%s/%s/%s' % (graph_api_url, graph_api_instance, 'messages')
                    # import pdb;pdb.set_trace();
                    response = requests.post(url, headers=headers, data=data)
                    print (response)
        #     headers = {
        #     'Authorization': 'Bearer '+ ACCESS_TOKEN,
        #     'Content-Type': 'application/pdf',
        #     }
        #     import base64
        #     TO_PHONE_NUMBER = self.user_id.mobile.split('+')[1]
        #     data = json.dumps({ "messaging_product": "whatsapp",
        #              "to": TO_PHONE_NUMBER,
        #               "type": "media", 
        #               "file": base64.b64decode(self.attachment_ids.datas) })
        #     url = '%s/%s/%s' % (graph_api_url, graph_api_instance, 'media')
        #     import pdb;pdb.set_trace();
        #     response = requests.post(url, headers=headers, data=data)

            # base64.b64decode(attachment_id.datas)
