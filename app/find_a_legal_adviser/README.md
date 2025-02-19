# Mini FALA (Find a Legal Adviser)

This surfaces a list of legal aid providers from the Legal Aid Agency Legal Adviser API (LAALAA).

If the user is deemed out of scope for Civil Legal Advice, but in-scope for Civil Legal Aid they will be direted to the
mini FALA search page with the category pre-populated in the query string.

The user will then enter their postcode, or a section of a postcode, and be shown a sorted list of legal aid providers near to them
who can provide the service they need.


## Query strings
`category` - The category of law the user is looking for help with.
This can any valid LAALAA category code, though should be lowercase.

`postcode` - The postcode the user searches for. If this is included the results page should display

`page` - The search page the user is on, this defaults to 1.
