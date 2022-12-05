""""""

from abc import ABC
from typing import List, Dict, Optional, Union, Any, Callable
import re
from io import StringIO
import pickle

import datetime as dt

import pandas as pd
from shimoku_api_python.api.explorer_api import FileExplorerApi, BusinessExplorerApi


class BasicFileMetadataApi(FileExplorerApi, ABC):
    """
    """
    _get_business = BusinessExplorerApi.get_business

    def __init__(self, api_client, **kwargs):
        self.api_client = api_client

        if kwargs.get('business_id'):
            self.business_id: Optional[str] = kwargs['business_id']
        else:
            self.business_id: Optional[str] = None

    @staticmethod
    def _encode_file_name(
            file_name: str, date: dt.date, chunk: Optional[int] = None
    ) -> str:
        """Append the date and chunk to the file name"""
        return (
            f'{file_name}_date:{date.isoformat()}_chunk:{chunk}'
            if chunk is not None else f'{file_name}_date:{date.isoformat()}'
        )

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
            raise ValueError('Invalid file name has multiple times "_date:" or "_chunk:"')

    @staticmethod
    def _get_file_date(file_name: str) -> Optional[dt.date]:
        try:
            date_iso: str = file_name.split('_date:')[1].split('_chunk:')[0]
        except IndexError:
            return None
        return dt.datetime.strptime(date_iso, '%Y-%m-%d').date()

    # TODO applies only to dataframes
    def _get_file_chunk(self):
        raise NotImplementedError('Not implemented yet')

    def _get_files_by_string_matching(
            self, string_match: str,
            app_name: Optional[str] = None,
            allow_reserved_words: bool = False,
    ) -> List[Dict]:
        if not allow_reserved_words:
            if '_date:' in string_match or '_chunk:' in string_match:
                raise ValueError(
                    'Reserved keywords "_date:" and "chunk:" are not allowed in file name'
                )

        apps: List[Dict] = self._get_business_apps(self.business_id)
        target_files: List[Dict] = []
        for app in apps:
            app_id: str = app['id']

            if app_name is not None:
                if app['name'] != app_name:
                    continue

            files: List[Dict] = self.get_files(business_id=self.business_id, app_id=app_id)
            for file_metadata in files:
                if string_match in file_metadata['name']:
                    target_files.append(file_metadata)

        return target_files

    def set_business(self, business_id: str):
        """"""
        # If the business id does not exists it raises an ApiClientError
        _ = self._get_business(business_id)
        self.business_id: str = business_id

    def get_files_by_name_prefix(
            self, name_prefix: str,
            app_name: Optional[str] = None,
            allow_reserved_words: bool = False,
    ) -> List[Dict]:
        target_files: List[Dict] = list()
        files: List[Dict] = self._get_files_by_string_matching(
            string_match=name_prefix,
            app_name=app_name,
            allow_reserved_words=allow_reserved_words,
        )
        for file in files:
            if file['name'].startswith(name_prefix):
                target_files.append(file)
        return target_files

    def get_file_by_name(
            self, file_name: str,
            app_name: Optional[str] = None,
            get_file_object: bool = False,
            force_name: bool = False,
    ) -> Union[Dict, bytes]:
        if not force_name:
            if '_date:' in file_name or '_chunk:' in file_name:
                raise ValueError(
                    'Reserved keywords "_date:" and "chunk:" are not allowed in file name'
                )

        apps: List[Dict] = self._get_business_apps(self.business_id)
        target_files: List[Dict] = []
        app_id = None
        for app in apps:
            app_id: str = app['id']

            if app_name is not None:
                if app['name'] != app_name:
                    continue

            files: List[Dict] = self.get_files(business_id=self.business_id, app_id=app_id)
            for file_metadata in files:
                if file_name == file_metadata['name']:
                    target_files.append(file_metadata)
                    break  # there must be only one file with the same name!
            break

        try:
            file: Dict = target_files[0]
        except IndexError:
            raise ValueError(f'File not found | file_name: {file_name}')

        if get_file_object:
            return self._get_file(
                business_id=self.business_id,
                app_id=app_id,
                file_id=file['id'],
            )
        return file

    def delete_files_by_name_prefix(
            self, name_prefix: str,
            app_name: Optional[str] = None,
    ):
        app: Dict = self._get_app_by_name(business_id=self.business_id, name=app_name)
        if not app:
            raise ValueError(f'App not found | App name: {app_name}')

        app_id: str = app['id']
        app_name: str = app['name']

        files_metadata: List[Dict] = self.get_files_by_name_prefix(
            app_name=app_name,
            name_prefix=name_prefix,
        )

        for file_metadata in files_metadata:
            self._delete_file(
                business_id=self.business_id,
                app_id=app_id,
                file_id=file_metadata['id'],
            )

    def post_object(
            self, app_name: str,
            file_name: str,
            object_data: bytes,
            overwrite: bool = True,
            force_name: bool = False,
            content_type: str = 'text/csv',
            date: Optional[dt.date] = dt.date.today(),
    ) -> Dict:
        app: Dict = self._get_app_by_name(business_id=self.business_id, name=app_name)
        if not app:
            raise ValueError(f'App not found | App name: {app_name}')

        app_id: str = app['id']

        if force_name:
            final_file_name: str = file_name
        else:
            final_file_name: str = self._encode_file_name(
                file_name=file_name, date=date,
            )

        file_metadata = {
            'name': final_file_name,
            'fileName': re.sub('[^0-9a-zA-Z]+', '-', final_file_name).lower(),
            'contentType': content_type,
        }

        if overwrite:
            app: Dict = self._get_app_by_name(business_id=self.business_id, name=app_name)
            if not app:
                raise ValueError(f'App not found | App name: {app_name}')

            fs: List[Dict] = self.get_files_by_name_prefix(
                app_name=app_name,
                name_prefix=file_metadata['name'],
                allow_reserved_words=True
            )
            for f in fs:
                self._delete_file(
                    business_id=self.business_id,
                    app_id=app['id'],
                    file_id=f['id'],
                )

        return self._create_file(
            business_id=self.business_id,
            app_id=app_id,
            file_metadata=file_metadata,
            file_object=object_data,
        )


