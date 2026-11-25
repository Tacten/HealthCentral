import frappe


def execute():
	encounters = frappe.get_all(
		"Patient Encounter",
		filters={
			"appointment": ["is", "set"],
			"insurance_policy": ["in", ["", None]],
		},
		fields=["name", "appointment"],
	)

	for encounter in encounters:
		appointment_insurance = frappe.db.get_value(
			"Patient Appointment",
			encounter.appointment,
			["insurance_policy", "insurance_coverage"],
			as_dict=True,
		)
		if not appointment_insurance:
			continue

		values = {}
		if appointment_insurance.insurance_policy:
			values["insurance_policy"] = appointment_insurance.insurance_policy
		if appointment_insurance.insurance_coverage:
			values["insurance_coverage"] = appointment_insurance.insurance_coverage

		if values:
			frappe.db.set_value("Patient Encounter", encounter.name, values, update_modified=False)
