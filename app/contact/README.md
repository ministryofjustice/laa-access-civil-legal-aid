# Contact Pages

The contact page is currently a placeholder for further development. It can be used in routes either via next_step_mapping or a routing_map:

```python
    next_step_mapping/routing_map = {
        "selection": "contact.contact_us",
    }
```

Views currently inherit from the `CategoryPage` from categories. A page can be registered with the contact section by adding the following to a blueprint:

```python
bp.add_url_rule('/url_endpoint', view_func=CategoryPage.as_view('page_name', template='template.html'))
```


## Reasons for contacting

The reason for contacting form is a direct contact method on Access Civil Legal Aid. The initial form submission adds to the database using the post_reasons_for_contacting function with the information defined via the api_payload function:

```python
    def api_payload(self):
        return {
            "reasons": [{"category": category} for category in self.reasons.data],
            "other_reasons": "",
            "user_agent": request.headers.get("User-Agent") or "Unknown",
            "referrer": self.referrer.data or "Unknown",
        }
```

The reasons-for-contacting route handles the previous referrer via a get request.