from dependency_injector import containers, providers
from utils.utils.src.container import UtilsContainer

from files.src.delete_file import DeleteFile
from files.src.file_repository import FileRepository
from files.src.parse_html_file_to_string import ParseHtmlFileToString
from files.src.save_file import SaveFile


class FilesContainer(containers.DeclarativeContainer):
    utils_container: UtilsContainer = providers.DependenciesContainer()
    base_dir = providers.Dependency(instance_of=str)

    file_repository = providers.Singleton(
        FileRepository, session_factory=utils_container.session_factory
    )

    save_file = providers.Singleton(
        SaveFile, file_repository=file_repository, base_dir=base_dir
    )

    parse_html_file_to_string = providers.Singleton(
        ParseHtmlFileToString, file_repository=file_repository, base_dir=base_dir
    )

    delete_file = providers.Singleton(
        DeleteFile, file_repository=file_repository, base_dir=base_dir
    )
