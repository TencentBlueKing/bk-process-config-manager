@echo off
if exist {file_target_path}\{file_name} (
	copy {file_target_path}\{file_name} {file_target_path}\{file_name}_{now_time}
)