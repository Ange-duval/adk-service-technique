# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AdkMaintenanceType(models.Model):
    _name = 'adk.maintenance.type'
    _description = "Type de maintenance"
    _order = 'sequence, name'

    name = fields.Char(string="Type de maintenance", required=True, translate=True)
    code = fields.Char(string="Code")
    sequence = fields.Integer(string="Séquence", default=10)
    description = fields.Text(string="Description")
    icone = fields.Char(string="Icône", default='fa-wrench',
                         help="Classe Font Awesome, ex: fa-wrench, fa-shield, fa-medkit")
    couleur = fields.Integer(string="Couleur")
    active = fields.Boolean(default=True)

    maintenance_ids = fields.One2many('adk.maintenance', 'maintenance_type_id', string="Interventions")
    maintenance_count = fields.Integer(compute='_compute_maintenance_count', string="Nb interventions")

    @api.depends('maintenance_ids')
    def _compute_maintenance_count(self):
        for rec in self:
            rec.maintenance_count = len(rec.maintenance_ids)

    def action_view_maintenances(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': 'adk.maintenance',
            'view_mode': 'kanban,list,form',
            'domain': [('maintenance_type_id', '=', self.id)],
            'context': {'default_maintenance_type_id': self.id},
        }
