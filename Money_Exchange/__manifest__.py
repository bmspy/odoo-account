{
    'name': 'Exchange Currencies',
    'category': 'Account',

    'summary': 'By Belal M. Alswerki',
    'description': """
            this Module For Handle your Exchange Currencies 
        """,
    'data': [
        'views/currency_pairs.xml',
        'views/exchange.xml',
        'views/exchange_rate.xml',
    ],
    'css': ['static/src/css/style.css'],
    'depends': ['base', 'mail'],
    'auto_install': False,
    'application': True,
    'installable': True,
}
