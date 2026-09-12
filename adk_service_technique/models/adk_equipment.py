# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AdkEquipment(models.Model):
    _name = 'adk.equipment'
    _description = "Équipement"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string="Nom de l'équipement", required=True, tracking=True)
    code = fields.Char(string="Numéro / Référence", copy=False)
    characteristic = fields.Text(string="Caractéristique")

    site_ids = fields.Many2many('adk.site', 'adk_equipment_site_rel', 'equipment_id', 'site_id',
                                 string="Points de contrôle", required=True, tracking=True)
    bloc_ids = fields.Many2many('adk.bloc', 'adk_equipment_bloc_rel', 'equipment_id', 'bloc_id',
                                 string="Blocs", tracking=True,
                                 domain="[('site_id', 'in', site_ids)]")

    technical_sheet = fields.Binary(string="Fiche technique")
    technical_sheet_filename = fields.Char(string="Nom du fichier")
    image_1920 = fields.Image(string="Photo")

    purchase_date = fields.Date(string="Date d'acquisition")
    warranty_date = fields.Date(string="Fin de garantie")

    state = fields.Selection([
        ('good', "Bon fonctionnement"),
        ('issue', "En panne"),
        ('maintenance', "En maintenance"),
    ], string="État", default='good', tracking=True, group_expand='_expand_states')

    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string="Société",
                                  compute='_compute_company_id', store=True)

    maintenance_ids = fields.One2many('adk.maintenance', 'equipment_id', string="Interventions")
    maintenance_count = fields.Integer(compute='_compute_maintenance_count', string="Nb interventions")

    @api.model
    def _expand_states(self, states, domain):
        return [key for key, val in self._fields['state'].selection]

    @api.depends('maintenance_ids')
    def _compute_maintenance_count(self):
        for rec in self:
            rec.maintenance_count = len(rec.maintenance_ids)

    @api.depends('site_ids.company_id')
    def _compute_company_id(self):
        for rec in self:
            rec.company_id = rec.site_ids[:1].company_id

    @api.onchange('site_ids')
    def _onchange_site_ids(self):
        if self.bloc_ids:
            invalid_blocs = self.bloc_ids.filtered(lambda b: b.site_id not in self.site_ids)
            if invalid_blocs:
                self.bloc_ids = self.bloc_ids - invalid_blocs

    @api.depends('name', 'code')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "[%s] %s" % (rec.code, rec.name) if rec.code else rec.name

    def action_view_maintenances(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': "Interventions - %s" % self.name,
            'res_model': 'adk.maintenance',
            'view_mode': 'list,kanban,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id, 'default_site_id': self.site_ids[:1].id},
        }
