# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryBook(models.Model):
    _name = "library.book"
    _description = "Library Book"
    _order = "date_release desc, name"

    name = fields.Char(
        string="Title",
        required=True,
        index=True,
    )
    short_name = fields.Char(
        string="Short Title",
        translate=True,
        index=True,
    )
    notes = fields.Text(
        string="Internal Notes",
    )
    state = fields.Selection(
        selection=[("draft", "Not Available"),
                   ("available", "Available"),
                   ("lost", "Lost")],
        string="State",
        default="draft",
    )
    description = fields.Html(
        string="Description",
        sanitize=True,
        strip_style=False,
    )
    cover = fields.Binary(
        string="Book Cover",
    )
    out_of_print = fields.Boolean(
        string="Out of Print?",
    )
    date_release = fields.Date(
        string="Release Date",
    )
    date_updated = fields.Datetime(
        string="Last Updated",
        copy=False,
    )
    pages = fields.Integer(
        string="Number of Pages",
        groups="base.group_user",
        states={"lost": [("readonly", True)]},
        help="Total book page count",
        company_dependent=False,
    )
    reader_rating = fields.Float(
        string="Reader Average Rating",
        digits=(14, 4),  # Optional precision (total, decimals),
    )
    author_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Authors",
    )
    cost_price = fields.Float(
        string="Book Cost",
        digits="Book Price",
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
    )
    retail_price = fields.Monetary(
        string="Retail Price",
        currency_field="currency_id",
    )
    publisher_id = fields.Many2one(
        comodel_name="res.partner",
        string="Publisher",
        ondelete="set null",
        context={},
        domain=[],
    )
    category_id = fields.Many2one(
        comodel_name="library.book.category",
    )
    age_days = fields.Float(
        string="Days Since Release",
        compute="_compute_age",
        inverse="_inverse_age",
        search="_search_age",
        store=False, 	# optional
        compute_sudo=False # optional
    )
    _sql_constraints = [("name_uniq", "UNIQUE (name)", "Book title must be unique.")]

    def name_get(self):
        """ This method used to customize display name of the record """
        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
            result.append((record.id, rec_name))
        return result

    @api.constrains("date_release")
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError("Release date must be in the past")

    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            delta = today - book.date_release
            book.age_days = delta.days

    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        # convert the operator:
        # book with age > value have a date < value_date
        operator_map = {'>': '<', '>=': '<=', '<': '>', '<=': '>=', }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]

    def grouped_data(self):
        data = self._get_average_cost()
        _logger.info("Groupped Data %s" % data)

    @api.model
    def _get_average_cost(self):
        grouped_result = self.read_group(
            [("cost_price", "!=", False)], # Domain
            ["category_id", "cost_price:avg"], # Fields to access
            ["category_id"] # group_by
            )
        return grouped_result


class ResPartner(models.Model):
    _inherit = "res.partner"

    published_book_ids = fields.One2many(
        comodel_name="library.book",
        inverse_name="publisher_id",
        string="Published Books",
    )
    authored_book_ids = fields.Many2many(
        comodel_name="library.book",
        string="Authored Books",
        relation="library_book_res_partner_rel",  # optional
    )
