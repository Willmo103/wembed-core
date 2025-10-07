@echo off
:: This script automates the process of creating a patch release for the wembed_core project.

:: --- SCRIPT SETUP ---
:: clear the screen for better readability
cls
:: run the ./scripts/cleanup.cmd script to clean up the codebase, only proceed if successful
call "%~dp0cleanup.cmd"
if errorlevel 1 (
    echo ^> Cleanup script failed. Aborting patch creation.
    exit /b 1
)
:: Confirm the project bump action before proceeding
uv version --bump patch --dry-run
if errorlevel 1 (
    echo ^> Version bump dry run failed. Aborting patch creation.
    exit /b 1
)
set /p confirm_bump=Proceed with version bump? (y/n):
if /i "%confirm_bump%" neq "y" (
    echo Aborting patch creation.
    exit /b 0
)
echo Proceeding with version bump...
:: bump the project version
uv version --bump patch
if errorlevel 1 (
    echo ^> Version bump failed. Aborting patch creation.
    exit /b 1
)
:: update the .project_version file
uv version --short > .project_version
if errorlevel 1 (
    echo ^> Updating .project_version failed. Aborting patch creation.
    exit /b 1
)
set /p project_version=<.project_version
set commit_message=Updating package version to %project_version%
:: display the changes, current branch, and generated commit message for review

git status
if errorlevel 1 (
    echo ^> git status failed. Aborting patch creation.
    exit /b 1
)
git branch --show-current
if errorlevel 1 (
    echo ^> git branch command failed. Aborting patch creation.
    exit /b 1
)
echo Commit message: %commit_message%
:: prompt the user for confirmation before proceeding
set /p user_input=Proceed with commit and push? (y/n):
if /i "%user_input%" neq "y" (
    echo Aborting patch creation.
    exit /b 0
)
:: prepare a commit of only the changed in already tracked files, tagging this commit with the new version number
git add -u
if errorlevel 1 (
    echo ^> git add command failed. Aborting patch creation.
    exit /b 1
)
git commit -m "%commit_message%"
if errorlevel 1 (
    echo ^> git commit failed. Aborting patch creation.
    exit /b 1
)
git tag v%project_version%
if errorlevel 1 (
    echo ^> git tag command failed. Aborting patch creation.
    exit /b 1
)
echo Commit and tag created, ready for the user to push.
exit /b 0
