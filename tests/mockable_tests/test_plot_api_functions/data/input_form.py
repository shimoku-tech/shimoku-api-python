input_form_data = {
    "fields": [
        {
            "title": "Personal information",
            "fields": [
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
            ],
        },
        {
            "title": "Other data",
            "fields": [
                {
                    "mapping": "skills",
                    "fieldName": "Skills",
                    "options": [
                        "Backend",
                        "Frontend",
                        "UX/UI",
                        "Api Builder",
                        "DevOps",
                    ],
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
                    "options": [
                        "Make Strong Api",
                        "Sailing to Canarias",
                        "Send Abracitos",
                    ],
                },
                {
                    "mapping": "textField2",
                    "fieldName": "Test Text",
                    "inputType": "text",
                },
            ],
        },
    ],
}
