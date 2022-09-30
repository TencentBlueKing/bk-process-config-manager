#!/bin/bash
backup_file="{file_target_path}/{file_name}"
if [ -f "$backup_file" ]; then
    cat $backup_file
else
  echo -n "{not_found_flag}"
fi
