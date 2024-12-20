from enums import Field


EXPLAINER = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""

TABS = {
    "line": {
        "label": "Time Series",
        "fields": [
            {
                "condition": lambda field: not field.temporal,
            },
            {
                "value": Field.DATE,
                "condition": lambda field: field is Field.DATE,
            },
        ],
    },
    "bar": {
        "label": "Bar",
        "fields": [{"condition": lambda field: field is not Field.DATE}, {}],
    },
    "scatter": {"label": "Scatter", "fields": [{}, {}]},
}
