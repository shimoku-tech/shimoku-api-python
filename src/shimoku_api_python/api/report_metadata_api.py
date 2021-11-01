""""""

from typing import Dict


class ReportMetadataApi(object):
    """
    """

# TODO
    def __init__(self, api_client):
        self.api_client = api_client

    def get_report_data_fields(self, report_id: str) -> Dict:
        """
        Get report.dataFields

        Example of report field:
        --------------

        {
            "Churn class":
             {
                "field": "stringField1",
                "filterBy": [
                    "Very probable", "Probable",
                    "Improbable", "Very Improbable",
                ]
            },
            "Churn probability" : {
                "field" : "intField1",
                "filterBy": None,
                }
            },
            ...
        }
        """
        report_dict: Dict = self.get_target_report(report_id=report_id)
        try:
            result = json_util.loads(report_dict['dataFields'])
        except JSONDecodeError:
            result = literal_eval(report_dict['dataFields'])
        return result

    # TODO este probablemente se tenga que romper en muchos
    def update_report_fields(
            self, fields: str, report_id: str,
    ) -> None:
        """Update report.dataFields
        """
        table_name: str = f'Report-{self.table_name_suffix}'
        # filter_expression = 'id = :report_id'
        # filter_values = {':report_id': {'S': report_id}}
        constraints: Dict = {
            'id': {'S': report_id},
        }
        update_expression: str = f'dataFields = :dataFields'
        attribute_vals: Dict[str, str] = {
            ':dataFields': fields,
        }

        self.update_item(
            table_name=table_name, constraints=constraints,
            update_expression=update_expression,
            attribute_vals=attribute_vals,
            action="set",
        )

    def change_report_description(
        self, description: str, report_id: str,
    ) -> None:
        """Update report.Description field
        """
        table_name: str = f'Report-{self.table_name_suffix}'
        # filter_expression = 'id = :report_id'
        # filter_values = {':report_id': {'S': report_id}}
        constraints: Dict = {
            'id': {'S': report_id},
        }
        update_expression: str = f'description = :description'
        attribute_vals: Dict[str, str] = {
            ':description': description,
        }

        self.update_item(
            table_name=table_name, constraints=constraints,
            update_expression=update_expression,
            attribute_vals=attribute_vals,
            action="set",
        )

    def update_report_chart_type(self, report_id: str, report_type: str) -> None:
        """Update report.reportType
        """
        table_name: str = f'Report-{self.table_name_suffix}'
        constraints: Dict = {
            'id': {'S': report_id},
        }
        update_expression: str = f'reportType = :reportType'
        attribute_vals: Dict[str, str] = {
            ':reportType': report_type,
        }

        self.update_item(
            table_name=table_name, constraints=constraints,
            update_expression=update_expression,
            attribute_vals=attribute_vals,
            action="set",
        )

# TODO
    def update_report_external_id(self, report_id: str, new_external_id: str):
        pass