class FileMetadataApi(BasicFileMetadataApi, ABC):
    """
    """
    def __init__(self, api_client, **kwargs):
        super().__init__(api_client, **kwargs)

        if kwargs.get('business_id'):
            self.business_id: Optional[str] = kwargs['business_id']
        else:
            self.business_id: Optional[str] = None

    def set_business(self, business_id: str):
        super().set_business(business_id)

    def get_all_files_by_app_name(self, app_name: str) -> List[Dict]:
        """"""
        apps: List[Dict] = self._get_business_apps(self.business_id)
        files: List[Dict] = []
        for app in apps:
            app_id: str = app['id']

            if app['name'] != app_name:
                continue

            files: List[Dict] = self.get_files(business_id=self.business_id, app_id=app_id)
            break
        return files

    def get_all_files_by_creation_date(
            self, datetime: dt.datetime,
            app_name: Optional[str] = None,
            force_name: bool = False,
    ) -> List[Dict]:
        """Get all files from a target creation date"""
        raise NotImplementedError

    def get_file_by_creation_date(
            self, file_name: str,
            date: dt.date,
            app_name: Optional[str] = None,
            get_file_object: bool = False,
    ) -> Any:
        """Get a specific file from a target creation date"""
        raise NotImplementedError

    def get_last_created_target_file(
            self, file_name: str,
            app_name: Optional[str] = None,
    ) -> Dict:
        """Get a specific file from a target creation date"""
        raise NotImplementedError

    def get_all_files_by_date(
            self, date: dt.date,
            app_name: Optional[str] = None,
    ) -> List[Dict]:
        """Get all files from a target date"""
        datetime_str: str = date.isoformat()
        return self._get_files_by_string_matching(
            string_match=datetime_str,
            app_name=app_name,
        )

    def get_file_by_date(
            self, file_name: str,
            date: dt.date,
            app_name: Optional[str] = None,
            get_file_object: bool = False,
    ) -> Any:
        """Get a specific file from a target date"""
        files: List[Dict] = self.get_files_by_name_prefix(
            app_name=app_name,
            name_prefix=file_name,
        )

        target_files: List[Dict] = [
            file for file in files
            if self._get_file_date(file['name']) == date
        ]

        # Chunks are only allowed for tabular data use get_dataframe() instead!
        len_target_files = len(target_files)
        if len_target_files == 0:
            if get_file_object:  # return Object
                return None
            else:
                return {}
        elif len_target_files >= 1:
            if get_file_object:  # return List[Object]
                try:
                    app: Dict = [
                        app for app in self._get_business_apps(self.business_id)
                        if app['name'] == app_name
                    ][0]
                except IndexError:
                    raise ValueError(f'App not found | app_name: {app_name}')

                results: List[bytes] = []
                for file in target_files:
                    result = self._get_file(
                        business_id=self.business_id,
                        app_id=app['id'],
                        file_id=file['id'],
                    )
                    results = results + [result]
                return results
            else:  # return List[Dict]
                return target_files
        else:
            raise ValueError('Multiple files found for the same date')

    def get_files_with_max_date(
            self, file_name: str,
            app_name: Optional[str] = None,
            get_file_object: bool = False,
    ) -> Any:
        """Get a specific file with maximum date"""
        app: Dict = self._get_app_by_name(business_id=self.business_id, name=app_name)
        if not app:
            raise ValueError(f'App not found | App name: {app_name}')

        files: List[Dict] = self.get_files_by_name_prefix(
            name_prefix=file_name,
            app_name=app_name,
        )
        target_files: List[Dict] = []
        max_date: dt.date = dt.date(2000, 1, 1)
        for file in files:
            try:
                new_date: Optional[dt.date] = self._get_file_date(file['name'])
            except ValueError:
                continue

            if new_date is None:
                continue

            if new_date > max_date:
                target_files = [file]
                max_date = new_date
            elif new_date == max_date:
                target_files = target_files + [file]

        if get_file_object:  # return List[bytes]
            results: List[bytes] = []
            for target_file in target_files:
                result = self._get_file(
                    business_id=self.business_id,
                    app_id=app['id'],
                    file_id=target_file['id'],
                )
                results = results + [result]
            return results
        else:  # return Dict
            return target_files

    # TODO pending implementation
    def replace_file_name(
            self, app_name: str, old_name: str, new_name: str
    ) -> Dict:
        """
        app: Dict = self._get_app_by_name(business_id=self.business_id, name=app_name)

        if not app:
            raise ValueError('App name not found')
        app_id: str = app['id']
        app_name: str = app['name']

        file_metadata: Dict = self.get_file_by_name(
            business_id=self.business_id,
            app_name=app_name,
            file_name=old_name,
        )

        file_object: bytes = self._get_file(
            business_id=self.business_id,
            app_id=app_id,
            file_id=file_metadata['id'],
        )
        file_metadata['name'] = new_name

        file: Dict = self._create_file(
            business_id=self.business_id,
            app_id=app_id,
            file=file_object,
            file_metadata=file_metadata,
        )

        self.delete_files_by_name_prefix(
            business_id=self.business_id,
            app_name=app_name,
            file_name=old_name,
        )
        return file
        """
        raise NotImplementedError

    def get_object(
            self, app_name: str,
            file_name: str,
            force_name: bool = False,
    ) -> bytes:
        if force_name:
            return self.get_file_by_name(
                app_name=app_name,
                file_name=file_name,
                get_file_object=True,
                force_name=True,
            )
        else:
            return self.get_files_with_max_date(
                file_name=file_name,
                app_name=app_name,
                get_file_object=True,
            )

    def post_dataframe(
            self, app_name: str, file_name: str, df: pd.DataFrame,
            force_name: bool = False, split_by_size: bool = True
    ) -> Union[Dict, List[Dict]]:
        """
        :param self.business_id:
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
                objects: List[Dict] = []
                total_chunks: int = int(bytes_size_df / 5)
                chunk_rows: int = int(len_df / total_chunks)
                for chunk in range(total_chunks + 1):
                    df_temp: pd.DataFrame = df.iloc[chunk*chunk_rows:(chunk+1)*chunk_rows]
                    dataframe_binary: bytes = df_temp.to_csv(index=False).encode('utf-8')

                    if force_name:
                        final_file_name: str = file_name
                    else:
                        final_file_name: str = self._encode_file_name(
                            file_name=file_name, date=dt.date.today(), chunk=chunk
                        )
                    object = self.post_object(
                        app_name=app_name,
                        file_name=final_file_name,
                        object_data=dataframe_binary,
                        force_name=True,
                    )
                    objects = objects + [object]
                return objects

        dataframe_binary: bytes = df.to_csv(index=False).encode('utf-8')

        return self.post_object(
            app_name=app_name,
            file_name=file_name,
            object_data=dataframe_binary,
        )

    def get_dataframe(
            self, app_name: str, file_name: str,
            get_last_date: bool = True, parse_name: bool = True,
            date: Optional[dt.date] = None,
    ) -> pd.DataFrame:
        """
        :param self.business_id:
        :param app_name:
        :param file_name:
        :param parse_name: if true then we parse the file name to get the date
        :param get_last_date:
        :param date:
        """
        if parse_name:
            df = pd.DataFrame()
            if get_last_date:
                dataset_binary = self.get_files_with_max_date(
                    app_name=app_name,
                    file_name=file_name,
                    get_file_object=True,
                )
                for binary in dataset_binary:
                    df = pd.concat([df, pd.read_csv(StringIO(binary.decode('utf-8')))])
            elif date:
                dataset_binary = self.get_file_by_date(
                    app_name=app_name,
                    file_name=file_name,
                    date=date,
                )
                for binary in dataset_binary:
                    df = pd.concat([df, pd.read_csv(StringIO(binary.decode('utf-8')))])
            else:
                dataset_names: List[Dict] = (
                    self.get_files_by_name_prefix(
                        app_name=app_name,
                        name_prefix=file_name,
                    )
                )

                for dataset_name in dataset_names:
                    dataset_binary = self.get_object(
                        app_name=app_name,
                        file_name=dataset_name['name'],
                        force_name=True,
                    )
                    for binary in dataset_binary:
                        df = pd.concat([df, pd.read_csv(StringIO(binary.decode('utf-8')))])
        else:
            dataset_binary: bytes = self.get_file_by_name(
                app_name=app_name,
                file_name=file_name,
                get_file_object=True,
            )
            d = StringIO(dataset_binary.decode('utf-8'))
            df = pd.read_csv(d)

        return df.reset_index(drop=True)

    def post_ai_model(
            self, app_name: str, model_name: str, model: Callable,
    ) -> Dict:
        """
        :param self.business_id:
        :param app_name:
        :param model_name:
        :param model:
        """
        model_binary: bytes = pickle.dumps(model)

        return self.post_object(
            app_name=app_name,
            file_name=model_name,
            object_data=model_binary,
        )

    def get_ai_model(
            self, app_name: str, model_name: str,
    ) -> Any:
        """
        :param self.business_id:
        :param app_name:
        :param model_name:
        """
        model_binary: bytes = self.get_object(
            app_name=app_name,
            file_name=model_name,
        )

        assert len(model_binary) == 1
        model_binary = model_binary[0]

        return pickle.loads(model_binary)
