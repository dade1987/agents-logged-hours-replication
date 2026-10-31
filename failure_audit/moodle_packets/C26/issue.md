# Quiz creation and updates trigger warnings when duedate is omitted

To replicate:

# Download MCP Quiz Creator v1.3.0 ([https://github.com/Sergio-Oracle/moodle-local-mcp-quiz/releases/tag/v1.3.0|https://github.com/Sergio-Oracle/moodle-local-mcp-quiz/releases/tag/v1.3.0]) and
extract it into *public/local/mcp_quiz*
# Delete *public/local/mcp_quiz/db/install.xml* (this release contains an invalid empty schema file that prevents installation)
# Navigate to “Site administration” > “Notifications” and complete the installation
# Create a course and note its ID
# Navigate to “Development” > “Debugging” and set debug messages to “DEVELOPER”
# Enable Web services under Advanced features, then enable REST (under “Server” > “Web services” > “Manage protocols”)
## Under “Manage tokens”, create a token for the administrator and MCP Quiz Service (take note of the token)
# Run this command:
{noformat}curl -sS '[YOUR SITE]/webservice/rest/server.php' \
  --data-urlencode 'wstoken=[TOKEN]' \
  --data-urlencode 'wsfunction=local_mcp_quiz_créer_quiz' \
  --data 'moodlewsrestformat=json' \
  --data 'courseid=COURSE_ID' \
  --data-urlencode 'name=Missing duedate reproduction'{noformat}
# Check the PHP error log and see: {{PHP Warning: Undefined property: stdClass::$duedate in .../public/mod/quiz/lib.php on line 1235}}

The same issue affects [qtype_stack|https://github.com/maths/moodle-qtype_stack] but it’s more annoying to reproduce. Probably other third party plugins are affected too.
