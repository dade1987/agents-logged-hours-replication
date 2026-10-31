# Quiz report user-search widget calls get_string() on raw custom profile field keys (e.g. profile_field_fruit), bypassing the profile_field_ guard

*Found via:* Apache logs from a Behat run (multiple parallel runs), as part of the [https://moodle.atlassian.net/browse/MDL-89731|https://moodle.atlassian.net/browse/MDL-89731|smart-link] pre-5.3 log-cleanup epic. Seen with at least two different custom profile field shortnames ({{fruit}} and {{frog}}), confirming this is a generic pattern, not specific to one field name.

*Observed error:*

{noformat}Debugging: Invalid get_string() identifier: 'profile_field_fruit' or component 'core'. Perhaps you are missing $string['profile_field_fruit'] = ''; in lang/en/core.php? in
* line 355 of /public/lib/classes/string_manager_standard.php: call to debugging()
* line 108 of /public/lib/external/externallib.php: call to core_string_manager_standard->get_string()
* line 0 of : call to core_external::get_string()
* line 258 of /public/lib/external/classes/external_api.php: call to call_user_func_array()
* line 85 of /public/lib/ajax/service.php: call to core_external\external_api::call_external_function()
referer: .../mod/quiz/report.php?id=109001&mode=overview{noformat}

(Also observed identically with {{mode=responses}}, and with identifier {{profile_field_frog}}.)

*Root cause:*
{{mod/quiz/amd/src/searchwidget/user.js}} (lines ~52-53) calls {{getStrings(r.extrafields.map((key) => ({key})))}} — the {{core/str}} {{getStrings()}} helper defaults the component to {{'core'}} and is invoked with the _raw_ field-name key (e.g. {{profile_field_fruit}}), with no special-casing for the {{profile_field_}} prefix.

{{r.extrafields}} is populated by the web service {{mod_quiz_get_users_in_report}} ({{mod/quiz/classes/external/get_users_in_report.php:150-152}}), which correctly builds the list via {{\core_user\fields::for_identity($context)->...->get_required_fields([PURPOSE_IDENTITY])}}, including custom profile fields as raw {{profile_field_<shortname>}} keys. However, nothing downstream (server-side or in the JS) routes these through the existing guard in {{\core_user\fields::get_display_name()}} ({{user/classes/fields.php}} line ~638), which is what every other Moodle UI path uses to resolve custom-field display labels instead of calling {{get_string()}} directly.

*Introduced by:* [https://moodle.atlassian.net/browse/MDL-81096|https://moodle.atlassian.net/browse/MDL-81096|smart-link] . This introduced the whole search-widget feature, including this bypass.

*Steps to reproduce:*

# Create a custom user profile field (e.g. shortname {{fruit}}).
# Add it to {{showuseridentity}} (Site administration → Users → Permissions → User policies).
# View a quiz's Overview or Responses report; the report action bar's user-search widget fires an AJAX request that triggers the debugging warning for that field.

Two independent real production stack traces (fields {{fruit}} and {{frog}}) confirm this fires reliably and generically for any custom identity field.

*Suggested fix:* in {{mod/quiz/amd/src/searchwidget/user.js}}, special-case (or strip) the {{profile_field_}} prefix before requesting the string, or resolve the label server-side via {{\core_user\fields::get_display_name()}} instead of relying on a raw {{core}} {{get_string()}} AJAX call.
