---
comments: true
---


# Home

**Note**
>
> This documentation is a work in progress!
> If you have any questions, please start a Q&A 
> on the [GitHub discussions page](https://github.com/in03/proxima/discussions/categories/q-a).


## Commands
  * `proxima queue`                                - Queue proxies from the currently open DaVinci Resolve timeline
  * `proxima work [Optional: number of workers]`   - Launch some local workers
  * `proxima config`                               - Open user settings configuration file for editing
  * `proxima purge`                                - Purge all tasks from Celery according to VC key
  * `proxima celery [celery command] `             - Pass commands to Celery buried in venv

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
