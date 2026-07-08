# Release Checklist

Use this checklist before sharing a Windows EXE build.

## Code

- All milestone ZIPs uploaded to GitHub
- Commit history has meaningful milestone messages
- `README.md` reflects the current milestone
- `requirements.txt` matches `pyproject.toml`

## Validation

- App opens successfully
- Product import works with a real MedBIS file
- Settings save and reload
- Test search completes without crashing if one competitor fails
- All-competitor search records runs and matches
- Excel report exports successfully
- Logs tab shows recent activity

## Packaging

- `scripts/build_exe.ps1` completes
- `dist\MedBIS Price Intelligence.exe` launches
- EXE uses installed Edge or Chrome
- EXE does not download a browser
- Version metadata is visible in Windows file properties

## Distribution

- Create a tagged GitHub release
- Attach the EXE or installer artifact
- Include first-run instructions
- Include known limitations
- Virus scan the EXE before distribution

## Production Notes

For a commercial deployment, add:

- code signing certificate
- signed installer
- update channel
- backup and restore workflow
- support contact inside the app

