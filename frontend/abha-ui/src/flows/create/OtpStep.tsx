import { completeEnrolment, requestEnrolmentOtp, resendEnrolmentOtp } from "../../api/abha";
import { useKnown } from "../../domain/StoreContext";
import { OtpPanel } from "../../ui/OtpPanel";

/**
 * Verify the Aadhaar OTP and create the ABHA. When the Aadhaar number was already given elsewhere (a lookup that found
 * no ABHA), the OTP has not been requested yet and this screen requests it, so the number is never asked for twice.
 */
export function OtpStep({ onNext, onBack }: { onNext: (mobileLinked: boolean) => void; onBack: () => void }) {
  const { known, dispatch } = useKnown();
  const patient = known.patient?.name;
  const needsSend = !known.txnId;

  async function firstSend() {
    if (!patient || !known.aadhaar || !known.consent) throw new Error("The Aadhaar number or the agreement is missing. Go back and enter it.");
    // Snapshot the patient/consent that started this request. If staff switch patients
    // while the OTP request is in flight, the old step must not merge its result onto the
    // new patient's state.
    const startedPatient = patient;
    const startedConsentId = known.consent.id;
    const res = await requestEnrolmentOtp(startedPatient, known.aadhaar, startedConsentId);
    if (known.patient?.name !== startedPatient || known.consent?.id !== startedConsentId) return;
    dispatch({ type: "learn", patch: { txnId: res.txnId } });
  }

  async function resend() {
    if (!patient || !known.txnId) throw new Error("The OTP request has expired. Go back and send it again.");
    await resendEnrolmentOtp(patient, known.txnId);
  }

  async function verify(code: string) {
    if (!patient || !known.txnId) throw new Error("The OTP request has expired. Go back and send it again.");
    // Snapshot the patient that started verification; reject the result if the patient changed.
    const startedPatient = patient;
    const res = await completeEnrolment(startedPatient, known.txnId, code);
    if (known.patient?.name !== startedPatient) return;
    dispatch({ type: "learn", patch: { txnId: res.txnId ?? known.txnId, abhaNumber: res.abha_number, mobileLinked: res.mobile_linked } });
    dispatch({ type: "forget", keys: ["aadhaar"] });
    onNext(res.mobile_linked); // passed on directly: the store has not re-rendered yet
  }

  return (
    <OtpPanel
      heading="Verify Aadhaar OTP"
      lede="Enter the 6-digit OTP sent to the mobile number linked to the Aadhaar. It is checked as soon as the sixth digit is in."
      label="Aadhaar OTP"
      verify={verify}
      resend={resend}
      send={needsSend ? firstSend : undefined}
      back={{ label: "Change Aadhaar number", onClick: onBack }}
    />
  );
}
