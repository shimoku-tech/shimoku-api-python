""""""

from abc import ABC
from typing import List, Dict, Optional, Union

import datetime as dt

import pandas as pd
from shimoku_api_python.api.explorer_api import FileExplorerApi


class FileMetadataApi(FileExplorerApi, ABC):
    """
    """
    def __init__(self, api_client):
        self.api_client = api_client

    @staticmethod
    def _encode_file_name(
            file_name: str, date: dt.datetime, chunk: Optional[int] = None
    ) -> str:
        """Append the date and chunk to the file name"""
        return f'{file_name}_date:{date.strftime("%Y%m%d")}_chunk:{chunk}' if chunk else f'{file_name}_date:{date.strftime("%Y%m%d")}'

    @staticmethod
    def _decode_file_name(file_name: str) -> str:
        """Decode the file name into its components
        """
        file_name_date_parts: List[str] = file_name.split('_date:')
        file_name_chunk_parts: List[str] = file_name.split('_chunk:')

        if len(file_name_date_parts) == 1 and len(file_name_chunk_parts) == 1:
            return file_name
        elif len(file_name_date_parts) == 2 or len(file_name_chunk_parts) == 1:
            return file_name_date_parts[0]
        else:
            raise ValueError('Invalid file name has multiple times "_date:"')

    def _get_files_by_string_matching(
            self, business_id: str, string_match: str,
            app_name: Optional[str] = None,
    ) -> List[Dict]:
        if '_date:' in string_match or '_chunk:' in string_match:
            raise ValueError(
                'Reserved keywords "date:" and "chunk:" are not allowed in file name'
            )
# TODO pending importar
        apps: List[Dict] = self.get_business_apps(business_id)
        target_files: List[Dict] = []
        for app in apps:
            app_id: str = app['id']

            if app_name is not None:
                if app['name'] != app_name:
                    continue

            files: List[Dict] = self.get_files(business_id=business_id, app_id=app_id)
            for file_metadata in files:
                if string_match in file_metadata['name']:
                    target_files.append(file_metadata)

        return files

    def get_file_by_name(
            self, business_id: str, file_name: str,
            app_name: Optional[str] = None,
            get_file_object: bool = False,
    ) -> Union[Dict, bytes]:
        if '_date:' in file_name or '_chunk:' in file_name:
            raise ValueError(
                'Reserved keywords "date:" and "chunk:" are not allowed in file name'
            )
        apps: List[Dict] = self.get_business_apps(business_id)
        target_files: List[Dict] = []
        app_id = None
        for app in apps:
            app_id: str = app['id']

            if app_name is not None:
                if app['name'] != app_name:
                    continue

            files: List[Dict] = self.get_files(business_id=business_id, app_id=app_id)
            for file_metadata in files:
                if file_name == file_metadata['name']:
                    target_files.append(file_metadata)
                    break  # there must be only one file with the same name!

        file: Dict = target_files[0]
        if get_file_object:
            return self.get_file(
                business_id=business_id,
                app_id=app_id,
                file_id=file,
            )
        return file

    def get_file_by_date(
            self, business_id: str, datetime: dt.datetime,
            app_name: Optional[str] = None
    ):
        datetime_str: str = datetime.isoformat()
        return self._get_files_by_string_matching(
            business_id=business_id,
            string_match=datetime_str,
            app_name=app_name,
        )

    def get_files_by_name_prefix(
            self, business_id: str, name_prefix: str,
            app_name: Optional[str] = None
    ) -> List[Dict]:
        return self._get_files_by_string_matching(
            business_id=business_id,
            string_match=name_prefix,
            app_name=app_name,
        )

    def delete_file_by_name(
            self, business_id: str, file_name: str,
            app_name: Optional[str] = None,
    ):
        app: Dict = self.get_app_by_name(business_id=business_id, app_name=app_name)

        if not app:
            raise ValueError('App name not found')
        app_id: str = app['id']
        app_name: str = app['name']

        file_metadata: Dict = self.get_file_by_name(
            business_id=business_id, app_name=app_name, file_name=file_name,
        )

        self.delete_file(
            business_id=business_id,
            app_id=app_id,
            file_id=file_metadata['id'],
        )

    def replace_file_name(
            self, business_id: str, app_name: str, old_name: str, new_name: str
    ) -> Dict:
        app: Dict = self.get_app_by_name(business_id=business_id, app_name=app_name)

        if not app:
            raise ValueError('App name not found')
        app_id: str = app['id']
        app_name: str = app['name']

        file_metadata: Dict = self.get_file_by_name(
            business_id=business_id,
            app_name=app_name,
            file_name=old_name,
        )

        file_object: bytes = self.get_file(
            business_id=business_id,
            app_id=app_id,
            file_id=file_metadata['id'],
        )
        file_metadata['name'] = new_name

        file: Dict = self.create_file(
            business_id=business_id,
            app_id=app_id,
            file=file_object,
            file_metadata=file_metadata,
        )

        self.delete_file_by_name(
            business_id=business_id,
            app_name=app_name,
            file_name=old_name,
        )
        return file

    def post_dataframe(
            self, business_id: str, app_name: str, file_name: str, df: pd.DataFrame,
            force_name: bool = False, split_by_size: bool = True
    ) -> Dict:
        """
        :param business_id:
        :param app_name:
        :param file_name:
        :param df:
        :param force_name: if not forced then we add the date to the file name
        :param split_by_size: if true then we split the file by size and set it in the file name
        """
        if split_by_size:
            len_df: int = len(df)
            bytes_size_df: int = df.memory_usage(deep=True).sum()
            bytes_size_df: int = bytes_size_df / 1024 / 1024
            if bytes_size_df > 5:
