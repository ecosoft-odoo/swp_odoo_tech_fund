# -*- coding: utf-8 -*-
import time
from odoo import _, api, fields, models

VoteValues = [("-1", "Not Voted"), ("0", "Very Bad"), ("25", "Bad"), \
              ("50", "Normal"), ("75", "Good"), ("100", "Very Good") ]
DefaultVoteValue = "50"

class IdeaCategory(models.Model):
    """ Category of Idea """
    _name = "idea.category"
    _description = "Idea Category"
    _order = "name asc"

    name = fields.Char(
        string="Category Name",
        size=64,
        required=True,
    )
    _sql_constraints = [
        ("name", "unique(name)", "The name of the category must be unique")
    ]


class IdeaIdea(models.Model):
    """ Idea """
    _name = "idea.idea"
    _inherit = ["mail.thread"]
    _order = "name asc"

    create_uid = fields.Many2one(
        comodel_name="res.users",
        string="Creator",
        required=True,
        readonly=True,
    )
    name = fields.Char(
        string="Idea Summary",
        size=64,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    description = fields.Text(
        string="Description",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Content of the idea",
    )
    category_ids = fields.Many2many(
        comodel_name="idea.category",
        string="Tags",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        selection=[("draft", "New"),
                   ("open", "Accepted"),
                   ("cancel", "Refused"),
                   ("close", "Done")],
        string="Status",
        default="draft",
        readonly=True,
        track_visibility="onchange",
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Idea's Owner",
        required=True,
    )

    _sql_constraints = [
        ("name", "unique(name)", "The name of the idea must be unique")
    ]

    def idea_cancel(self):
        return self.write({"state": "cancel"})

    def idea_open(self):
        return self.write({"state": "open"})

    def idea_close(self):
        return self.write({"state": "close"})

    def idea_draft(self):
        return self.write({"state": "draft"})
