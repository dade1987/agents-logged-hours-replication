# Script admin/cli/fix_orphaned_question_categories.php throws error "Undefined variable $course"

The script admin/cli/fix_orphaned_question_categories.php is designed to repair question categories that refer to a context that no longer exists (orphaned question categories).

*Logic of the function question_category_delete_safe($category) called for these question categories:*

*Case 1:* the question category does not contain any questions that are in use => the question category is deleted.

*Case 2:* the question category contains questions that are in use => the questions should be moved to a question bank with a suitable context.

However, determining this target context requires the existence of the original context of the question category, which does not exist when called by admin/cli/fix_orphaned_question_categories.php because exactly these question categories are selected.

The value for $context is false when called by admin/cli/fix_orphaned_question_categories.php.

({{function question_category_delete_safe}} in public/lib/questionlib.php)

!grafik-20260312-110113.png|width=721,alt="grafik-20260312-110113.png"!

$course is not initialized 
=> core_question\local\bank\question_bank_helper::get_default_open_instance_system_type($course, true); fails
=> question_save_from_deletion is not successful.
=> the script does not fix the orphaned question categories in this case.
