# -*- coding: utf-8 -*-
from odoo import fields, models


class AdkReportWizard(models.TransientModel):
    _name = 'adk.report.wizard'
    _description = "Assistant de génération de rapport"

    report_type = fields.Selection([
        ('intervention', "Rapport de suivi d'intervention"),
        ('equipment', "Rapport d'équipement"),
    ], string="Type de rapport", required=True, default='intervention')

    site_id = fields.Many2one('adk.site', string="Point de contrôle (Site)", required=True)
    bloc_id = fields.Many2one('adk.bloc', string="Bloc", domain="[('site_id', '=', site_id)]",
                               help="Laisser vide pour générer le rapport sur tout le site")
    date_from = fields.Date(string="Date du")
    date_to = fields.Date(string="Date au")

    def action_generate_report(self):
        self.ensure_one()

        if self.report_type == 'intervention':
            domain = [('site_id', '=', self.site_id.id)]
            if self.bloc_id:
                domain.append(('bloc_id', '=', self.bloc_id.id))
            if self.date_from:
                domain.append(('detection_date', '>=', self.date_from))
            if self.date_to:
                domain.append(('detection_date', '<=', self.date_to))
            records = self.env['adk.maintenance'].search(domain)
            return self.env.ref('adk_service_technique.action_report_intervention').report_action(records)

        domain = [('site_ids', 'in', self.site_id.id)]
        if self.bloc_id:
            domain.append(('bloc_ids', 'in', self.bloc_id.id))
        records = self.env['adk.equipment'].search(domain)
        return self.env.ref('adk_service_technique.action_report_equipment').report_action(records)
