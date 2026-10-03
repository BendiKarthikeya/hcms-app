from django.db import migrations


EMPLOYMENT_PROPOSAL_GENERAL = """
<div style="font-family: Arial, sans-serif; font-size: 11px; color:#000; max-width: 760px; margin:auto;">
  <div style="text-align:center; font-weight:bold;">
    <div style="font-size:13px;">الشركة الوطنية العمانية للهندسة و الاستثمار ( ش م ع ع )</div>
    <div style="font-size:13px;">Oman National Engineering &amp; Investment Company (SAOG)</div>
    <div style="font-size:14px; margin-top:6px;">EMPLOYMENT PROPOSAL FORM</div>
  </div>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:10px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;">
      <td colspan="4">General</td>
      <td style="width:60px;">05</td>
      <td style="width:60px;">2025</td>
    </tr>
    <tr>
      <td style="width:130px;">Post Applied for</td>
      <td colspan="3"><b>{{position}}</b></td>
      <td>Grade Group</td>
      <td>&nbsp;</td>
    </tr>
    <tr>
      <td>Div. / Dept.</td>
      <td colspan="3"><b>{{department}}</b></td>
      <td>Post Location</td>
      <td>&nbsp;</td>
    </tr>
    <tr>
      <td>Contractual</td>
      <td colspan="3">☐ YES &nbsp;&nbsp; ☑ NO</td>
      <td>Contract Name</td>
      <td>&nbsp;</td>
    </tr>
    <tr>
      <td>Contract Period</td>
      <td>From</td>
      <td>&nbsp;</td>
      <td>To</td>
      <td>Job No.</td>
      <td>83001</td>
    </tr>
    <tr>
      <td>Reporting to</td>
      <td colspan="3">{{reporting_to}}</td>
      <td>Staff No.</td>
      <td>&nbsp;</td>
    </tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="6">Brief (Recruitment)</td></tr>
    <tr>
      <td style="width:130px;">New Appointment</td>
      <td>☑ YES</td>
      <td>☐ NO</td>
      <td colspan="3">Replacement for Staff No. ___________</td>
    </tr>
    <tr>
      <td>Candidate Referred</td>
      <td>☐ Client</td>
      <td>☐ Consultancy</td>
      <td>☑ Direct</td>
      <td colspan="2">☐ Staff Number</td>
    </tr>
    <tr>
      <td>Consultancy Reg.</td>
      <td>☐ Voltech HR</td>
      <td>☐ Zen</td>
      <td>☐ Trehan</td>
      <td>☐ Sinclus</td>
      <td>☐ ALYousuf / ☐ Others</td>
    </tr>
    <tr>
      <td>Employment Contract</td>
      <td colspan="5">☐ Temporary ______ Months &nbsp;&nbsp; ☑ Permanent (Two years basis)</td>
    </tr>
    <tr>
      <td colspan="6">Does the Candidate have any relation working in the Company? ☐ YES &nbsp; ☑ NO<br/>
      If YES, mention Name: __________ ; Staff No: ______ ; Work Location: __________</td>
    </tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="4">Summary of Resume</td></tr>
    <tr><td>Application Date:</td><td>{{application_date}}</td><td>Interview Date:</td><td>{{interview_date}}</td></tr>
    <tr><td>Name of Applicant:</td><td><b>{{candidate_name}}</b></td><td>Nationality:</td><td>{{nationality}}</td></tr>
    <tr><td>Present Employer:</td><td>{{present_employer}}</td><td colspan="2">Local Transfer: ☑ YES &nbsp; ☐ NO</td></tr>
    <tr><td>Marital Status:</td><td colspan="3">☐ Single &nbsp; ☑ Married &nbsp; ☐ Divorced &nbsp; ☐ Widow &nbsp; ☐ Other</td></tr>
    <tr><td>Date of Birth:</td><td>{{dob}}</td><td>Place of Birth:</td><td>{{birth_place}}</td></tr>
    <tr><td>Qualification (Academic):</td><td colspan="3">Master of Business Administration &nbsp; / &nbsp; Professional/Technical: __________</td></tr>
    <tr><td>Experience:</td><td>Local: __________</td><td colspan="2">Overseas: __________</td></tr>
    <tr><td>Languages:</td><td colspan="3">☐ Arabic &nbsp; ☑ English &nbsp; ☐ Others &nbsp;&nbsp; Driving License: ☐ Omani ☐ GCC ☐ Other</td></tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="4">SALARY RECOMMENDATION</td></tr>
    <tr style="background:#f6f6f6; font-weight:bold;">
      <td>Salary OMR — ☑ Budgeted R.O. &nbsp; ☐ Not Budgeted &nbsp; ☐ Contractual</td>
      <td>Proposed</td><td>HRC Suggestion</td><td>CEO Approval</td>
    </tr>
    <tr><td>Basic Salary</td><td>{{basic_salary}}</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>HRA (Inc. E&amp;W, Tel. &amp; GSM)</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Transport Allowance</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Additional Responsibility Allowance</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Overtime Allowance</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>FOOD ALLOWANCE</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Living Standard Allowance (LSA)<br/>
      ☐ RO 50 (&lt;300) &nbsp; ☐ RO (301–500) &nbsp; ☐ RO 30 (501–999) &nbsp; ☐ RO 20 (1000 &amp; Above)<br/>
      <i>LSA calculated as per Basic salary</i></td>
      <td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr style="font-weight:bold;"><td>Gross Salary →</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
  </table>

  <p style="font-size:10px;">* This allowance is part of gross salary and can be dissolved to adjust in basic and allowances during any compensation restructuring.</p>

  <div style="margin-top:6px;">
    <b>Notes:</b>
    <ul style="margin:4px 0 0 18px; padding:0;">
      <li>☐ Contract Period: ______ to ______ (Two years basis / Short Period)</li>
      <li>☑ Air passage Sector: From ______ to ______ (Entitlement: ☑ 12 months / ☐ 24 months)</li>
      <li>☐ Family status (Wife, 2 children up to 18 years age) &nbsp; ☑ Bachelor status</li>
      <li>☑ Medical (as per Company's medical insurance policy and Oman Labour Law)</li>
      <li>☐ Increase Salary by RO ___ after ☐ 3 or ☐ 6 months in ☐ RO ___ in basic / ☐ RO ___ in Addl. Resp. Allow.</li>
    </ul>
    <p>HOD's Comments (if any): ______________________________________________________</p>
  </div>

  <table border="1" cellspacing="0" cellpadding="6" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="3">Approvals by Circular – HRC</td></tr>
    <tr><td>Project Director</td><td>Member</td><td>__________________________</td></tr>
    <tr><td>Head Of Department</td><td>Member</td><td>__________________________</td></tr>
    <tr><td>Chief Operation Officer</td><td>Member</td><td>__________________________</td></tr>
    <tr><td>Legal Advisor</td><td>Member</td><td>__________________________</td></tr>
    <tr><td>General Manager HR&amp;A</td><td>Member</td><td>__________________________</td></tr>
  </table>

  <p>Remarks (if any): ______________________________________________________</p>

  <table border="1" cellspacing="0" cellpadding="10" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="2">FINAL APPROVAL</td></tr>
    <tr style="text-align:center;">
      <td><br/><br/>__________________________<br/><b>Chief Financial Officer</b><br/>HRC Chairman</td>
      <td><br/><br/>__________________________<br/><b>Chief Executive Officer</b></td>
    </tr>
  </table>

  <p style="font-size:10px; margin-top:6px;">
    Note: 1) "S&amp;O" Grade (Expat.) final approval by the Head of HR.<br/>
    2) Any change in this form must be signed by any 3 members at least, otherwise it is considered as void.
  </p>
  <p style="font-size:9px; text-align:right;">HR&amp;A/EPF/V3/R/July 2022</p>
</div>
"""


