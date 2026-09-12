import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class AdkDashboard extends Component {
    static template = "adk_service_technique.Dashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            data: {
                kpis: {},
                by_type: [],
                by_site: [],
                by_team: [],
                recent: [],
            },
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.loading = true;
        const data = await this.orm.call("adk.maintenance", "get_dashboard_data", []);
        this.state.data = data;
        this.state.loading = false;
    }

    stateLabel(state) {
        return {
            draft: "Brouillon",
            in_progress: "En cours",
            done: "Bon fonctionnement",
            cancel: "Annulée",
        }[state] || state;
    }

    stateBadgeClass(state) {
        return {
            draft: "text-bg-secondary",
            in_progress: "text-bg-warning",
            done: "text-bg-success",
            cancel: "text-bg-danger",
        }[state] || "text-bg-secondary";
    }

    async openMaintenances(domain = [], context = {}) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            name: "Maintenances",
            res_model: "adk.maintenance",
            view_mode: "list,kanban,form,calendar",
            views: [
                [false, "list"],
                [false, "kanban"],
                [false, "form"],
                [false, "calendar"],
            ],
            domain,
            context,
        });
    }

    async openRecord(id) {
        await this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "adk.maintenance",
            res_id: id,
            views: [[false, "form"]],
            target: "current",
        });
    }

    onClickTotal() {
        this.openMaintenances([]);
    }
    onClickInProgress() {
        this.openMaintenances([["state", "=", "in_progress"]]);
    }
    onClickDone() {
        this.openMaintenances([["state", "=", "done"]]);
    }
    onClickDraft() {
        this.openMaintenances([["state", "=", "draft"]]);
    }
    onClickType(typeId) {
        this.openMaintenances([["maintenance_type_id", "=", typeId]]);
    }
    onClickSite(siteId) {
        this.openMaintenances([["site_id", "=", siteId]]);
    }
    onClickTeam(teamId) {
        this.openMaintenances([["team_id", "=", teamId]]);
    }
    onClickRecent(id) {
        this.openRecord(id);
    }
    onClickNewIntervention() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Nouvelle intervention",
            res_model: "adk.maintenance",
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("adk_service_technique.dashboard", AdkDashboard);
