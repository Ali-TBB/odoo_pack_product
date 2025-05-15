# -*- coding: utf-8 -*-
{
    'name': 'pack_product',
    'description': """
        This module about Wholesale add field to product.
    """,
    'sequence': 1,
    'version': '1.0',
    'category': 'Productivity',
    'depends': ['sale'],
    'assets': {
        'web.assets_backend': [
            'odoo_pack_product/static/src/js/product_line.js',
            'odoo_pack_product/static/src/js/pack_handler.js',
            'odoo_pack_product/static/src/css/product_highlight.css',
        ]
    },
    'data': [
        'security/ir.model.access.csv',
        'wizard/show_comp_wizard_view.xml',
        'views/product_template.xml',
        'views/sale_order_line.xml',
        'views/color_change.xml'

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
