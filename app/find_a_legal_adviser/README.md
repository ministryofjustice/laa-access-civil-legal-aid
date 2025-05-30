# Find a legal aid adviser (FALA)
When users are eligible for Civil Legal Aid but out of scope for Civil Legal Advice they are signposted to  find a legal aid adviser, a service which allows users to search for nearby legal aid providers that provide services for their category of law.

As check if you can get legal aid is responsible for diagnosing users' category of law we direct users to a version of  find a legal aid adviser with the category pre-selected where appropriate. 

Additionally, a sub category may be included, where appropriate, which results in additional providers being appended to the search results.

This version of FALA is found at: https://find-legal-advice.justice.gov.uk/check

This endpoint supports the following query string parameters:

- `categories=<laalaa_category>`
- `sub-category=<laalaa_category>`

Where `laalaa_category` is one of:
- `MOSL` (Modern Slavery)
- `MED` (Clinical Negligence)
- `PUB` (Public Law)
- `MHE` (Mental Health)
- `COM` (Community Care)
- `DEB` (Debt)
- `WB` (Welfare Benefits)
- `HLPAS` (Housing Loss Prevention Advice Service)
- `FMED` (Family Mediation)
- `DISC` (Discrimination)
- `AAP` (Claims Against Public Authorities)
- `EDU` (Education)
- `MAT` (Family)
- `IMMAS` (Immigration or asylum)
- `HOU` (Housing)
- `PL` (Prison law)
- `CRM` (Crime)
