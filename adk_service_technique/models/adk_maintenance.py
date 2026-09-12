# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AdkMaintenance(models.Model):
    _name = 'adk.maintenance'
    _description = "Intervention de maintenance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'detection_date desc, id desc'
    _rec_name = 'name'

    name = fields.Char(string="Référence", required=True, copy=False, readonly=True, default='Nouveau')

    maintenance_type_id = fields.Many2one('adk.maintenance.type', string="Type de maintenance",
                                           required=True, tracking=True)
    detection_date = fields.Datetime(string="Date du constat d'anomalie",
                                      default=fields.Datetime.now, required=True, tracking=True)

    site_id = fields.Many2one('adk.site', string="Point de contrôle", required=True, tracking=True)
    bloc_id = fields.Many2one('adk.bloc', string="Bloc de contrôle",
                               domain="[('site_id', '=', site_id)]", tracking=True,
                               help="Lieu ou lieux précis du point de contrôle")
    partner_id = fields.Many2one('res.partner', string="Client / Responsable du point de contrôle")

    intervention_mode = fields.Selection([
        ('team', "Équipe"),
        ('agent', "Agent(s)"),
    ], string="Mode d'intervention", default='team', required=True)
    team_id = fields.Many2one('adk.team', string="Équipe d'intervention",
                               domain="[('active', '=', True)]")
    agent_ids = fields.Many2many('hr.employee', string="Agents intervenants")

    equipment_id = fields.Many2one('adk.equipment', string="Équipement concerné",
                                    domain="[('site_ids', 'in', site_id)]")

    diagnostic = fields.Text(string="Diagnostic")
    measures_taken = fields.Text(string="Mesures prises")
    corrective_actions = fields.Text(string="Actions à mener (Mesures correctives)")

    state = fields.Selection([
        ('draft', "Brouillon"),
        ('in_progress', "En cours"),
        ('done', "Bon fonctionnement"),
        ('cancel', "Annulée"),
    ], string="Statut", default='draft', tracking=True, group_expand='_expand_states')
    priority = fields.Selection([
        ('0', "Normale"),
        ('1', "Urgente"),
    ], string="Priorité", default='0')

    start_datetime = fields.Datetime(string="Début intervention")
    end_datetime = fields.Datetime(string="Fin intervention")
    duration = fields.Float(string="Durée (heures)", compute='_compute_duration', store=True)
    color = fields.Integer(string="Couleur", related='maintenance_type_id.couleur', store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.model
    def _expand_states(self, states, domain):
        return [key for key, val in self._fields['state'].selection]

    @api.depends('start_datetime', 'end_datetime')
    def _compute_duration(self):
        for rec in self:
            if rec.start_datetime and rec.end_datetime:
                delta = rec.end_datetime - rec.start_datetime
                rec.duration = delta.total_seconds() / 3600.0
            else:
                rec.duration = 0.0

    @api.onchange('site_id')
    def _onchange_site_id(self):
        if self.bloc_id and self.bloc_id.site_id != self.site_id:
            self.bloc_id = False
        if self.equipment_id and self.site_id not in self.equipment_id.site_ids:
            self.equipment_id = False

    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        if self.equipment_id:
            if self.site_id not in self.equipment_id.site_ids:
                self.site_id = self.equipment_id.site_ids[:1]
            if self.bloc_id not in self.equipment_id.bloc_ids:
                self.bloc_id = self.equipment_id.bloc_ids.filtered(
                    lambda b: b.site_id == self.site_id)[:1]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('adk.maintenance') or 'Nouveau'
        return super().create(vals_list)

    def action_start(self):
        self.write({'state': 'in_progress', 'start_datetime': fields.Datetime.now()})

    def action_done(self):
        self.write({'state': 'done', 'end_datetime': fields.Datetime.now()})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    @api.model
    def get_dashboard_data(self):
        """Aggregates data consumed by the OWL dashboard widget."""
        Maintenance = self.env['adk.maintenance']
        all_records = Maintenance.search([])
        total = len(all_records)
        by_state = {
            'draft': len(all_records.filtered(lambda m: m.state == 'draft')),
            'in_progress': len(all_records.filtered(lambda m: m.state == 'in_progress')),
            'done': len(all_records.filtered(lambda m: m.state == 'done')),
            'cancel': len(all_records.filtered(lambda m: m.state == 'cancel')),
        }
        resolution_rate = (by_state['done'] / total * 100.0) if total else 0.0

        types = self.env['adk.maintenance.type'].search([])
        by_type = [{
            'id': t.id,
            'name': t.name,
            'icon': t.icone or 'fa-wrench',
            'color': t.couleur or 0,
            'count': t.maintenance_count,
        } for t in types]

        sites = self.env['adk.site'].search([])
        by_site = [{
            'id': s.id,
            'name': s.name,
            'bloc_count': s.bloc_count,
            'equipment_count': s.equipment_count,
            'maintenance_count': s.maintenance_count,
            'open_count': s.maintenance_open_count,
        } for s in sites]

        teams = self.env['adk.team'].search([])
        by_team = [{
            'id': tm.id,
            'name': tm.name,
            'agent_count': tm.agent_count,
            'intervention_count': tm.intervention_count,
            'open_count': tm.open_intervention_count,
            'avg_duration': round(tm.avg_duration, 2),
            'success_rate': round(tm.success_rate, 1),
        } for tm in teams]

        recent = Maintenance.search([], order='detection_date desc', limit=8)
        recent_list = [{
            'id': r.id,
            'name': r.name,
            'site': r.site_id.name or '',
            'bloc': r.bloc_id.name or '',
            'type': r.maintenance_type_id.name or '',
            'state': r.state,
            'date': fields.Datetime.to_string(r.detection_date) if r.detection_date else '',
        } for r in recent]

        equipments = self.env['adk.equipment'].search([])
        equipment_issue_count = len(equipments.filtered(lambda e: e.state == 'issue'))

        return {
            'kpis': {
                'total': total,
                'draft': by_state['draft'],
                'in_progress': by_state['in_progress'],
                'done': by_state['done'],
                'cancel': by_state['cancel'],
                'resolution_rate': round(resolution_rate, 1),
                'site_count': len(sites),
                'team_count': len(teams),
                'equipment_count': len(equipments),
                'equipment_issue_count': equipment_issue_count,
            },
            'by_type': by_type,
            'by_site': by_site,
            'by_team': by_team,
            'recent': recent_list,
        }
