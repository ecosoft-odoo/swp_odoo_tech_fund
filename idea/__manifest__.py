# -*- coding: utf-8 -*-
{
    "name": "Ideas",
    "version": "0.1",
    "category": "Tools",
    "description": """
This module allows user to easily and efficiently participate in enterprise innovation.
=======================================================================================

It allows everybody to express ideas about different subjects.
Then, other users can comment on these ideas and vote for particular ideas.
Each idea has a score based on the different votes.
The managers can obtain an easy view of best ideas from all the users.
Once installed, check the menu "Ideas" in the "Tools" main menu.""",
    "author": "OpenERP SA",
    "website": "http://openerp.com",
    "depends": ["mail"],
    "data": [
        "security/idea_security.xml",
        "security/ir.model.access.csv",
        "views/idea_view.xml",
    ],
    "demo": ["demo/idea_data.xml"],
    "installable": True,
}
