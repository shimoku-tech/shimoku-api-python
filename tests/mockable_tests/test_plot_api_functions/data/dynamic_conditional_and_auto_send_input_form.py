form_groups = {
    f"form group {i}": [
        {
            "mapping": "country",
            "fieldName": f"Country {i}",
            "inputType": "select",
            "options": ["España", "Colombia"],
        },
        {
            "dependsOn": f"Country {i}",
            "mapping": "city",
            "fieldName": f"City {i}",
            "inputType": "select",
            "options": {
                "España": ["Madrid", "Barcelona"],
                "Colombia": ["Bogotá", "Medellin"],
            },
        },
    ]
    for i in range(4)
}

form_groups["Personal information"] = [
    {
        "mapping": "name",
        "fieldName": "name",
        "inputType": "text",
    },
    {
        "mapping": "surname",
        "fieldName": "surname",
        "inputType": "text",
    },
    {
        "mapping": "age",
        "fieldName": "age",
        "inputType": "number",
    },
    {
        "mapping": "tel",
        "fieldName": "phone",
        "inputType": "tel",
    },
    {
        "mapping": "gender",
        "fieldName": "Gender",
        "inputType": "radio",
        "options": ["Male", "Female", "No-binary", "Undefined"],
    },
    {
        "mapping": "email",
        "fieldName": "email",
        "inputType": "email",
    },
]

form_groups["Other data"] = [
    {
        "mapping": "skills",
        "fieldName": "Skills",
        "options": ["Backend", "Frontend", "UX/UI", "Api Builder", "DevOps"],
        "inputType": "checkbox",
    },
    {
        "mapping": "birthDay",
        "fieldName": "Birthday",
        "inputType": "date",
    },
    {
        "mapping": "onCompany",
        "fieldName": "time on Shimoku",
        "inputType": "dateRange",
    },
    {
        "mapping": "hobbies",
        "fieldName": "Hobbies",
        "inputType": "select",
        "options": ["Make Strong Api", "Sailing to Canarias", "Send Abracitos"],
    },
    {
        "mapping": "textField2",
        "fieldName": "Test Text",
        "inputType": "text",
    },
    {
        "mapping": "objectives",
        "fieldName": "Objetivos",
        "inputType": "multiSelect",
        "options": ["sleep", "close eyes", "awake"],
    },
]
