{
    "name": "My Library",
    "summary": "Manage books easily",
    "description": """
Long description of this module
    """,
    "author": "Kitti U.",
    "website": "http://www.example.com",
    "category": "Uncategorized",
    "version": "13.0.1.0.1",
    "depends": ["base", "contacts"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/library_security.xml",
        "views/res_partner.xml",
        "views/library_book.xml",
        "views/library_book_categ.xml",
        "views/library_book_rent.xml",
        "views/library_book_statistics.xml",
        "views/res_config_settings_views.xml",
        "wizard/library_book_rent_wizard.xml",
        "wizard/library_book_return_wizard.xml",
        "data/data.xml",
    ],
    "demo": [
        "data/demo.xml",
    ],
    "post_init_hook": "add_book_hook",
}
