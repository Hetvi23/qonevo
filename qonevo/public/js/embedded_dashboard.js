// Embedded Delivery Dashboard Integration
if (typeof frappe !== 'undefined' && frappe.ready) {
    frappe.ready(function() {
        setTimeout(function() {
            addEmbeddedDashboardButton();
        }, 2000);
    });
} else {
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(function() {
            addEmbeddedDashboardButton();
        }, 2000);
    });
}

function addEmbeddedDashboardButton() {
    // Check if button already exists
    if (document.getElementById('embedded-dashboard-btn')) {
        return;
    }

    // Create dashboard button
    const dashboardBtn = $(`
        <button class="btn btn-primary" id="embedded-dashboard-btn" style="margin: 10px;">
            <i class="fa fa-chart-line"></i> Delivery Dashboard
        </button>
    `);

    // Add click handler
    dashboardBtn.click(function() {
        openEmbeddedDashboard();
    });

    // Try to add to the main navigation
    const navbar = $('.navbar-nav, .nav.navbar-nav, .navbar .nav');
    if (navbar.length) {
        navbar.append(dashboardBtn);
    } else {
        // Fallback: add to the page header
        const pageHeader = $('.page-header, .page-title, .breadcrumb');
        if (pageHeader.length) {
            pageHeader.after(dashboardBtn);
        } else {
            // Last resort: add to body
            $('body').prepend(dashboardBtn);
        }
    }

    // Add some styling
    dashboardBtn.css({
        'position': 'relative',
        'z-index': '1000',
        'font-weight': 'bold'
    });
}

function openEmbeddedDashboard() {
    // Create modal container
    const modal = $(`
        <div class="modal fade" id="dashboardModal" tabindex="-1" role="dialog" aria-labelledby="dashboardModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-xl" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="dashboardModalLabel">
                            <i class="fa fa-chart-line"></i> Delivery Dashboard
                        </h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body" style="padding: 0;">
                        <iframe src="/delivery_dashboard_embedded.html" 
                                style="width: 100%; height: 600px; border: none;"
                                frameborder="0">
                        </iframe>
                    </div>
                </div>
            </div>
        </div>
    `);

    // Remove existing modal if any
    $('#dashboardModal').remove();

    // Add modal to body
    $('body').append(modal);

    // Show modal
    $('#dashboardModal').modal('show');

    // Handle modal close
    $('#dashboardModal').on('hidden.bs.modal', function() {
        $(this).remove();
    });
}

// Add dashboard button to Sales Order list view
if (typeof frappe !== 'undefined' && frappe.listview_settings) {
    frappe.listview_settings['Sales Order'] = {
        onload: function(listview) {
            setTimeout(function() {
                addDashboardToSalesOrderList(listview);
            }, 1000);
        }
    };
}

function addDashboardToSalesOrderList(listview) {
    // Check if button already exists
    if (listview.$page.find('#embedded-dashboard-btn').length) {
        return;
    }

    // Create dashboard button for list view
    const dashboardBtn = $(`
        <button class="btn btn-primary btn-sm" id="embedded-dashboard-btn" style="margin: 10px;">
            <i class="fa fa-chart-line"></i> Delivery Dashboard
        </button>
    `);

    // Add click handler
    dashboardBtn.click(function() {
        openEmbeddedDashboard();
    });

    // Try multiple locations to place the button
    let buttonAdded = false;

    // 1. Try to add to the toolbar area
    const toolbar = listview.$page.find('.list-toolbar, .toolbar, .list-header');
    if (toolbar.length && !buttonAdded) {
        toolbar.append(dashboardBtn);
        buttonAdded = true;
    }

    // 2. Try to add to the list view header
    const listViewHeader = listview.$page.find('.list-view-header');
    if (listViewHeader.length && !buttonAdded) {
        listViewHeader.append(dashboardBtn);
        buttonAdded = true;
    }

    // 3. Try to add to the page header
    const pageHeader = listview.$page.find('.page-header, .page-title');
    if (pageHeader.length && !buttonAdded) {
        pageHeader.after(dashboardBtn);
        buttonAdded = true;
    }

    // 4. Fallback: add to the top of the list container
    if (!buttonAdded) {
        const listContainer = listview.$page.find('.list-view-container, .list-container');
        if (listContainer.length) {
            listContainer.prepend(dashboardBtn);
        } else {
            // Last resort: add to the page body
            listview.$page.prepend(dashboardBtn);
        }
    }

    // Add some styling to make it more visible
    dashboardBtn.css({
        'position': 'relative',
        'z-index': '1000',
        'font-weight': 'bold'
    });
} 