from typing import Optional, List, Tuple, Dict

from shimoku_api_python.resources.app import App
from shimoku_api_python.resources.data_set import DataSet
from shimoku_api_python.resources.report import Report
from shimoku_api_python.resources.reports.modal import Modal
from shimoku_api_python.resources.reports.tabs_group import TabsGroup
from shimoku_api_python.utils import change_data_set_name_with_report

from shimoku_api_python.code_generation.file_generator import CodeGenFileHandler

import tqdm
import pandas as pd
import asyncio

import logging
from shimoku_api_python.execution_logger import logging_before_and_after

logger = logging.getLogger(__name__)


class CodeGenTree:
    """ Class for generating code generation tree. """

    def __init__(self, app: App, file_generator: CodeGenFileHandler, pbar: Optional[tqdm.tqdm] = None):
        self._app = app
        self._file_generator = file_generator
        self._pbar = pbar
        self.custom_data_sets_with_data = {}
        self.actual_bentobox: Optional[Dict] = None
        self.all_tab_groups: Dict[str, List[dict]] = {}
        self.tree: Optional[dict] = None
        self.shared_data_sets: List[str] = []
        self.needs_pandas: bool = False

    def _update_pbar(self, n: int = 1):
        if self._pbar is not None:
            self._pbar.update(n)

    @logging_before_and_after(logger.debug)
    async def _check_for_shared_data_sets(
            self, report: Report, seen_data_sets: set, individual_data_sets: Dict[str, Report]
    ):
        """ Check for shared data sets in a report.
            :param report: report to check
            :param seen_data_sets: set of data sets already seen
            :param individual_data_sets: list of data sets to append to
            """
        report_data_sets: List[Report.ReportDataSet] = await report.get_report_data_sets()
        data_sets_from_rds = set([rds['dataSetId'] for rds in report_data_sets])

        for ds_id in data_sets_from_rds:
            if ds_id in self.shared_data_sets:
                continue
            if ds_id in seen_data_sets:
                self.shared_data_sets.append(ds_id)
                del individual_data_sets[ds_id]
            else:
                individual_data_sets[ds_id] = report
                seen_data_sets.add(ds_id)

    async def _check_for_create_data_set(self, data_set: DataSet, report: Optional[Report] = None):
        """ Create a file for a data set.
        :param data_set: data set to create file for
        :param report: report to create file for
        """
        if data_set['name'] is None:
            data_set['name'] = data_set['id']

        data: List[dict] = [
            {k: v for k, v in dp.cascade_to_dict().items()
             if k not in ['id', 'dataSetId'] and v is not None}
            for dp in await data_set.get_data_points()
        ]

        if len(data) == 0:
            return

        data_as_df = pd.DataFrame(data)

        if len(data) > 1 or 'customField1' not in data[0]:
            output_name = data_set["name"] if report is None else change_data_set_name_with_report(data_set, report)
            reverse_columns = {v: k for k, v in data_set['columns'].items()} if data_set['columns'] else None
            self._file_generator.create_data_frame_file(output_name, data_as_df, reverse_columns)
            self.needs_pandas = True
        else:
            self.custom_data_sets_with_data[data_set['id']] = data[0]['customField1']

    @logging_before_and_after(logger.debug)
    async def _get_data_sets(self):
        """ Create files for the data sets. """
        reports = await self._app.get_reports()

        # To store the data sets in the cache for the reports to have faster access to them
        await self._app.get_data_sets()

        individual_data_sets: Dict[str, Report] = {}
        seen_data_sets = set()

        await asyncio.gather(*[self._check_for_shared_data_sets(report, seen_data_sets, individual_data_sets)
                               for report in reports])
        tasks = []
        for ds_id in self.shared_data_sets:
            tasks.append(self._check_for_create_data_set(await self._app.get_data_set(ds_id)))
        for ds_id, report in individual_data_sets.items():
            tasks.append(self._check_for_create_data_set(await self._app.get_data_set(ds_id), report))
        await asyncio.gather(*tasks)

    @logging_before_and_after(logger.debug)
    async def _tree_from_tabs_group(
            self, tree: list, tabs_group: TabsGroup, parent_tabs_index: Tuple[str, str] = None
    ):
        """ Recursively build a tree of reports from a tabs group.
        :param tree: list to append to
        :param tabs_group: tabs group to build tree from
        :param parent_tabs_index: tuple of (tabs_group hash, tab name) of parent tabs group
        """
        path = tabs_group['path'] + '_' if tabs_group['path'] else ''
        name = tabs_group['properties']['hash'][len(path):]
        tabs_group_dict = {'tabs_group': tabs_group, 'tabs': {}, 'order': tabs_group['order'],
                           'parent_tabs_index': parent_tabs_index, 'name': name}

        path = tabs_group['path']
        if path not in self.all_tab_groups:
            self.all_tab_groups[path] = []
        self.all_tab_groups[path].insert(0, tabs_group_dict)

        tree.append(tabs_group_dict)
        tabs = sorted(tabs_group['properties']['tabs'].items(), key=lambda x: x[1]['order'])
        for tab, tab_data in tabs:
            report_ids = tab_data['reportIds']
            tab_dict = {'tab_groups': [], 'other': []}
            tabs_group_dict['tabs'][tab] = tab_dict
            for child_id in report_ids:
                child_report = await self._app.get_report(child_id)
                if child_report['reportType'] == 'TABS':
                    await self._tree_from_tabs_group(
                        tab_dict['tab_groups'], child_report, (tabs_group['properties']['hash'], tab))
                else:
                    tab_dict['other'].append(child_report)
                self._update_pbar()

            tab_dict['tab_groups'] = sorted(tab_dict['tab_groups'], key=lambda x: x['tabs_group']['order'])
            tab_dict['other'] = sorted(tab_dict['other'], key=lambda x: x['order'])

    @logging_before_and_after(logger.debug)
    async def _tree_from_modal(self, tree: list, modal: Modal):
        """ Recursively build a tree of reports from a modal.
        :param self: PlotApi instance
        :param tree: list to append to
        :param modal: modal to build tree from
        """
        path = modal['path'] + '_' if modal['path'] else ''
        name = modal['properties']['hash'][len(path):]
        modal_dict = {'modal': modal, 'tab_groups': [], 'other': [], 'name': name}
        tree.append(modal_dict)
        for child_id in modal['properties']['reportIds']:
            child_report = await self._app.get_report(child_id)
            if child_report['reportType'] == 'TABS':
                await self._tree_from_tabs_group(modal_dict['tab_groups'], child_report)
            else:
                modal_dict['other'].append(child_report)
            self._update_pbar()

        modal_dict['tab_groups'] = sorted(modal_dict['tab_groups'], key=lambda x: x['tabs_group']['order'])
        modal_dict['other'] = sorted(modal_dict['other'], key=lambda x: x['order'])

    @logging_before_and_after(logger.debug)
    async def generate_tree(self):
        """ Generate a tree of reports from a list of reports.
        :param self: PlotApi instances
        """
        self.tree = {}
        reports = await self._app.get_reports()
        contained_reports = set()
        for report in reports:
            # TODO: make this not necessary
            if 'hash' not in report['properties']:
                report['properties']['hash'] = 'id_' + report['id']
            if report['reportType'] == 'MODAL':
                contained_reports.update(report['properties']['reportIds'])
            elif report['reportType'] == 'TABS':
                for tab in report['properties']['tabs']:
                    contained_reports.update(report['properties']['tabs'][tab]['reportIds'])
        reports = sorted(
            reports,
            key=lambda x: (x['pathOrder'] if x['pathOrder'] else 0,
                           '0' if x['reportType'] == 'MODAL' else
                           '1' if x['reportType'] == 'TABS' else
                           '_' + (x['properties']['hash'])),
        )
        for report in reports:

            if report['id'] in contained_reports:
                continue

            if report['path'] not in self.tree:
                self.tree[report['path']] = {'modals': [], 'tab_groups': [], 'other': []}

            if report['reportType'] == 'MODAL':
                await self._tree_from_modal(self.tree[report['path']]['modals'], report)
            elif report['reportType'] == 'TABS':
                await self._tree_from_tabs_group(self.tree[report['path']]['tab_groups'], report)
            else:
                self.tree[report['path']]['other'].append(report)

            self._update_pbar()

        for path in self.tree:
            self.tree[path]['other'] = sorted(self.tree[path]['other'], key=lambda x: x['order'])
            self.tree[path]['tab_groups'] = sorted(self.tree[path]['tab_groups'],
                                                   key=lambda x: x['tabs_group']['order'])

        # Todo: Solve path ordering
        # self.tree = {k: v for k, v in sorted(reports.items(), key=lambda item: }
        await self._get_data_sets()
