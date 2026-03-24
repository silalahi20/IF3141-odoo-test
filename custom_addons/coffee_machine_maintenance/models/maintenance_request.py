# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class CoffeeMaintenanceRequest(models.Model):
    _name = 'coffee.maintenance.request'
    _description = 'Coffee Machine Maintenance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'request_date desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'coffee.maintenance.request'
        ) or 'New',
    )
    machine_id = fields.Many2one(
        'coffee.machine',
        string='Coffee Machine',
        required=True,
        ondelete='restrict',
        tracking=True,
    )
    machine_type = fields.Selection(
        related='machine_id.machine_type',
        string='Machine Type',
        store=True,
    )
    location = fields.Char(
        related='machine_id.location',
        string='Location',
        store=True,
    )

    request_date = fields.Date(
        string='Request Date',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    date_completed = fields.Date(
        string='Date Completed',
        tracking=True,
    )

    technician_id = fields.Many2one(
        'res.users',
        string='Assigned Technician',
        tracking=True,
    )
    maintenance_type = fields.Selection([
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
    ], string='Maintenance Type', required=True, default='corrective', tracking=True)

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Urgent'),
        ('2', 'Critical'),
    ], string='Priority', default='0')

    state = fields.Selection([
        ('draft', 'New'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    description = fields.Text(string='Problem Description', required=True)
    resolution_notes = fields.Text(string='Resolution Notes')
    cost = fields.Float(string='Maintenance Cost')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )

    parts_used = fields.Text(string='Parts / Materials Used')

    # -------------------------------------------------------------------------
    # State Transitions
    # -------------------------------------------------------------------------

    def action_start(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError('Only new requests can be started.')
            rec.state = 'in_progress'
            rec.machine_id.status = 'under_maintenance'

    def action_done(self):
        for rec in self:
            if rec.state != 'in_progress':
                raise UserError('Only in-progress requests can be marked as done.')
            if not rec.resolution_notes:
                raise UserError('Please fill in the Resolution Notes before closing.')
            rec.state = 'done'
            rec.date_completed = fields.Date.today()
            # Set machine back to operational if no other open requests
            open_requests = self.search([
                ('machine_id', '=', rec.machine_id.id),
                ('state', 'in', ['draft', 'in_progress']),
                ('id', '!=', rec.id),
            ])
            if not open_requests:
                rec.machine_id.status = 'operational'

    def action_cancel(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError('Completed requests cannot be cancelled.')
            rec.state = 'cancelled'

    def action_reset_draft(self):
        for rec in self:
            if rec.state != 'cancelled':
                raise UserError('Only cancelled requests can be reset to draft.')
            rec.state = 'draft'
