# Copyright (c) 2026, earthians Health Informatics Pvt. Ltd. and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase

from healthcare.healthcare.doctype.patient_appointment.test_patient_appointment import create_patient
from healthcare.healthcare.utils import get_healthcare_services_to_invoice


class TestHealthcareServicesToInvoice(IntegrationTestCase):
	def test_link_customer_uses_patient_name_for_set_value(self):
		patient = create_patient(id=9001, customer=None)
		customer = "_Test Customer"
		if not frappe.db.exists("Customer", customer):
			frappe.get_doc({"doctype": "Customer", "customer_name": customer, "customer_type": "Individual"}).insert(
				ignore_permissions=True
			)

		frappe.db.set_value("Patient", patient, "customer", None)
		get_healthcare_services_to_invoice(patient, customer, "_Test Company", link_customer=1)

		self.assertEqual(frappe.db.get_value("Patient", patient, "customer"), customer)