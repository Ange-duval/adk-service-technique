# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AdkSite(models.Model):
    _name = 'adk.site'
    _description = "Point de contrôle (Site)"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string="Nom du point de contrôle", required=True, tracking=True,
                        help="Ex: Étage 1, Étage 2, Siège, Agence Bonanjo...")
    code = fields.Char(string="Code")
    address = fields.Char(string="Adresse")
    partner_id = fields.Many2one('res.partner', string="Client / Responsable", tracking=True)
    color = fields.Integer(string="Couleur")
    image_1920 = fields.Image(string="Image")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string="Société", default=lambda self: self.env.company)

    bloc_ids = fields.One2many('adk.bloc', 'site_id', string="Blocs")
    equipment_ids = fields.Many2many('adk.equipment', 'adk_equipment_site_rel', 'site_id', 'equipment_id',
                                      string="Équipements")
    maintenance_ids = fields.One2many('adk.maintenance', 'site_id', string="Interventions")

    bloc_count = fields.Integer(compute='_compute_counts', string="Nb Blocs")
    equipment_count = fields.Integer(compute='_compute_counts', string="Nb Équipements")
    maintenance_count = fields.Integer(compute='_compute_counts', string="Nb Interventions")
    maintenance_open_count = fields.Integer(compute='_compute_counts', string="Interventions en cours")

    @api.depends('bloc_ids', 'equipment_ids', 'maintenance_ids', 'maintenance_ids.state')
    def _compute_counts(self):
        for rec in self:
            rec.bloc_count = len(rec.bloc_ids)
            rec.equipment_count = len(rec.equipment_ids)
            rec.maintenance_count = len(rec.maintenance_ids)
            rec.maintenance_open_count = len(rec.maintenance_ids.filtered(
                lambda m: m.state in ('draft', 'in_progress')))

    def action_view_maintenances(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Interventions - %s" % self.name,
            'res_model': 'adk.maintenance',
            'view_mode': 'list,kanban,form',
            'domain': [('site_id', '=', self.id)],
            'context': {'default_site_id': self.id},
        }

    def action_view_equipments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Équipements - %s" % self.name,
            'res_model': 'adk.equipment',
            'view_mode': 'list,kanban,form',
            'domain': [('site_ids', 'in', self.id)],
            'context': {'default_site_ids': [self.id]},
        }

    def action_view_blocs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Blocs - %s" % self.name,
            'res_model': 'adk.bloc',
            'view_mode': 'list,form',
            'domain': [('site_id', '=', self.id)],
            'context': {'default_site_id': self.id},
        }

    @api.model
    def action_print_global_report(self):
        """Génère le rapport global sur tous les points de contrôle (sites) et blocs actifs."""
        sites = self.search([])
        return self.env.ref('adk_service_technique.action_report_global').report_action(sites)
