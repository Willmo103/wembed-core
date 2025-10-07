@echo off
REM This script generates markdown documentation for the wembed_core project using devtul.

set project_dir=%~dp0..
cd /d %project_dir%
uv version --short > .project_version
:: Make a version dir if it doesn't exist
if not exist .context md .context
set /p project_version=<.project_version
if not exist .context\%project_version% md .context\%project_version%
set project_version_fn_base=.context\%project_version%\%project_version%
devtul md -f %project_version_fn_base%_src.md --sub-dir src/wembed_core --empty %project_dir%
devtul md -f %project_version_fn_base%_tests.md --sub-dir tests --empty %project_dir%
devtul md -f %project_version_fn_base%_schemas.md --sub-dir src/wembed_core/schemas --empty %project_dir%
devtul md -f %project_version_fn_base%_models.md --sub-dir src/wembed_core/models --empty %project_dir%
@REM devtul md -f %project_version_fn_base%_controllers.md --sub-dir src/wembed_core/controllers --empty %project_dir%
exit /b 0x0
