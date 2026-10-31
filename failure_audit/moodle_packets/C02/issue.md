# Add hook before_help_icon_rendered to allow plugins to extend, augment, or replace help icon output

Currently, the help icon rendering ({{render_help_icon()}} in {{core_renderer}}) offers no extension point. The method renders the blue {{?}} icon with its popover directly from the template without dispatching any hook. This means plugins cannot interact with help icons at all — neither to enrich their content, nor to place additional UI elements alongside them, nor to replace them with alternative implementations.

This proposal adds a new PSR-14-style hook {{\core\hook\output\before_help_icon_rendered}} that is dispatched in {{render_help_icon()}} before the template is rendered. The hook exposes three optional approaches through a single, minimal extension point:

h4. 1. Modify the popover content (mutable template context)

The hook provides the template context as a mutable {{stdClass}}. Callbacks can directly modify its properties ({{text}}, {{completedoclink}}, {{title}}, {{url}}, etc.) to change what appears inside the popover 

*Use cases:*

* A plugin providing extended documentation adds deep links to an external knowledge base directly within the help popup.
* A training/onboarding plugin appends interactive tips or micro-tutorials to specific help texts based on {{identifier}} and {{component}}.
* An AI assistant plugin appends a "Ask AI about this setting" button inside the help popover, giving administrators instant contextual guidance.

h4. 2. Add HTML before or after the help icon ({{add_before_icon}} / {{add_after_icon}})

Callbacks can inject additional HTML that the renderer places immediately before or after the standard help icon output. Multiple plugins can independently add elements without conflicting.

*Use cases:*

* A "Guided Setup" plugin places a small indicator badge next to help icons for settings that still need attention during initial configuration.
* An accessibility plugin adds a secondary button beside the {{?}} that opens a screenreader-friendly version of the help text in a modal dialog instead of a popover.
* A plugin adds a "Copy link to this help topic" button next to specific help icons for sharing in support contexts.

h4. 3. Completely replace the help icon ({{set_replacement}})

A callback can provide a full HTML replacement, in which case the default template rendering is skipped entirely.

*Use cases:*

* A custom theme or UX plugin replaces the standard popover-based {{?}} with a slide-out panel for better readability on complex settings pages.
* An integration plugin replaces specific help icons with links that open a context-sensitive page in an external help desk system (e.g. ServiceNow, Confluence).
* A simplified admin interface plugin hides or replaces help icons for non-expert users with a streamlined alternative.
