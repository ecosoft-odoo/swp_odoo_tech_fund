# -*- coding: utf-8 -*-
from odoo import models, fields


class LibraryBook(models.Model):
    _name = "library.book"
    _description = "Library Book"

    name = fields.Char(
        string="Title",
        required=True,
    )
    date_release = fields.Date(
        string="Release Date",
    )
    author_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Authors",
    )
