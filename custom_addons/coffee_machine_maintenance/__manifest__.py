# -*- coding: utf-8 -*-
{
    'name': 'Coffee Machine Maintenance',
    'version': '1.0.0',
    'category': 'Maintenance',
    'summary': 'Manage and track maintenance of coffee machines in coffeeshops',
    'description': """
        Coffee Machine Maintenance Module
        ==================================
        This module helps coffeeshop owners and technicians to:
        - Register and manage coffee machines by location
        - Create and track maintenance requests (preventive & corrective)
        - Monitor machine status and maintenance history
        - Assign technicians to maintenance tasks
    """,
    'author': 'Custom',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/coffee_machine_views.xml',
        'views/maintenance_request_views.xml',
        'views/menu.xml',
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
