@echo off
if exist {file_target_path}\{file_name} (
	type {file_target_path}\{file_name}
) else (
    echo|set /p="{not_found_flag}"
)
