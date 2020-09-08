# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


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
    active = fields.Boolean(default=True)
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

    @api.model
    def update_book_price(self):
        # NOTE: Real cases can be complex but here we just increse cost price by 10
        _logger.info('Method update_book_price called from XML')
        all_books = self.search([])
        for book in all_books:
            book.cost_price += 10

    def make_available(self):
        self.ensure_one()
        self.state = 'available'

    def make_borrowed(self):
        self.ensure_one()
        self.state = 'borrowed'

    def make_lost(self):
        self.ensure_one()
        self.state = 'lost'
        if not self.env.context.get('avoid_deactivate'):
            self.active = False

    def book_rent(self):
        self.ensure_one()
        if self.state != 'available':
            raise UserError(_('Book is not available for renting'))
        rent_as_superuser = self.env['library.book.rent'].sudo()
        rent_as_superuser.create({
            'book_id': self.id,
            'borrower_id': self.env.user.partner_id.id,
        })

    def average_book_occupation(self):
        sql_query = """
            SELECT
                lb.name,
                avg((EXTRACT(epoch from age(return_date, rent_date)) / 86400))::int
            FROM
                library_book_rent AS lbr
            JOIN
                library_book as lb ON lb.id = lbr.book_id
            WHERE lbr.state = 'returned'
            GROUP BY lb.name;"""
        self.env.cr.execute(sql_query)
        result = self.env.cr.fetchall()
        logger.info("Average book occupation: %s", result)

    def return_all_books(self):
        self.ensure_one()
        wizard = self.env['library.return.wizard']
        values = {
            'borrower_id': self.env.user.partner_id.id,
        }
        specs = wizard._onchange_spec()
        updates = wizard.onchange(values, ['borrower_id'], specs)
        value = updates.get('value', {})
        for name, val in value.items():
            if isinstance(val, tuple):
                value[name] = val[0]
        values.update(value)
        wiz = wizard.create(values)
        return wiz.sudo().books_returns()


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
