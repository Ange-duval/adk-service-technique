# -*- coding: utf-8 -*-
{
    'name': 'ADK Service Technique',
    'version': '18.0.1.1.1',
    'category': 'Services/Maintenance',
    'sequence': 5,
    'summary': "Interventions de maintenance, points de contrôle, équipements et équipes techniques, avec tableau de bord et rapports PDF",
    'description': '''
ADK Service Technique pour Odoo 18
==================================

Gestion du service technique et de la maintenance :

* Tableau de bord : interventions, taux de résolution, équipements en panne, équipes.
* Interventions : constat d'anomalie, diagnostic, mesures prises, actions correctives, statuts.
* Points de contrôle (sites) et blocs pour localiser précisément chaque intervention.
* Équipements : caractéristiques, état, garantie, fiche technique.
* Équipes de maintenance et agents liés aux employés Odoo.
* Rapports PDF : suivi des interventions, équipements et rapport global.
* Droits d'accès par rôle : agent et responsable.
''',
    'author': 'Kambeu Henang Ange Duval',
    'support': 'duvalkambeu61@gmail.com',
    'depends': ['base', 'mail', 'hr'],
    'data': [
        'security/adk_security.xml',
        'security/ir.model.access.csv',
        'data/adk_data.xml',
        'views/adk_site_views.xml',
        'views/adk_bloc_views.xml',
        'views/adk_equipment_views.xml',
        'views/adk_maintenance_type_views.xml',
        'views/adk_team_views.xml',
        'views/adk_maintenance_views.xml',
        'views/adk_dashboard_views.xml',
        'wizard/adk_report_wizard_views.xml',
        'report/report_intervention.xml',
        'report/report_equipment.xml',
        'report/report_global.xml',
        'views/adk_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'adk_service_technique/static/src/dashboard/adk_dashboard.js',
            'adk_service_technique/static/src/dashboard/adk_dashboard.xml',
            'adk_service_technique/static/src/dashboard/adk_dashboard.scss',
        ],
    },
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    # Offre de lancement : gratuit. Pour passer en payant, remplacer par 'price': 49.0
    'price': 0.0,
    'currency': 'EUR',
}
