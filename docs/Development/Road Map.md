# Road Map
Proxima has a few places it wants to go!

---

## 2022

### Refactor job-handling
I'm hoping to focus on a large scale refactor of job-handling.
In the early days, Proxima was just two scripts: One that dumped clip metadata into a text file,
and another that watched a directory for those text files and encoded everything in them.
The first computer to take the job would change the `status` flag in the text file and get going.
Of course we had all sorts of issues with op-locks, race conditions and unhandled exceptions...

Some of that legacy code has remained. Clip attributes are saved into dictionaries
and extended later with project and timeline metadata. There's no typing nor dynamic attributes, just good old fashioned data.
While the data passed by Resolve's API doesn't require the same kind of validation that user input requires, 
it's still difficult to extend or refactor code around job handling, so I'd like to rewrite them as data-classes.

### Improved CLI commands
The CLI commands in Proxima are simple: `queue` to add jobs, `work` to consume them, `purge` to clear them and `celery` to pass in advanced commands.
I must admit my use case has not changed much over the years. We queue jobs straight from the timeline because it works for us. I don't really know what works
for everyone else. So if you use Proxima, feel free to tell me.

I figure some more options would be fitting however.

#### Interactive timeline queuing
Currently `queue` always refers to the active timeline in the current project. That works nicely. But what if you want to queue all the timelines? Or timelines matching a pattern?
Or be given a list and select at will? See issue [#161](https://github.com/in03/proxima/issues/161)


## 2023

### Split and stitch encoding
Split and stitch encoding or "chunking" allows source media to be divided into time-range "chunks" for more workers to work on before being concatenated as a single file once all are finished.
Let me explain why this is a good idea.

A single worker can encode many proxies simultaneously, but a a single proxy cannot be encoded by many workers simultaneously. 
This can mean a lot of idle processing power when encoding media with a long duration. All the short media will finish first and the long media will be left to individual workers.
Chunking means we can divide the work evenly and win back all that processing power.

#### Considerations
This is a huge undertaking. I've managed to get it working as a proof of concept locally, but to integrate it with Proxima is a different story. 
Integration will depend on the aforementioned "job-handling refactor". There's not much we can do about the complexity besides simplify existing code,
try to follow best practices and model after good examples of similar systems - which unfortunately seem scarce. If anyone knows of any please let me know! 

Concatenation is a fast operation but is limited by disk speed.
The overhead can be minimised by only chunking source media over a certain duration. 
Since disk-speed is an environmental factor, the exact duration of a file that is worth chunking will differ for each system. 
We can provide a good default value in settings but leave it up to the end user to configure. 


#### Implementation proposal


``` mermaid
graph TD;
    A[Proxima CLI]--> R
    A --> S(Get setting:<br>duration_worth_chunking)
    S --> |45 seconds| D[Jobs]
    R[Resolve API<br>- Project <br>- Timeline<br>- Clip attributes] --> D
    D --> |45 seconds|T[Create encoding tasks:<br>chunks / full-duration]
    T --> |Tasks that are chunks| C[Wrap as chord:<br> task,<br> concat callback]
    C --> G[Wrap as group:<br>- chords<br>- full-duration]
    T --> |Tasks that are<br>full-duration|G
    G --> Q[Queue tasks]
    Q --> P["Progress discrete completion:<br>len([x for x in results if x.ready)"]
```

---

1. Run `proxima queue` 
2. Get the `duration_worth_chunking` setting value from user settings
3. Get the project, timeline and source media metadata from Resolve's API
4. Restructure existing jobs as "chunks" depending on source-media duration.
5. Wrap chunked jobs as chords with a concatenate callback
6. Wrap all jobs in a group
7. Worker side progress displays encoding progress-bar of current chunk and discrete completion of current chord 
8. Queuer side progress displays total average progress-bar and completion based on status of chords AsyncResults and standard AsyncResults

### Proxy presets

The ability to create multiple encoding presets would allows us to set up different settings for different purposes. 
Like h.264 for a project we can send over the internet? Or high quality archival of select takes. 
We could also do this with Resolve's individual clip export from the delivery page, but to achieve distributed encoding, you'd still need more licenses. 
That might be of interest to others.

It also means we can preconfigure some ideal default settings that work for different users as good starting points. 
say a ProRes preset for Mac users, DNxHD preset for Windows, h.264/5 for archival (a lot of fiddly settings we can disambiguate).
We can add comments to explain any unintiutive necessities in the ffmpeg settings. 

```yaml
edit_proxy:
  ffmpeg_loglevel: "error"
  codec: "dnxhd"
  vertical_res: 720
  profile: "dnxhd_sq"
  pix_fmt: "yuv422p"
  audio_codec: "pcm_s16le" 
  audio_samplerate: "48000" 
  misc_args: [-"hide_banner", -"stats"] 
  ext: ".mov"
  threads: 2
  
portable_proxy:
  ffmpeg_loglevel: "info"
  codec: "x264"
  vertical_res: 1080
  profile: "slow"
  ...
  ext ".mp4"
  threads: "auto" # x264 handles best

portable_archive:
  ffmpeg_loglevel: "info"
  codec: "x265"
  vertical_res: 2160
  profile: "very-slow"
  ...
  ext ".mp4"
  threads: "auto" # x264 handles best
```

#### Worker Overrides
```yaml
# Override queuer settings
overrides:
  # Use wildcard matching
  # Latest overrides
  presets:
    *:
      vertical_res: 720

    *proxy: 
        vertical_res: 1080
        threads: 2

    *archive:
       threads: 1

    portable_proxy:
      threads: 2 # Prioritizes last override
      vertical_res: 720
```