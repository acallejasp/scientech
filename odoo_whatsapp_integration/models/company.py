from odoo import models, fields, api, _

class Company(models.Model):
    _inherit = 'res.company'

    graph_api_url = fields.Char(default='https://graph.facebook.com/v15.0/')
    graph_api_instance = fields.Char()
    graph_api_bussiness = fields.Char()
    graph_api_token = fields.Char()
    status = fields.Selection([('inactive','Inactive'),('active','Activated')], default='inactive')
