frappe.pages['sales-kpi-dashboard'].on_page_load = function(wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Lead & Sales KPI Dashboard',
        single_column: true
    });

    $(frappe.render_template("sales_kpi_dashboard")).appendTo(page.body);

    const kpis = [
        { report: "My Conversion Rate", field: "rate", suffix: " %", target: "#my_conversion_rate" },
        { report: "Team Conversion Rate", field: "rate", suffix: " %", target: "#team_conversion_rate" },
        { report: "Revenue This Month", field: "revenue", suffix: " ₹", target: "#revenue_this_month" },
        { report: "Opportunities Won This Month", field: "won", suffix: "", target: "#opps_won" },
        { report: "Demos Scheduled Today", field: "count", suffix: "", target: "#demos_today" },
        { report: "Lost Opportunities This Month", field: "lost", suffix: "", target: "#opps_lost" },
    ];

    kpis.forEach(kpi => {
        frappe.call({
            method: "frappe.desk.query_report.run",
            args: { report_name: kpi.report },
            callback: function(r) {
                console.log(`KPI: ${kpi.report}`, r);
                if (r.message && r.message.result && r.message.result.length) {
                    const val = r.message.result[0][kpi.field] ?? "N/A";
                    $(kpi.target).text(val + kpi.suffix);
                } else {
                    $(kpi.target).text("N/A");
                }
            },
            error: function(err) {
                console.error(`Error fetching ${kpi.report}:`, err);
                $(kpi.target).text("Error");
            }
        });
    });

    // Donut Chart: Conversion Breakdown
    frappe.call({
        method: "frappe.desk.query_report.run",
        args: { report_name: "My Conversion Rate" },
        callback: function(r) {
            if (r.message && r.message.result && r.message.result.length) {
                const converted = r.message.result[0].converted || 0;
                const total = r.message.result[0].total || 0;
                const not_converted = total - converted;

                const data = {
                    labels: ["Converted", "Not Converted"],
                    datasets: [{ values: [converted, not_converted] }]
                };

                new frappe.Chart("#conversion_chart", {
                    title: "My Lead Conversion Breakdown",
                    data: data,
                    type: 'donut',
                    height: 250
                });
            }
        }
    });
};
