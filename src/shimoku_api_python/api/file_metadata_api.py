""""""
from typing import Optional, Any, Callable, TYPE_CHECKING

from io import StringIO
import pickle
import asyncio

import pandas as pd
from shimoku_api_python.async_execution_pool import async_auto_call_manager, ExecutionPoolContext

import logging
from shimoku_api_python.execution_logger import logging_before_and_after
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..resources.app import App


class FileMetadataApi:
    """
    """

    @logging_before_and_after(logging_level=logger.debug)
    def __init__(self, app: Optional['App'], execution_pool_context: ExecutionPoolContext):
        self._app = app
        self.epc = execution_pool_context

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_file(self, file_name: str):
        """
        :param file_name: name of the file
        """
        await self._app.delete_file(name=file_name)

    @logging_before_and_after(logging_level=logger.debug)
    async def _overwrite_file(self, file_name: str, overwrite: bool = True):
        """
        :param file_name: name of the file
        :param overwrite: if True, overwrite the file if it already exists
        """
        if overwrite and file_name in [file['name'] for file in await self._app.get_files()]:
            logger.info(f'Overwriting file {file_name}')
            await self._app.delete_file(name=file_name)

    @async_auto_call_manager()
    @logging_before_and_after(logging_level=logger.info)
    async def post_object(
        self, file_name: str, obj: bytes, overwrite: bool = True
    ):
        """
        :param file_name: name of the file
        :param obj: object to be saved
        :param overwrite: if True, overwrite the file if it already exists
        """
        await self._overwrite_file(file_name=file_name, overwrite=overwrite)
        await self._app.create_file(name=file_name, file_object=obj)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_object(
        self, file_name: str
    ) -> bytes:
        """
        :param file_name: name of the file
        :return: object
        """
        return await self._app.get_file_object(name=file_name)

    # @staticmethod
    # @logging_before_and_after(logging_level=logger.debug)
    # def get_chunks(
    #     df: pd.DataFrame
    # ) -> Optional[List[bytes]]:
    #     """
    #     :param df: dataframe to be split
    #     """
    #     len_df: int = len(df)
    #     bytes_size_df: int = df.memory_usage(deep=True).sum()
    #     bytes_size_df: int = bytes_size_df // 1024 // 1024
    #     if bytes_size_df <= 5:
    #         return None
    #
    #     total_chunks: int = int(bytes_size_df / 5)
    #     chunk_rows: int = int(len_df / total_chunks)
    #     chunks = []
    #     for chunk in range(total_chunks + 1):
    #         df_temp: pd.DataFrame = df.iloc[chunk*chunk_rows:(chunk+1)*chunk_rows]
    #         dataframe_binary: bytes = df_temp.to_csv(index=False).encode('utf-8')
    #         chunks.append(dataframe_binary)
    #     return chunks

    @async_auto_call_manager()
    @logging_before_and_after(logging_level=logger.info)
    async def post_dataframe(
        self, file_name: str, df: pd.DataFrame, overwrite: bool = True
        # split_by_size: bool = True
    ):
        """
        :param file_name: name of the file
        :param df: dataframe to be saved
        :param overwrite: if True, overwrite the file if it already exists
        :return: object
        """
        # chunks = self.get_chunks(df) if split_by_size else None
        # if chunks:
        #     posting_tasks = []
        #     for chunk, dataframe_binary in enumerate(chunks):
        #         final_file_name: str = file_name + f'_chunk:{chunk}'
        #         posting_tasks.append(
        #             self._app.create_file(file=final_file_name, file_object=dataframe_binary)
        #         )
        #         list(await asyncio.gather(*posting_tasks))
        # else:
        await self._overwrite_file(file_name=file_name, overwrite=overwrite)
        dataframe_binary: bytes = df.to_csv(index=False).encode('utf-8')
        await self._app.create_file(name=file_name, file_object=dataframe_binary)

    @logging_before_and_after(logging_level=logger.debug)
    async def _get_dataframe(
        self, file_name: str
    ) -> pd.DataFrame:
        """
        :param file_name: name of the file
        :return: dataframe
        """
        dataset_binary: bytes = await self._app.get_file_object(name=file_name)
        d = StringIO(dataset_binary.decode('utf-8'))
        df = pd.read_csv(d)

        return df.reset_index(drop=True)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_dataframe(
        self, file_name: str
    ) -> pd.DataFrame:
        """
        :param file_name: name of the file
        :return: dataframe
        """
        return await self._get_dataframe(file_name=file_name)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def deleted_batched_dataframe(
        self, file_name: str
    ):
        """
        :param file_name: name of the file
        """
        files = await self._app.get_files()
        files = [file for file in files if file['name'].startswith(file_name+'_batch_')]
        if files:
            logger.info(f'Deleting {len(files)} files to overwrite {file_name}')
            await asyncio.gather(*[self._app.delete_file(name=file['name']) for file in files])

    @logging_before_and_after(logging_level=logger.info)
    def post_batched_dataframe(
        self, file_name: str, df: pd.DataFrame, batch_size: int = 10000, overwrite: bool = True
    ):
        """
        Uploads a dataframe in batches, for big dataframes
        :param file_name: name of the file
        :param df: dataframe to be saved
        :param batch_size: size of the batches
        :param overwrite: if True, overwrite the file if it already exists
        """
        if overwrite:
            self.deleted_batched_dataframe(file_name=file_name)

        batches = [df[i:i+batch_size] for i in range(0, df.shape[0], batch_size)]
        for i, batch in enumerate(batches):
            self.post_dataframe(file_name=f'{file_name}_batch_{i}', df=batch)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_batched_dataframe(
        self, file_name: str
    ) -> pd.DataFrame:
        """
        :param file_name: name of the file
        :return: dataframe
        """
        files = await self._app.get_files()
        files = [file for file in files if file['name'].startswith(file_name+'_batch_')]
        files = sorted(files, key=lambda x: int(x['name'].split('_batch_')[1]))
        results = await asyncio.gather(*[self._get_dataframe(file['name']) for file in files])
        return pd.concat(results, ignore_index=True)

    @async_auto_call_manager()
    @logging_before_and_after(logging_level=logger.info)
    async def post_ai_model(
        self, model_name: str, model: Callable, overwrite: bool = True
    ):
        """
        :param model_name: name of the model
        :param model: model to be saved
        :param overwrite: if True, overwrite the file if it already exists
        """
        await self._overwrite_file(file_name=model_name, overwrite=overwrite)
        model_binary: bytes = pickle.dumps(model)
        return await self._app.create_file(name=model_name, file_object=model_binary)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_ai_model(
        self, model_name: str
    ) -> Any:
        """
        :param model_name: name of the model
        :return: model
        """
        model_binary: bytes = await self._app.get_file_object(name=model_name)
        return pickle.loads(model_binary)