# TODO split dataframe
                chunk: int =
                dataframe_binary: bytes = df.to_csv(index=False).encode('utf-8')
                final_file_name: str = self._encode_file_name(
                    file_name=file_name, date=dt.datetime.today()
                )
                self.create_file(
                    business_id=business_id,
                    app_name=app_name,
                    file_name=final_file_name,
                    file_object=dataframe_binary,
                )
            else:
                dataframe_binary: bytes = df.to_csv(index=False).encode('utf-8')
                final_file_name: str = self._encode_file_name(
                    file_name=file_name, date=dt.datetime.today()
                )
                self.create_file(
                    business_id=business_id,
                    app_name=app_name,
                    file_name=final_file_name,
                    file_object=dataframe_binary,
                )
        else:
            dataframe_binary: bytes = df.to_csv(index=False).encode('utf-8')
            final_file_name: str = self._encode_file_name(
                file_name=file_name, date=dt.datetime.today()
            )
            self.create_file(
                business_id=business_id,
                app_name=app_name,
                file_name=final_file_name,
                file_object=dataframe_binary,
            )

    def get_dataframe(
            self, business_id: str, app_name: str, file_name: str,
            parse_name: bool = True,
    ) -> pd.DataFrame:
        """
        :param business_id:
        :param app_name:
        :param file_name:
        :param parse_name: if true then we parse the file name to get the date
        """
        if parse_name:
            dataset_names: List[Dict] = (
                self.get_files_by_name_prefix(
                    business_id=business_id,
                    app_name=app_name,
                    name_prefix=file_name,
                )
            )

            df = pd.DataFrame()
            for dataset_name in dataset_names:
                dataset_binary: bytes = self.get_file_by_name(
                    business_id=business_id,
                    app_name=app_name,
                    file_name=dataset_name['name'],
                    get_file_object=True,
                )
                df = df.append(pd.read_csv(dataset_binary.decode('utf-8')))
        else:
            dataset_binary: bytes = self.get_file_by_name(
                business_id=business_id,
                app_name=app_name,
                file_name=file_name,
                get_file_object=True,
            )
            return pd.read_csv(dataset_binary.decode('utf-8'))
