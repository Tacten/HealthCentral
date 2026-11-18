# Copyright (c) 2026, earthians and contributors
# See license.txt


import frappe
from frappe.tests import UnitTestCase

from healthcare.healthcare.utils import get_healthcare_services_to_invoice


class TestPatientCustomerLink(UnitTestCase):
	def setUp(self):
		super().setUp()
		self.patient_name = None
		self.customer_name = None
		self.previous_link_customer = frappe.db.get_single_value(
			"Healthcare Settings", "link_customer_to_patient"
		)

	def tearDown(self):
		frappe.db.rollback()
		for doctype, name in (("Patient", self.patient_name), ("Customer", self.customer_name)):
			if name and frappe.db.exists(doctype, name):
				frappe.delete_doc(doctype, name, force=1, ignore_permissions=True)
		if (
			frappe.db.get_single_value("Healthcare Settings", "link_customer_to_patient")
			!= self.previous_link_customer
		):
			frappe.db.set_single_value(
				"Healthcare Settings", "link_customer_to_patient", self.previous_link_customer
			)
		super().tearDown()

	def test_validate_customer_created_from_patient_document(self):
		# Sales Invoice loads the Patient document, then links a customer.
		# db.set_value must receive the document name, not the document.
		frappe.db.set_single_value("Healthcare Settings", "link_customer_to_patient", 0)
		patient = frappe.get_doc(
			{"doctype": "Patient", "first_name": "_Test Invoice Link", "sex": "Female"}
		).insert(ignore_permissions=True)
		self.patient_name = patient.name
		customer = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": "_Test Invoice Link Customer",
				"customer_group": "Individual",
				"customer_type": "Individual",
				"territory": frappe.db.get_value("Territory", {"is_group": 0}, "name"),
			}
		).insert(ignore_permissions=True)
		self.customer_name = customer.name
		company = frappe.db.get_value("Company", {}, "name")

		get_healthcare_services_to_invoice(patient.name, customer.name, company, link_customer=1)

		self.assertEqual(frappe.db.get_value("Patient", patient.name, "customer"), customer.name)
