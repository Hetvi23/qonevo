frappe.pages['demo-to-order-dashbo'].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Demo to Order Dashboard',
        single_column: true
    });

    // Load the HTML template into the page
    page.body.html(frappe.render_template("demo_to_order_dashbo"));

    // Fetch data from the backend
    frappe.call({
        method: "qonevo.api.get_demo_conversion_data",
        callback: function(r) {
            if (r.message) {
                const { completed, converted, ratio } = r.message;

                // Show Conversion Rate
                $("#conversionRate").html(`Conversion Rate: <strong>${ratio}%</strong>`);

                // Render Chart.js Donut Chart
                const ctx = document.getElementById("conversionChart").getContext("2d");
                new Chart(ctx, {
                    type: 'doughnut',
                    data: {
                        labels: ["Converted to Order", "Completed but Not Converted"],
                        datasets: [{
                            data: [converted, completed - converted],
                            backgroundColor: ["#4CAF50", "#FFC107"]
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'bottom' }
                        }
                    }
                });
            } else {
                frappe.msgprint("No data found to display.");
            }
        }
    });
};