EMPLOYMENT_PROPOSAL_SOM = """
<div style="font-family: Arial, sans-serif; font-size: 11px; color:#000; max-width:760px; margin:auto;">
  <div style="text-align:center; font-weight:bold;">
    <div style="font-size:13px;">الشركة الوطنية العمانية للهندسة و الاستثمار ( ش م ع ع )</div>
    <div style="font-size:13px;">Oman National Engineering &amp; Investment Company (SAOG)</div>
    <div style="font-size:14px; margin-top:6px;">EMPLOYMENT PROPOSAL FORM</div>
    <div style="font-size:12px;">("S-O-M" Grade — Contractual)</div>
    <div style="text-align:right; font-size:11px;">Date: __________ &nbsp; 2022</div>
  </div>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:10px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="4">General</td></tr>
    <tr><td>Post Applied for</td><td>{{position}}</td><td>Grade Group</td><td>&nbsp;</td></tr>
    <tr><td>Div. / Dept.</td><td>{{department}}</td><td>Post Location</td><td>&nbsp;</td></tr>
    <tr><td>Contractual</td><td>☐ YES &nbsp; ☐ NO</td><td>Contract Name</td><td>&nbsp;</td></tr>
    <tr><td>Contract Period</td><td>From _____ To _____</td><td>Job No.</td><td>&nbsp;</td></tr>
    <tr><td>Reporting to</td><td>{{reporting_to}}</td><td>Staff No. / GSM / CPN No.</td><td>&nbsp;</td></tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="6">Brief (Recruitment)</td></tr>
    <tr><td>New Appointment</td><td>☐ YES</td><td>☐ NO</td><td colspan="3">Replacement for Staff No. ______</td></tr>
    <tr><td>Candidate Referred</td><td>☐ Client</td><td>☐ Consultancy</td><td>☐ Direct</td><td colspan="2">☐ Staff Number</td></tr>
    <tr><td>Consultancy Reg.</td><td>☐ Voltech HR</td><td>☐ Zen</td><td>☐ Trehan</td><td>☐ Sinclus</td><td>☐ ALYousuf / ☐ Others</td></tr>
    <tr><td>Employment Contract</td><td colspan="5">☐ Temporary _____ Months &nbsp; ☐ Permanent (______)</td></tr>
    <tr><td colspan="6">Does the Candidate have any relation working in the Company? ☐ YES &nbsp; ☐ NO<br/>If YES, mention Name: ______ ; Staff No: ______ ; Work Location: ______</td></tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="4">Summary of Resume</td></tr>
    <tr><td>Application Date:</td><td>{{application_date}}</td><td>Interview Date:</td><td>{{interview_date}}</td></tr>
    <tr><td>Name of Applicant:</td><td><b>{{candidate_name}}</b></td><td>Nationality:</td><td>{{nationality}}</td></tr>
    <tr><td>Present Employer:</td><td>{{present_employer}}</td><td colspan="2">Local Transfer: ☐ YES ☐ NO</td></tr>
    <tr><td>Marital Status:</td><td colspan="3">✓ Single &nbsp; ☐ Married &nbsp; ☐ Divorced &nbsp; ☐ Widow &nbsp; ☐ Other</td></tr>
    <tr><td>Date of Birth:</td><td>{{dob}}</td><td>Place of Birth:</td><td>{{birth_place}}</td></tr>
    <tr><td>Qualification (Academic):</td><td colspan="3">__________ &nbsp; Professional/Technical: __________</td></tr>
    <tr><td>Experience:</td><td colspan="3">Overseas: ______ Years</td></tr>
    <tr><td>Languages:</td><td colspan="3">✓ Arabic &nbsp; ✓ English &nbsp; ☐ Others &nbsp;&nbsp; Driving License: ✓ Omani ☐ GCC ☐ Other</td></tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td colspan="4">SALARY RECOMMENDATION</td></tr>
    <tr style="background:#f6f6f6; font-weight:bold;">
      <td>Salary OMR — ☐ Budgeted &nbsp; ☐ Not Budgeted &nbsp; ☐ Contractual</td>
      <td>Proposed</td><td>HR Suggestion</td><td>Remarks</td></tr>
    <tr><td>Basic Salary</td><td>{{basic_salary}}</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>HRA (Inc. E&amp;W, Tel. &amp; GSM)</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Transport Allowance</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Addl. Resp. Allowance</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Food Allowance</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr><td>Living Standard Allowance (LSA)<br/>
      ☐ RO 50 (&lt;300) ☐ RO (301–500) ☐ RO 30 (501–999) ☐ RO 20 (1000 &amp; Above)<br/>
      <i>LSA calculated as per Basic salary</i></td>
      <td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    <tr style="font-weight:bold;"><td>Gross Salary →</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
  </table>

  <div style="margin-top:6px;">
    <b>Notes:</b>
    <ul style="margin:4px 0 0 18px; padding:0;">
      <li>☐ Contract Period: From ______ to ______ (Two years basis / Short Period)</li>
      <li>☐ Air passage Sector: From ______ to MUSCAT (Entitlement: ☐ 12 months ☐ 24 months)</li>
      <li>☐ Family status (Wife, 2 children up to 18 years age) &nbsp; ☐ Bachelor status</li>
      <li>☐ Medical (as per Company's medical insurance policy and Oman Labour Law)</li>
      <li>☐ Increase Salary by RO ___ after ☐ 3 or ☐ 6 months in ☐ RO ___ in basic / ☐ RO ___ in Addl. Resp. Allow.</li>
    </ul>
    <p>HOD's Comments (if any): ______________________________________________________</p>
  </div>

  <table border="1" cellspacing="0" cellpadding="6" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; font-weight:bold;"><td colspan="3">Approvals by Circular</td></tr>
    <tr><td>Head Of Department</td><td>Member</td><td>__________________________</td></tr>
    <tr><td>Chief Operation Officer</td><td>Member</td><td>__________________________</td></tr>
  </table>

  <p>Remarks (if any): ______________________________________________________</p>

  <table border="1" cellspacing="0" cellpadding="10" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; text-align:center; font-weight:bold;"><td>FINAL APPROVAL</td></tr>
    <tr style="text-align:center;"><td><br/><br/>__________________________<br/><b>General Manager HR&amp;A</b></td></tr>
  </table>
  <p>Comments (if any): ______________________________________________________</p>

  <p style="font-size:10px;">
    Note: 1) "S – O – M" Grade: Final approval by the Head of HR for all contractual proposals.<br/>
    2) Any change in this form must be signed by any 3 members at least, otherwise it is considered as void.
  </p>
  <p style="font-size:9px; text-align:right;">HR&amp;A/EPF-S/V4/R/July 2022</p>
</div>
"""


