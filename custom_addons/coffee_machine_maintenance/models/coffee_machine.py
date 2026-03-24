# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CoffeeMachine(models.Model):
    _name = 'coffee.machine'
    _description = 'Coffee Machine'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    name = fields.Char(
        string='Machine Name',
        required=True,
        tracking=True,
    )
    serial_number = fields.Char(
        string='Serial Number',
        required=True,
        copy=False,
        tracking=True,
    )
    machine_type = fields.Selection([
        ('espresso', 'Espresso Machine'),
        ('drip', 'Drip Coffee Maker'),
        ('capsule', 'Capsule Machine'),
        ('cold_brew', 'Cold Brew Machine'),
        ('grinder', 'Coffee Grinder'),
        ('other', 'Other'),
    ], string='Machine Type', required=True, tracking=True)

    brand = fields.Char(string='Brand')
    model_number = fields.Char(string='Model Number')

    location = fields.Char(
        string='Coffeeshop Location',
        required=True,
        tracking=True,
    )
    status = fields.Selection([
        ('operational', 'Operational'),
        ('under_maintenance', 'Under Maintenance'),
        ('out_of_service', 'Out of Service'),
    ], string='Status', default='operational', required=True, tracking=True)

    purchase_date = fields.Date(string='Purchase Date')
    warranty_expiry = fields.Date(string='Warranty Expiry')
    last_maintenance_date = fields.Date(
        string='Last Maintenance Date',
        compute='_compute_last_maintenance_date',
        store=True,
    )
    next_maintenance_date = fields.Date(
        string='Next Scheduled Maintenance',
        tracking=True,
    )
    maintenance_interval_days = fields.Integer(
        string='Maintenance Interval (Days)',
        default=30,
        help='Number of days between scheduled preventive maintenance',
    )

    notes = fields.Text(string='Notes')
    active = fields.Boolean(default=True)

    maintenance_request_ids = fields.One2many(
        'coffee.maintenance.request',
        'machine_id',
        string='Maintenance Requests',
    )
    maintenance_count = fields.Integer(
        string='Maintenance Count',
        compute='_compute_maintenance_count',
    )

    # -------------------------------------------------------------------------
    # Compute Methods
    # -------------------------------------------------------------------------

    @api.depends('maintenance_request_ids.date_completed', 'maintenance_request_ids.state')
    def _compute_last_maintenance_date(self):
        for rec in self:
            done_requests = rec.maintenance_request_ids.filtered(
                lambda r: r.state == 'done' and r.date_completed
            )
            if done_requests:
                rec.last_maintenance_date = max(done_requests.mapped('date_completed'))
            else:
                rec.last_maintenance_date = False

    def _compute_maintenance_count(self):
        for rec in self:
            rec.maintenance_count = len(rec.maintenance_request_ids)

    # -------------------------------------------------------------------------
    # Constraints
    # -------------------------------------------------------------------------

    _sql_constraints = [
        ('serial_number_unique', 'UNIQUE(serial_number)',
         'Serial number must be unique across all machines.'),
    ]

    @api.constrains('maintenance_interval_days')
    def _check_maintenance_interval(self):
        for rec in self:
            if rec.maintenance_interval_days <= 0:
                raise ValidationError('Maintenance interval must be a positive number of days.')

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------

    def action_view_maintenance_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Requests',
            'res_model': 'coffee.maintenance.request',
            'view_mode': 'tree,form',
            'domain': [('machine_id', '=', self.id)],
            'context': {'default_machine_id': self.id},
        }

    def action_set_operational(self):
        self.write({'status': 'operational'})

    def action_set_under_maintenance(self):
        self.write({'status': 'under_maintenance'})

    def action_set_out_of_service(self):
        self.write({'status': 'out_of_service'})
