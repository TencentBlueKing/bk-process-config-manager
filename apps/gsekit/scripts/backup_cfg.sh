#!/bin/bash
backup_file="{file_target_path}/{file_name}"
if [ -f "$backup_file" ]; then
    cp {file_target_path}/{file_name} {file_target_path}/{file_name}_{now_time}
fi