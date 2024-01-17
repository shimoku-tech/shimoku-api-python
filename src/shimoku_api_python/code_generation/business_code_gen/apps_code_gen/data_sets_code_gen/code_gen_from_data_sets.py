from typing import TYPE_CHECKING, List, Dict, Tuple, Optional

from shimoku_api_python.resources.report import Report
from shimoku_api_python.resources.data_set import DataSet
from shimoku_api_python.code_generation.utils_code_gen import code_gen_from_dict, code_gen_from_list

if TYPE_CHECKING:
    from ..code_gen_from_apps import AppCodeGen


async def get_linked_data_set_info(
        self: 'AppCodeGen', report: 'Report', rds_ids_in_order: List[str]
) -> Tuple[Dict[str, DataSet], List[Tuple[str, str]]]:
    unordered_rds: List[Report.ReportDataSet] = await report.get_report_data_sets()
    rds: List[Report.ReportDataSet] = []
    for rds_id in rds_ids_in_order:
        rds.append(next(rd for rd in unordered_rds if rd['id'] == rds_id))
    referenced_data_sets = {d_id: await self._app.get_data_set(d_id) for d_id in [rd['dataSetId'] for rd in rds]}
    mappings = [(rd['dataSetId'], rd['properties']['mapping']) for rd in rds]
    return referenced_data_sets, mappings


async def code_gen_read_csv_from_data_set(data_set: DataSet, name: str) -> Optional[str]:
    """ Generate code for reading a csv file from a data set.
    :param data_set: data set to generate code from
    :param name: name of the data set
    :return: code line
    """
    reverse_columns = {}
    if data_set['columns']:
        reverse_columns = {v: k for k, v in data_set['columns'].items()}
    data_point = await data_set.get_one_data_point()
    if data_point is None:
        return None
    data_point = data_point.cascade_to_dict()
    parse_dates = []
    for key, value in data_point.items():
        if key not in reverse_columns:
            reverse_columns[key] = key
        if 'date' in key and value is not None:
            parse_dates.append(reverse_columns[key])

    return (
        f'pd.read_csv('
        f'f"{{data_folder_path}}/{name}.csv"{f", parse_dates={parse_dates}" if parse_dates else ""})'
        f'.fillna("")'
    )


async def code_gen_from_shared_data_sets(self: 'AppCodeGen') -> List[str]:
    """ Generate code for data sets that are shared between reports.
    :return: list of code lines
    """
    code_lines = []
    dfs: List[DataSet] = []
    custom: List[DataSet] = []
    for ds_id in self._code_gen_tree.shared_data_sets:
        ds = await self._app.get_data_set(ds_id)
        if ds_id in self._code_gen_tree.custom_data_sets_with_data:
            custom.append(ds)
        else:
            dfs.append(ds)
    if len(dfs) > 0 or len(custom) > 0:
        code_lines.append("shimoku_client.plt.set_shared_data(")

    if len(dfs) > 0:
        dfs_code_lines = []
        for ds in dfs:
            data_line = await code_gen_read_csv_from_data_set(ds, ds["name"])
            if data_line is not None:
                dfs_code_lines.append(f'    "{ds["name"]}": {data_line},')
        code_lines.extend([
            "    dfs={",
            *dfs_code_lines,
            "    },",
        ])
    if len(custom) > 0:
        code_lines.append('    custom_data={')
        for ds in custom:
            custom_data = self._code_gen_tree.custom_data_sets_with_data[ds["id"]]
            if isinstance(custom_data, dict):
                custom_data = code_gen_from_dict(custom_data, 8)
            else:
                custom_data = code_gen_from_list(custom_data, 8)

            code_lines.extend([
                f'        "{ds["name"]}": {custom_data[0][8:]}',
                *custom_data[1:],
            ])
        code_lines.append('    },')

    if len(dfs) > 0 or len(custom) > 0:
        code_lines.append(")")
        code_lines = [''] + code_lines

    return code_lines
