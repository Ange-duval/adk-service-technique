# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AdkBloc(models.Model):
    _name = 'adk.bloc'
    _description = "Bloc de contrôle"
    _order = 'site_id, name'

    name = fields.Char(string="Nom du bloc", required=True,
                        help="Ex: Bureau directeur, Hall, Salle de réunion...")
    site_id = fields.Many2one('adk.site', string="Point de contrôle", required=True,
                               ondelete='cascade', tracking=True)
    description = fields.Text(string="Description")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(related='site_id.company_id', store=True)

    equipment_ids = fields.Many2many('adk.equipment', 'adk_equipment_bloc_rel', 'bloc_id', 'equipment_id',
                                      string="Équipements")
    maintenance_ids = fields.One2many('adk.maintenance', 'bloc_id', string="Interventions")
    equipment_count = fields.Integer(compute='_compute_counts', string="Nb Équipements")
    maintenance_count = fields.Integer(compute='_compute_counts', string="Nb Interventions")

    @api.depends('equipment_ids', 'maintenance_ids')
    def _compute_counts(self):
        for rec in self:
            rec.equipment_count = len(rec.equipment_ids)
            rec.maintenance_count = len(rec.maintenance_ids)

    @api.depends('name', 'site_id')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "%s / %s" % (rec.site_id.name, rec.name) if rec.site_id else rec.name

    def action_view_maintenances(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Interventions - %s" % self.name,
            'res_model': 'adk.maintenance',
            'view_mode': 'list,kanban,form',
            'domain': [('bloc_id', '=', self.id)],
            'context': {'default_bloc_id': self.id, 'default_site_id': self.site_id.id},
        }
