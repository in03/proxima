from pydavinci.wrappers.mediapoolitem import MediaPoolItem
from proxima.app.exceptions import MPIAlreadyRegistered


class MediaPoolIndex:
    """
    Index to lookup media pool items by ID allowing roundtrip through Celery
    """

    def __init__(self):
        """
        Media pool index object allows media pool object lookup by ID.

        MPIs are unhashable. Retaining a reference is the easiest way to link
        proxies post-encode. Use it to round-trip the reference ID through Celery.
        The instance should be initialised at the module-level and imported into
        each additional module as needed for global access to references.
        """
        self._mpi_index = dict()

    def add_to_index(self, media_pool_item: MediaPoolItem, exists_ok: bool = True):
        """
        Add a new media pool item to the index

        Args:
            media_pool_item (MediaPoolItem): Media pool item to add
            exists_ok (bool, optional): Don't raise `MPIAlreadyRegistered` on duplicate MPI additions. Defaults to True.

        Raises:
            MPIAlreadyRegistered: Raised when trying to add the same media pool item twice unless `exists_ok` is True.
        """

        id = media_pool_item.media_id

        if id in self._mpi_index.keys():
            if not exists_ok:
                raise MPIAlreadyRegistered(id)

        self._mpi_index.update({id: media_pool_item})
        return

    def lookup(self, id: str) -> MediaPoolItem:
        """Lookup mediapoolitem in index by ID"""
        return self._mpi_index.get(id)  # type: ignore


media_pool_index = MediaPoolIndex()
