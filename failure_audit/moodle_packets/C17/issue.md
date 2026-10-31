# Navigation footer: Implement linear navigation exceptions for Previous/Next

Following the implementation of the core 'Previous' and 'Next' navigation buttons, we need to refine the logic to handle boundary cases within the course structure. This improvement ensures that the navigation remains logical and does not lead users into "dead ends" or redundant loops.

Specifically, we need to handle the start of course sections and the end of the course. At the first activity of a course, the “Previous” link should be suppressed to encourage a forward-moving flow within that module. At the final activity of the entire course, the “Next” link should be replaced with a clear "Back to course" link to return the user to the main course page for closure:

!image-20260430-132750.png|width=600,alt="image-20260430-132750.png"!

!image-20260430-132814.png|width=600,alt="image-20260430-132814.png"!

h3. 🎯 Required actions

* Update the navigation renderer to detect if the current activity is the first item in the course. If so, the “Previous” button should be hidden.
* Update the footer logic to identify the final activity in the entire course sequence. For the last activity, replace the standard “Next” link with a "Go to course" link as per the design prototype.
* Ensure the "Go to course" link correctly resolves to the course main page (course/view.php?id=x).
* Ensure that when the “Previous” button is hidden (at the first activity of a course), the remaining navigation elements (the “Next” button or "Go to course" link) maintain their correct alignment according to the prototype.

h3. (/) Acceptance criteria

* The “Previous” button is not displayed for the first activity of a course.
* The “Next” button is replaced by a "Go to course" link for the last activity of the course.
* Clicking "Go to course" successfully redirects the user to the main course page.
* The transition between these states is seamless and does not cause layout shifts in the sticky footer.
* Navigation logic respects hidden activities and access restrictions (e.g., if the "next" activity is hidden, the "Go to course" link should appear earlier if that activity is effectively the last one accessible to the student).