VISA_REQUISITION = """
<div style="font-family: Arial, sans-serif; font-size: 11px; color:#000; max-width:760px; margin:auto;">
  <div style="text-align:center; font-weight:bold;">
    <div style="font-size:13px;">الشركة الوطنية العمانية للهندسة و الاستثمار ( ش م ع ع )</div>
    <div style="font-size:13px;">Oman National Engineering &amp; Investment Company (SAOG)</div>
    <div style="font-size:14px; margin-top:6px; font-style:italic;">Visa Requisition Form</div>
    <div style="text-align:right; font-size:11px;">CV#: «CV_NO» &nbsp; Source: «Consultancy»</div>
  </div>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:10px;">
    <tr><td>Staff/Candidate Name</td><td><b>{{candidate_name}}</b></td><td>Date</td><td>{{today_date}}</td></tr>
    <tr><td>Staff No / PP No</td><td>«PP_ID_NO»</td><td>Designation</td><td>{{position}}</td></tr>
    <tr><td>Department</td><td><b>O&amp;M</b></td><td>Job No / Location</td><td>«Job_no» / «Job_Location»</td></tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; font-weight:bold;"><td colspan="2">Type of Visa (Please ✓)</td></tr>
    <tr>
      <td>☐ Short Employment Visa<br/>Months ___ (4/6/9)</td>
      <td>☐ Medical report (attested) &nbsp; ☐ Salary Details &nbsp; ☐ Photographs &nbsp; ☐ Passport copy<br/>
          ☐ Degree/Diploma attested copy (Apostle) &nbsp; ☐ Govt./Semi Govt. Document — Contract with ONEIC</td>
    </tr>
    <tr>
      <td>☑ Employment Visa</td>
      <td>☑ Medical report (attested) &nbsp; ☑ Copy of Signed offer letter &nbsp; ☑ Photographs &nbsp; ☑ Passport copy<br/>
          ☐ Degree/Diploma attested copy (Apostle)</td>
    </tr>
  </table>

  <p style="margin-top:6px;">This Candidate Visa/Post is covered under the contract / project as per the below details:</p>
  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%;">
    <tr>
      <td style="width:50%;">☑ Existing &nbsp; &nbsp; Job No: «Job_no»</td>
      <td>☐ New &nbsp; &nbsp; Job No: __________</td>
    </tr>
    <tr><td>Project Period</td><td>From «Contract_Start_Date» &nbsp; To «Contract_End_Date»</td></tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; font-weight:bold; text-align:center;">
      <td>Name of the Position</td><td>Requirement as per Contract / Manpower supply (nos)</td>
      <td>Replacement Post ☐ Y / ☐ N (if 'Y' write Staff no)</td>
      <td>Additional Post Budgeted ☐ Y / ☐ N</td>
      <td>Existing / Available (Nos)</td><td>Shortage (Nos)</td><td>Remarks</td>
    </tr>
    <tr><td>{{position}}</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>«ReplS»</td></tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr>
      <td style="width:30%;">☐ Family Visit Visa<br/><i>Mention the Relationship</i></td>
      <td>☐ Passport Copy &nbsp; ☐ Photographs &nbsp; ☐ Undertaking letter from Embassy (if necessity) &nbsp; ☐ Insurance (RO.2000 — if necessary)<br/>
          ____________________ &nbsp; Their Mother's name ____________________</td>
    </tr>
    <tr>
      <td>☐ Family Joining Visa<br/><i>Mention the Relationship</i></td>
      <td>☐ Medical report (attested) &nbsp; ☐ Passport Copy &nbsp; ☐ Photographs &nbsp; ☐ Attested Marriage Certificate &nbsp; ☐ House Rental Agreement from Municipality &nbsp; ☐ Insurance (RO.2000)<br/>
          ____________________ &nbsp; Their Mother's name ____________________</td>
    </tr>
    <tr>
      <td colspan="2">☑ Others: <b>EMPLOYMENT VISA</b> &nbsp; ☑ Passport Copy &nbsp; ☑ Photographs &nbsp; ☑ Medical report (attested)</td>
    </tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; font-weight:bold;"><td colspan="2">Undertaking for &nbsp; ☐ Visit Visa &nbsp; ☐ Family Joining Visa</td></tr>
    <tr><td colspan="2">I, ______________________ Staff No. ______ am accepting all the relevant expenses (visa charges, ticket, and medical expenses) for my ______________________ stay in Oman during the visit.</td></tr>
    <tr><td>Signature: ______________________</td><td>Date: ______________________</td></tr>
    <tr><td colspan="2"><i>Visit visa &amp; Family Joining Visa (if staff is not eligible), the undertaking is <b>Must</b>. Company is not responsible for staff's relatives insurance.</i></td></tr>
  </table>

  <p>All relevant documents are enclosed.</p>

  <table border="1" cellspacing="0" cellpadding="6" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="text-align:center;">
      <td>__________________<br/>Requester Signature</td>
      <td>__________________<br/>Date</td>
    </tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="6" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; font-weight:bold; text-align:center;"><td colspan="4">Approved by</td></tr>
    <tr style="text-align:center;">
      <td>__________________<br/>Recommended by</td>
      <td>__________________<br/>Head of Div/Dept</td>
      <td>__________________<br/>General Manager (HR&amp;A)</td>
      <td>__________________<br/>Chief Executive Officer<br/>(for HODs)</td>
    </tr>
  </table>

  <table border="1" cellspacing="0" cellpadding="4" style="border-collapse:collapse; width:100%; margin-top:6px;">
    <tr style="background:#eee; font-weight:bold;"><td colspan="2">HR &amp; Admin Department</td></tr>
    <tr><td>Family Status: ☐ YES &nbsp; ☐ NO</td><td>☐ Staff Eligibility</td></tr>
    <tr><td colspan="2">☐ Accepted &nbsp; ☐ Rejected (Basis) — ☐ Salary &nbsp; ☐ ONEIC Experience &nbsp; ☐ Grade &nbsp; ☐ HRC Approval &nbsp; ☐ Less Salary &nbsp; ☐ Less Experience</td></tr>
    <tr><td>1 — I/C Admin Completed &amp; Forwarded on: __________</td><td>2 — I/C PRO Completed on: __________</td></tr>
    <tr><td>Visa Entered on Date: __________</td><td>Visa Issued on Date: __________ &nbsp; Visa Charges: RO. ________</td></tr>
    <tr><td colspan="2">Charge to ☐ SSR Account No __________ &nbsp; ☐ Job No __________</td></tr>
  </table>

  <p style="font-size:10px; margin-top:6px;">
    ♦ Pakistani Nationalities — Enclose 2<sup>nd</sup> Page of Passport with Mother Name &nbsp;&nbsp; ♦ Incomplete forms shall not be processed
  </p>
  <p style="font-size:9px; text-align:right; font-style:italic;">HR&amp;A/010/09/R1/11/R2/14</p>
</div>
"""


