// Add Delivery Dashboard button to navigation
if (typeof frappe !== 'undefined' && frappe.ready) {
    frappe.ready(function() {
        // Wait for the page to load completely
        setTimeout(function() {
            addDashboardToNav();
        }, 2000);
    });
} else {
    // Fallback: wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(function() {
            addDashboardToNav();
        }, 2000);
    });
}

function addDashboardToNav() {
    // Check if button already exists
    if (document.querySelector('#delivery-dashboard-nav-btn')) {
        return;
    }
    
    // Create the dashboard button
    const dashboardBtn = document.createElement('a');
    dashboardBtn.href = '/delivery-dashboard';
    dashboardBtn.id = 'delivery-dashboard-nav-btn';
    dashboardBtn.className = 'btn btn-primary btn-sm';
    dashboardBtn.style.cssText = `
        margin: 5px 10px;
        color: white;
        text-decoration: none;
        font-weight: bold;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    `;
    dashboardBtn.innerHTML = '<i class="fa fa-chart-line"></i> Delivery Dashboard';
    
    // Try to add to different navigation areas
    let added = false;
    
    // 1. Try to add to the main navbar
    const navbar = document.querySelector('.navbar-nav, .nav.navbar-nav');
    if (navbar && !added) {
        const navItem = document.createElement('li');
        navItem.className = 'nav-item';
        navItem.appendChild(dashboardBtn);
        navbar.appendChild(navItem);
        added = true;
    }
    
    // 2. Try to add to the page header
    const pageHeader = document.querySelector('.page-header, .page-title');
    if (pageHeader && !added) {
        pageHeader.appendChild(dashboardBtn);
        added = true;
    }
    
    // 3. Try to add to the toolbar
    const toolbar = document.querySelector('.toolbar, .list-toolbar');
    if (toolbar && !added) {
        toolbar.appendChild(dashboardBtn);
        added = true;
    }
    
    // 4. Try to add to the top of the page
    if (!added) {
        const body = document.querySelector('body');
        if (body) {
            body.insertBefore(dashboardBtn, body.firstChild);
        }
    }
}

// Also add to Sales Order list view specifically
if (typeof frappe !== 'undefined' && frappe.listview_settings) {
    frappe.listview_settings['Sales Order'] = {
        onload: function(listview) {
            // Add dashboard button to Sales Order list
            setTimeout(function() {
                addDashboardToSalesOrderList(listview);
            }, 1000);
        }
    };
}

function addDashboardToSalesOrderList(listview) {
    // Check if button already exists
    if (listview.$page.find('#delivery-dashboard-list-btn').length) {
        return;
    }
    
    // Create dashboard button for Sales Order list
    const dashboardBtn = $(`
        <a href="/delivery-dashboard" class="btn btn-primary btn-sm" id="delivery-dashboard-list-btn" 
           style="margin: 10px; color: white; text-decoration: none; font-weight: bold;">
            <i class="fa fa-chart-line"></i> Delivery Dashboard
        </a>
    `);
    
    // Add to the list view
    const listContainer = listview.$page.find('.list-view-container, .list-container');
    if (listContainer.length) {
        listContainer.prepend(dashboardBtn);
    } else {
        listview.$page.prepend(dashboardBtn);
    }
} 