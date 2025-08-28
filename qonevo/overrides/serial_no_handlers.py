import frappe

def set_model_and_size(doc, method):
    """
    Automatically set model and size on Serial No based on Item defaults.
    Runs on insert/validate.
    """
    if not doc.item_code:
        return

    item = frappe.get_doc("Item", doc.item_code)

    if not doc.custom_model_number and item.custom_default_model_number:
        doc.custom_model_number = item.custom_default_model_number
        frappe.db.commit()

    if not doc.custom_size and item.custom_default_size:
        doc.custom_size = item.custom_default_size
        frappe.db.commit()

