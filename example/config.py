import re
import view_logs as vl

class VIEW_LOGS:
    EDITOR_PATH = "C:/Program Files/Notepad++/notepad++.exe"

    FILTER_RULES = [
        vl.filter_remove_category('LogTemp'),
        #vl.filter_remove_lines_with('_C_0]'),
        vl.filter_clean_category('LogCharacterMovement'),
        vl.filter_remove_data_before_category('LogNavMeshMovement'),
        vl.filter_rule_to_config('VeryVerbose: ', '', re.M),
        vl.filter_rule_to_config('Verbose: ', '', re.M),
        vl.filter_rule_to_config('Warning: ', '', re.M),
        vl.filter_rule_to_config(r'\\n', '\n', re.M),
    ]
