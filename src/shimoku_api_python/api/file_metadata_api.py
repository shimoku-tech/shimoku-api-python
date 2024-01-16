""""""
from typing import Optional, Any, Callable, TYPE_CHECKING

from io import StringIO
import pickle
import asyncio

import pandas as pd
from shimoku_api_python.resources.file import File
from shimoku_api_python.async_execution_pool import async_auto_call_manager, ExecutionPoolContext
from shimoku_api_python.exceptions import ShimokuFileError

import logging
from shimoku_api_python.execution_logger import logging_before_and_after, log_error
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

    @logging_before_and_after(logging_level=logger.debug)
    async def _check_for_shimoku_generated_create(self, file_name: str):
        """ Check if a file is shimoku generated, if it is, raise an error
        :param file_name: name of the file
        """
        file: File = await self._app.get_file(name=file_name)
        if file is not None and 'shimoku_generated' in file['tags']:
            log_error(logger, f'File {file_name} is shimoku generated, you cannot overwrite it', ShimokuFileError)

    @logging_before_and_after(logging_level=logger.debug)
    async def _check_for_shimoku_generated_delete(self, file_name: str, with_shimoku_generated: bool = False):
        """ Check if a file is shimoku generated, if it is, raise an error
        :param file_name: name of the file
        :param with_shimoku_generated: if True, allow to delete a file with the tag 'shimoku_generated'
        """
        file: File = await self._app.get_file(name=file_name)
        if file is None:
            log_error(logger, f'File {file_name} not found', ShimokuFileError)
        if 'shimoku_generated' in file['tags'] and not with_shimoku_generated:
            log_error(logger, f'File {file_name} is shimoku generated, if you are sure you want to delete it, '
                              f'please set with_shimoku_generated to True', ShimokuFileError)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def delete_file(
        self, uuid: Optional[str] = None, file_name: Optional[str] = None,
        with_shimoku_generated: bool = False
    ):
        """ Delete a file
        :param uuid: uuid of the file
        :param file_name: name of the file
        :param with_shimoku_generated: if True, allow to delete a file with the tag 'shimoku_generated'
        """
        await self._check_for_shimoku_generated_delete(file_name, with_shimoku_generated)
        await self._app.delete_file(uuid=uuid, name=file_name)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_file_metadata(self, uuid: Optional[str] = None,  file_name: Optional[str] = None) -> dict:
        """ Get file metadata
        :param uuid: uuid of the file
        :param file_name: name of the file
        :return: the metadata
        """
        return (await self._app.get_file(uuid=uuid, name=file_name)).cascade_to_dict()

    @async_auto_call_manager()
    @logging_before_and_after(logging_level=logger.info)
    async def post_object(
        self, file_name: str, obj: bytes, overwrite: bool = True,
        tags: Optional[list] = None, metadata: Optional[dict] = None
    ):
        """ Save an object
        :param file_name: name of the file
        :param obj: object to be saved
        :param overwrite: if True, overwrite the file if it already exists
        :param tags: tags to be added to the file
        :param metadata: metadata to be added to the file
        """
        await self._check_for_shimoku_generated_create(file_name)
        await self._app.create_file(name=file_name, file_object=obj, tags=tags, metadata=metadata, overwrite=overwrite)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_object(
        self, uuid: Optional[str] = None, file_name: Optional[str] = None,
    ) -> bytes:
        """ Get an object
        :param file_name: name of the file
        :param uuid: uuid of the file
        :return: object
        """
        return await self._app.get_file_object(uuid=uuid, name=file_name)

    @async_auto_call_manager()
    @logging_before_and_after(logging_level=logger.info)
    async def post_dataframe(
        self, file_name: str, df: pd.DataFrame, overwrite: bool = True,
        tags: Optional[list] = None, metadata: Optional[dict] = None
    ):
        """ Save a dataframe
        :param df: dataframe to be saved
        :param file_name: name of the file
        :param overwrite: if True, overwrite the file if it already exists
        :param tags: tags to be added to the file
        :param metadata: metadata to be added to the file
        :return: object
        """
        await self._check_for_shimoku_generated_create(file_name)
        dataframe_binary: bytes = df.to_csv(index=False).encode('utf-8')
        await self._app.create_file(
            name=file_name, file_object=dataframe_binary, tags=tags, metadata=metadata, overwrite=overwrite
        )

    @logging_before_and_after(logging_level=logger.debug)
    async def _get_dataframe(
        self, uuid: Optional[str] = None,  file_name: Optional[str] = None,
    ) -> pd.DataFrame:
        """ Get a dataframe file
        :param uuid: uuid of the file
        :param file_name: name of the file
        :return: dataframe
        """
        dataset_binary: bytes = await self._app.get_file_object(uuid=uuid, name=file_name)
        d = StringIO(dataset_binary.decode('utf-8'))
        df = pd.read_csv(d)

        return df.reset_index(drop=True)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_dataframe(
        self, uuid: Optional[str] = None,  file_name: Optional[str] = None,
    ) -> pd.DataFrame:
        """ Get a dataframe file
        :param uuid: uuid of the file
        :param file_name: name of the file
        :return: dataframe
        """
        return await self._get_dataframe(uuid=uuid, file_name=file_name)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def deleted_batched_dataframe(
        self, file_name: str, with_shimoku_generated: bool = False
    ):
        """ Delete a batched dataframe
        :param file_name: name of the file
        :param with_shimoku_generated: if True, allow to delete a file with the tag 'shimoku_generated'
        """

        files = await self._app.get_files()
        files = [file for file in files if file['name'].startswith(file_name+'_batch_')]
        if files:
            await self._check_for_shimoku_generated_delete(files[0]['name'], with_shimoku_generated)
            logger.info(f'Deleting {len(files)} files to overwrite {file_name}')
            await asyncio.gather(*[self._app.delete_file(name=file['name']) for file in files])

    @logging_before_and_after(logging_level=logger.info)
    def post_batched_dataframe(
        self, file_name: str, df: pd.DataFrame, batch_size: int = 10000, overwrite: bool = True,
        tags: Optional[list] = None, metadata: Optional[dict] = None
    ):
        """ Creates an multiple files saving a dataframe in batches, for big dataframes
        Uploads a dataframe in batches, for big dataframes
        :param file_name: name of the file
        :param df: dataframe to be saved
        :param batch_size: size of the batches
        :param overwrite: if True, overwrite the file if it already exists
        :param tags: tags to be added to the file
        :param metadata: metadata to be added to the file
        """
        if overwrite:
            self.deleted_batched_dataframe(file_name=file_name)

        batches = [df[i:i+batch_size] for i in range(0, df.shape[0], batch_size)]
        for i, batch in enumerate(batches):
            self.post_dataframe(file_name=f'{file_name}_batch_{i}', df=batch, tags=tags, metadata=metadata)

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_batched_dataframe(
        self, file_name: str
    ) -> pd.DataFrame:
        """ Get a batched dataframe file group
        :param file_name: name of the file
        :return: dataframe
        """
        files = await self._app.get_files()
        files = [file for file in files if file['name'].startswith(file_name+'_batch_')]
        files = sorted(files, key=lambda x: int(x['name'].split('_batch_')[1]))
        results = await asyncio.gather(*[self._get_dataframe(file['id']) for file in files])
        return pd.concat(results, ignore_index=True)

    @async_auto_call_manager()
    @logging_before_and_after(logging_level=logger.info)
    async def post_ai_model(
        self, model_name: str, model: Callable, overwrite: bool = True,
        tags: Optional[list] = None, metadata: Optional[dict] = None
    ):
        """ Save a model
        :param model_name: name of the model
        :param model: model to be saved
        :param overwrite: if True, overwrite the file if it already exists
        :param tags: tags to be added to the file
        :param metadata: metadata to be added to the file
        """
        await self._check_for_shimoku_generated_create(model_name)
        model_binary: bytes = pickle.dumps(model)
        return await self._app.create_file(
            name=model_name, file_object=model_binary, tags=tags, metadata=metadata, overwrite=overwrite
        )

    @async_auto_call_manager(execute=True)
    @logging_before_and_after(logging_level=logger.info)
    async def get_ai_model(
        self, uuid: Optional[str] = None,  model_name: Optional[str] = None,
    ) -> Any:
        """ Get a model
        :param uuid: uuid of the file
        :param model_name: name of the model
        :return: model
        """
        model_binary: bytes = await self._app.get_file_object(uuid=uuid, name=model_name)
        return pickle.loads(model_binary)
