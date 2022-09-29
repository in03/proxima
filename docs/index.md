---
comments: true
---
# Proxima

<p align="center">
  <a href="https://in03.github.io/proxima/"><img src="images/proxima_banner_vector.svg" alt="Proxima"></a>
</p>
<p align="center">
    <em>Davinci Resolve proxies meets distributed-computing!</em>
</p>
<p align="center">
<a href="https://github.com/in03/proxima/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/in03/proxima" alt="License">
</a>
<a href="https://results.pre-commit.ci/latest/github/in03/proxima/main" target="_blank">
    <img src="https://results.pre-commit.ci/badge/github/in03/proxima/main.svg" alt="Pre-commit CI">
</a>
<a href="https://github.com/in03/proxima/actions" target="_blank">
    <img src="https://img.shields.io/github/checks-status/in03/proxima/main" alt="GitHub Branch Checks">
</a>
<a href="https://pypi.org/project/typer" target="_blank">
    <img src="https://img.shields.io/github/last-commit/in03/proxima" alt="GitHub Last Commit">
</a>
</p>



---

**Documentation**: <a href="https://in03.github.io/proxima/" target="_blank">https://in03.github.io/proxima/</a>

**Source Code**: <a href="https://github.com/in03/proxima" target="_blank">https://github.com/in03/proxima</a>

---
!!! Note
    This documentation is a work in progress!
    Things are constantly changing here. If something isn't working as it should 
    or you have any questions about Proxima or the documentation, please start a 
    [Q&A discussion](https://github.com/in03/proxima/discussions/categories/q-a)
    on GitHub.
---

Proxima is a CLI tool designed to make transcoding proxies for DaVinci Resolve a **breeze** 😎👌.

![Queuing Demo](images/proxima_queue_demo.gif)

---

Only create proxies for footage used in your timeline - not entire subfolders!
Once finished encoding, proxies are **automatically** linked.

Launch Proxima on as many computers as you have free and it'll pool all the resources together to encode multiple proxies at once.
Best of all, you don't need any extra licenses!

**Only have one computer?**

*No Worries!* Depending on your chosen settings, Proxima can run as many workers as logical CPU cores. A 12-core / 24-thread machine could do 24 proxies at once!
Encoding can also run **entirely** on the **CPU**, leaving **GPU-heavy** Resolve with plenty of resources to continue editing while you pump out proxies. 

### Key Features 

It's ***gutsy*** ⚡:

 - **Distributed computing** - Use multiple computers to share the load, if you have them. Proxima can use as many as you have - no limit.
 - **Background encoding** - Encode in the background and edit in Resolve at the same time. Choose a CPU-heavy codec and Resolve will take a minimal hit.
 - **Multiprocessing** - Each worker runs a single encoding process. Start several workers on a single machine or just a couple if it's an older machine. Easy resource management.
 - **Scalable** - Start more workers at any time and they'll get busy. Stop workers at any time and unfinished jobs will be requeued for another worker to pick up.
 - **Multiple codec support** - Anything ffmpeg supports, Proxima supports - including ProRes on Windows! (Grade 10-bit without switching to camera originals) 
 - **Timeline based queueing** - Easily queue *only* what you need. Don't choose between navigating messy folders or transcoding too much footage. Save space and time.

 But ***smart*** 🧐:

 - **Resolve clip attributes support** - Generated proxy media inherits orientation, data-levels, and other clip attributes from the original source media in Resolve.
 - **Automatic linking** - Proxima automatically links generated proxies to the correct media pool items after encoding.
 - **Intelligent handling** - Proxima intelligently searches for existing proxies, always picking the newest one - even ones made by other applications. It's also careful in handling offline and orphaned proxies. 
 - **Advanced user configuration** - Simple YAML configuration with settings for source media whitelisting (by framerate, extension type), cross-platform path-mapping and lots more!
 - **Easy progress tracking** - A nice pretty progress bar to display aggregate task progress, discrete task completion worker utilisation + desktop notifications. Flower for advanced metrics and a dedicated web-app on the way.


--- 

#### Coming soon!


## Usage
Check out the [Getting Started](https://in03.github.io/proxima/User Guide/Getting Started) guide for a quick setup tutorial.
Otherwise, here are the basics for reference.


### Commands
  * `proxima queue`                                - Queue proxies from the currently open DaVinci Resolve timeline
  * `proxima work [Optional: number of workers]`   - Launch some local workers
  * `proxima config`                               - Open user settings configuration file for editing
  * `proxima purge`                                - Purge all tasks from Celery according to VC key
  * `proxima celery [celery command] `             - Pass commands to Celery buried in venv
  * `proxima -- help`