OFFER_TEMPLATES = [
    {"name": "ONEIC — Employment Proposal Form (General)", "body_html": EMPLOYMENT_PROPOSAL_GENERAL},
    {"name": "ONEIC — Employment Proposal Form (S-O-M Grade Contractual)", "body_html": EMPLOYMENT_PROPOSAL_SOM},
]

VISA_TEMPLATES = [
    {"name": "ONEIC — Visa Requisition Form", "body_html": VISA_REQUISITION},
]


def seed(apps, schema_editor):
    OfferLetterTemplate = apps.get_model("recruitment", "OfferLetterTemplate")
    VisaLetterTemplate = apps.get_model("recruitment", "VisaLetterTemplate")
    for t in OFFER_TEMPLATES:
        OfferLetterTemplate.objects.update_or_create(name=t["name"], defaults={"body_html": t["body_html"], "is_active": True})
    for t in VISA_TEMPLATES:
        VisaLetterTemplate.objects.update_or_create(name=t["name"], defaults={"body_html": t["body_html"], "is_active": True})


def unseed(apps, schema_editor):
    OfferLetterTemplate = apps.get_model("recruitment", "OfferLetterTemplate")
    VisaLetterTemplate = apps.get_model("recruitment", "VisaLetterTemplate")
    OfferLetterTemplate.objects.filter(name__in=[t["name"] for t in OFFER_TEMPLATES]).delete()
    VisaLetterTemplate.objects.filter(name__in=[t["name"] for t in VISA_TEMPLATES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0022_recruitment_approval_queried_status"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
