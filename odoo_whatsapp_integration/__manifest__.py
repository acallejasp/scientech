{
    'name': "Whatsapp Odoo Integration",
    'summary': """
        This module allows you to send whatsapp messages about the sale orders, purchase orders, 
        invoice order amount, and delivery orders along with order items to the respective user.""",

    'description': """
    """,
    'author': "bhavit.odoo@gmail.com",
    'website': "bhavit.odoo@gmail.com",
    'category': 'Whatsapp',
    'version': '1.0',
    'license': 'LGPL-3',
    'depends': ['base', 'sale', 'web', 'stock', 'purchase','account','contacts','crm'],
    'data': [
        'security/ir.model.access.csv',
        'security/sms_security.xml',
        'views/views.xml',
        'views/template.xml',
        'views/setting_inherit_view.xml',
        'wizard/message_wizard.xml',
        'wizard/wizard.xml',
        'wizard/wizard_contact.xml',
    ],
}
