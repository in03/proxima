""" Helper functions for proxies """

import pathlib
import os

def get_expected_proxy_path(media_list):
    """Retrieves the current expected proxy path using the source media path.
    """

    for media in media_list:

        file_path = media['File Path']
        p = pathlib.Path(file_path)

        # Tack the source media relative path onto the proxy media path
        expected_proxy_path = os.path.join(proxy_path_root, os.path.dirname(p.relative_to(*p.parts[:1])))
        media.update({'Expected Proxy Path': expected_proxy_path})

    return media_list


