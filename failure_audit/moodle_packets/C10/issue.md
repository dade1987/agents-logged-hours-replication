# Linear navigation footer incorrectly visible on stealth activities

Linear navigation should be disabled for stealth activities to preserve the custom learning path designed by the teacher.

*Current behaviour:* The linear navigation footer is visible at the bottom right of the screen on stealth activity pages, allowing users to bypass the intended custom path:

!Screencast from 2026-07-01 15-12-27.mp4|width=600,alt="Screencast from 2026-07-01 15-12-27.mp4"!

*Expected behaviour:* The linear navigation footer should be entirely hidden/disabled when a user is viewing a stealth activity.

h3. 🎯 Required actions

* Ensure the linear navigation footer element is programmatically hidden or not rendered when the active module is a stealth activity.

h3. (/) Acceptance criteria

* The linear navigation footer is completely hidden on stealth activity pages.
* Standard pages continue to display linear navigation as expected across all activity pages and tabs.
* The interface remains visually cohesive and clean when the footer is absent.
