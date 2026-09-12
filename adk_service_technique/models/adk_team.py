# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AdkTeam(models.Model):
    _name = 'adk.team'
    _description = "Équipe de maintenance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string="Nom de l'équipe", required=True, tracking=True,
                        help="Ex: Équipe de nuit, Équipe électricité...")
    agent_ids = fields.Many2many('hr.employee', string="Agents (employés Odoo)", tracking=True)
    agent_count = fields.Integer(compute='_compute_agent_count', string="Nb agents")
    color = fields.Integer(string="Couleur")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    maintenance_ids = fields.One2many('adk.maintenance', 'team_id', string="Interventions")
    intervention_count = fields.Integer(compute='_compute_stats', string="Nb interventions")
    open_intervention_count = fields.Integer(compute='_compute_stats', string="Interventions en cours")
    avg_duration = fields.Float(compute='_compute_stats', string="Durée moyenne (h)")
    success_rate = fields.Float(compute='_compute_stats', string="Taux de résolution (%)")

    @api.depends('agent_ids')
    def _compute_agent_count(self):
        for rec in self:
            rec.agent_count = len(rec.agent_ids)

    @api.depends('maintenance_ids', 'maintenance_ids.state', 'maintenance_ids.duration')
    def _compute_stats(self):
        for rec in self:
            interventions = rec.maintenance_ids
            rec.intervention_count = len(interventions)
            rec.open_intervention_count = len(interventions.filtered(
                lambda m: m.state in ('draft', 'in_progress')))
            durations = interventions.filtered(lambda m: m.duration > 0)
            rec.avg_duration = (sum(durations.mapped('duration')) / len(durations)) if durations else 0.0
            done = interventions.filtered(lambda m: m.state == 'done')
            rec.success_rate = (len(done) / len(interventions) * 100.0) if interventions else 0.0

    def action_view_maintenances(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Interventions - %s" % self.name,
            'res_model': 'adk.maintenance',
            'view_mode': 'list,kanban,form',
            'domain': [('team_id', '=', self.id)],
            'context': {'default_team_id': self.id},
        }
