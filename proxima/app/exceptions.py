class ResolveUnsupportedPlatform(Exception):
    """
    Exception raised when Resolve's API does not support the current system.

    This will occur when using any OS other than Windows, MacOS or Linux.
    """

    def __init__(self, message="Platform is not 'Windows', 'MacOS' or 'Linux'"):
        self.message = message
        super().__init__(self.message)


class ResolveAPIConnectionError(Exception):
    """
    Exception raised when Resolve API is unreachable.

    This can occur when Resolve is not open or the API server has crashed.
    """

    def __init__(
        self,
        message="Resolve Python API is not accessible. Is DaVinci Resolve running?",
    ):
        self.message = message
        super().__init__(self.message)


class ResolveNoCurrentProjectError(Exception):
    """
    Exception raised when the current project is unknown.

    This can occur when Resolve is running but no project has been opened.
    """

    def __init__(
        self, message="Couldn't get the current project. Is a project open in Resolve?"
    ):
        self.message = message
        super().__init__(self.message)


class ResolveNoCurrentTimelineError(Exception):
    """
    Exception raised when the current timeline is unknown.

    This can occur when Resolve is running and a project is open
    but no timeline has been opened.
    """

    def __init__(
        self,
        message="Couldn't get the current timeline. Is a timeline open in Resolve?",
    ):
        self.message = message
        super().__init__(self.message)


class ResolveNoMediaPoolError(Exception):
    """
    Exception raised when the Media Pool object is not accessible.

    This shouldn't occur under normal circumstances.
    """

    def __init__(self, message="Resolve's Media Pool is inacessible."):
        self.message = message
        super().__init__(self.message)


class ResolveLinkMismatchError(Exception):
    """
    Exception raised when Resolve's `LinkProxyMedia` API method rejects a provided proxy.

    The API method returns a bool with no additional error context.
    Common reasons for a mismatch include incorrect proxy settings (framerate, timecode)
    or a corrupt/unfinished proxy file.
    """

    def __init__(self, proxy_file, message=None):

        self.proxy_file = proxy_file

        if message != None:
            self.message = message
        else:
            message = f"Couldn't link source media to proxy '{self.proxy_file}'\n"
            f"The proxy file may be corrupt, incomplete or encoding settings may be incorrect (framerate, timecode, etc)"

        super().__init__(self.message)


class ResolveLostMPIReferenceError(Exception):
    """
    Exception raised when media pool items passed to Resolve's `LinkProxyMedia` no longer reference in memory objects.

    This occurs when any amount of project switching occurs between queuing and linking.
    MPI references exist per session and will be lost on project changes.
    """

    def __init__(self, media_pool_item, message=None):

        self.media_pool_item = media_pool_item

        if message != None:
            self.message = message
        else:
            message = f"Lost reference to original media pool items, has the project been changed?\n"
            f"Post-encode linking after a project change is not possible without re-iterating media pool items."

        super().__init__(self.message)
