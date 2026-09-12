# -*- coding: utf-8 -*-
{
    'name': 'ADK Service Technique',
    'version': '18.0.1.1.0',
    'category': 'Services/Maintenance',
    'sequence': 5,
    'summary': 'Professional management of technical interventions, sites, equipment and maintenance teams',
    'description': '''
ADK SERVICE TECHNIQUE
=====================
Professional technical service and maintenance management for Odoo 18.

* Integrated dashboard for interventions, sites, teams and maintenance KPIs.
* End-to-end intervention management: anomaly, diagnosis, measures and corrective actions.
* Sites and blocks for structured technical locations and control points.
* Equipment management with technical information, location, status and warranty details.
* Maintenance teams and agents linked to Odoo employees.
* PDF reports for interventions, equipment and global service activity.
* Role-based access for agents and managers.
''',
    'author': 'Kambeu Henang Ange Duval',
    'website': '',
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
    'price': 49.0,
    'currency': 'EUR',
}
