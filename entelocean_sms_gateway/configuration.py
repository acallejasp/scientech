from odoo import fields, models, api, _


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    auth_server_url = fields.Char(
        string='Auth Server Url', default='https://api.touchapp.cl/165/'
    )
    client_id = fields.Char(default='j8yjJQdGbUFCdrT0lYzBJQQVQYQbuOGR')
    client_secret = fields.Char(default='4LNk5bG7SPNpWQKG1mRYFPLd7lMXJE34')
    
    @api.model
    def get_values(self):
        res = super(ResConfigSetting, self).get_values()
        param_obj = self.env['ir.config_parameter']
        res.update({
            'auth_server_url': param_obj.sudo().get_param('entelocean_sms_gateway.auth_server_url'),
            'client_id': param_obj.sudo().get_param('entelocean_sms_gateway.client_id'),
            # 'entelocean_from_number': param_obj.sudo().get_param('entelocean_sms_gateway.entelocean_from_number'),
            'client_secret': param_obj.sudo().get_param('entelocean_sms_gateway.client_secret'),
        })
        return res

    @api.model
    def set_values(self):
        super(ResConfigSetting, self).set_values()
        param_obj = self.env['ir.config_parameter']
        param_obj.sudo().set_param('entelocean_sms_gateway.auth_server_url', self.auth_server_url)
        param_obj.sudo().set_param('entelocean_sms_gateway.client_id', self.client_id)
        # param_obj.sudo().set_param('entelocean_sms_gateway.entelocean_from_number', self.entelocean_from_number)
        param_obj.sudo().set_param('entelocean_sms_gateway.client_secret', self.client_secret)