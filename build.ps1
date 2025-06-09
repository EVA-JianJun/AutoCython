python -m build --wheel

Remove-Item -Path .\build -Recurse
Remove-Item -Path .\AutoCython_jianjun.egg-info -Recurse

pause