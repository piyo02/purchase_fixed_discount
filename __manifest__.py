{
    'name': 'Purchase Fixed Discount',
    'author': 'technoindo.com',
    'category': 'hidden',
    'version': '10.0',
    'summary': 'Summary the addon.',
    'description': '''Description the addon'''
                   ,
    'depends': ['purchase', 'account_invoice_po_fixed_discount'], #
    'data': [
        'views/purchase_view.xml',
    ],
    'images': [''],
    'auto_install': False,
    'installable': True,
    'application': False,
}
