# Allow extensible list of Safe BBB Recording Formats

BigBlueButton can generate multiple recording formats after a meeting, some of which are intended only for moderators (e.g., teachers or administrators). The BigBlueButtonBN plugin provides a configuration setting to define "safe formats"—formats that can be viewed by all users. By default, on installation, only the _presentation_ and _video_ formats are considered safe, but more formats can be selected.

However, the current list of formats is hard-coded and only includes the official formats available in open source, making it difficult to support new formats that should also be considered safe by default. To improve flexibility and future compatibility, there should be a way to extend the list of available formats without modifying the source code.

The workaround for now is to define the variable in config.php

{code:php}$CFG->bigbluebuttonbn_recording_safe_formats = 'podcast,presentation,video,transcript';
{code}

But that locks the configuration,
