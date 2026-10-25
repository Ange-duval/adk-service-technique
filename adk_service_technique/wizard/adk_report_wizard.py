# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


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

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError(_("La date de début doit être antérieure à la date de fin."))

    def action_generate_report(self):
        self.ensure_one()

        if self.report_type == 'intervention':
            domain = [('site_id', '=', self.site_id.id)]
            if self.bloc_id:
                domain.append(('bloc_id', '=', self.bloc_id.id))
            if self.date_from:
                domain.append(('detection_date', '>=', fields.Datetime.to_datetime(self.date_from)))
            if self.date_to:
                # Inclure toute la journée de la date de fin (23:59:59)
                domain.append(('detection_date', '<',
                               fields.Datetime.to_datetime(self.date_to) + timedelta(days=1)))
            records = self.env['adk.maintenance'].search(domain)
            if not records:
                raise UserError(_("Aucune intervention ne correspond à ces critères."))
            return self.env.ref('adk_service_technique.action_report_intervention').report_action(records)

        domain = [('site_ids', 'in', self.site_id.id)]
        if self.bloc_id:
            domain.append(('bloc_ids', 'in', self.bloc_id.id))
        records = self.env['adk.equipment'].search(domain)
        if not records:
            raise UserError(_("Aucun équipement ne correspond à ces critères."))
        return self.env.ref('adk_service_technique.action_report_equipment').report_action(records)
