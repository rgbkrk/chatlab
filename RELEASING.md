Releasing is automated with GitHub actions, so long as a tag is created with v*.*.\* format. `bump2version` does this for us.

-   Get an up to date `main`
-   Check out a new branch like `release-0.12.2`
-   Update the Changelog to reflect the changes since the last release
-   `poetry run bump2version minor`
-   Verify that it changed what we expected it to
-   `git push && git push --tags`

Then go check on the [Actions](https://github.com/rgbkrk/murkrow/actions), namely the release & publish workflow.
