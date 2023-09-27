import pandas as pd
import os
from typing import Optional
import logging
from shimoku_api_python.execution_logger import logging_before_and_after

logger = logging.getLogger(__name__)


class CodeGenFileHandler:

    def __init__(self, output_path: str):
        self._output_path = output_path
        if not os.path.exists(self._output_path):
            os.makedirs(self._output_path)

    @logging_before_and_after(logger.debug)
    def create_data_frame_file(self, file_name: str, data: pd.DataFrame, mapping: Optional[dict[str, str]]):
        """ Create a file for a data set. """

        if not os.path.exists(f'{self._output_path}/data'):
            os.makedirs(f'{self._output_path}/data')

        for column in data:
            if 'date' in column:
                data[column] = pd.to_datetime(data[column]).dt.strftime('%Y-%m-%dT%H:%M:%S')

        if 'orderField1' in data.columns:
            data = data.sort_values(by='orderField1')
            data = data.drop(columns=['orderField1'])

        if mapping is None:
            mapping = {column: column for column in data.columns}

        aux_data = pd.DataFrame()
        for column in mapping:
            if column in data:
                aux_data[column] = data[column]
                aux_data = aux_data.rename(columns={column: mapping[column]})
        try:
            aux_data.to_csv(
                os.path.join(f'{self._output_path}/data', f'{file_name}.csv'), index=False
            )
        except Exception as e:
            logger.error(f'Error creating file {file_name}.csv: {e}')

    @logging_before_and_after(logger.debug)
    def generate_script_file(self, script_name: str, script_code_lines: list[str]):
        with open(os.path.join(self._output_path, script_name + '.py'), 'w') as f:
            f.write('\n'.join(script_code_lines))
