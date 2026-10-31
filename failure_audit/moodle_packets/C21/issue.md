# qtype_multichoice: Screen readers do not announce question text for radio button groups

On the quiz attempt page, radio button options for each question are wrapped in a {{<fieldset>}} whose {{<legend>}} contains the generic text "Question 1 Answer" rather than the actual question text. The question text is rendered as a plain {{<div>}} outside the {{<legend>}}.

*Steps to Reproduce:*

# Navigate to a quiz attempt page containing multiple choice questions.
# Turn on a screen reader
# Press Tab to move focus to the radio button options for any question.
# Observe that the screen reader announces "Question 1 Answer" as the group label instead of the actual question text, followed by the answer options.
# Observe that the {{<legend>}} contains "Question 1 Answer" and the actual question text is rendered outside the {{<legend>}} in a separate {{<div class="qtext">}}.



{noformat}<div class="formulation clearfix">
  <h4 class="accesshide">Question text</h4>

  <div class="qtext">
      <p>Select your city</p> <!-- actual question text -->
  </div>

  <fieldset class="ablock no-overflow visual-scroll-x">
    <legend class="prompt h6 font-weight-normal sr-only">
      <span class="sr-only">Question 1</span> Answer
    </legend>
    <!-- Answers/radion buttons -->
  </fieldset>
</div>{noformat}
