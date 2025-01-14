#!/usr/bin/python3
""" Invoked by msbuild to run in behalf of the actual clang-tidy.exe
to accept the command lines --export-fixes and --line-filter, currently
unsupported by the built-in msbuild ClangTidy target. """
#
# Copyright (C) 2021 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Source code adapted from https://github.com/platisd/clang-tidy-pr-comments.


import subprocess
import json
import os

from clang_lint.clang_lint import files_to_lint


def run(*kwargs):
    export_fixes = "fixes.yaml"
    # Need to find rootdir in some way.
    rootdir = os.getenv("GITHUB_WORKSPACE")
    if rootdir is None:
        gitProc = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                 capture_output=True, text=True)
        if gitProc.returncode != 0:
            print("Could not determine repository root")
            # Running from MSBuild my current directory will be child of
            # the repository root. At least for WSL.
            rootdir = os.path.abspath("../")
        else:
            rootdir = gitProc.stdout.strip()
    project_dir = "DistroLauncher"
    sources = files_to_lint.files_to_lint(rootdir, project_dir)
    # line_filter will contain the non-excluded files.
    line_filter = []
    for s in sources:
        line_filter += [{"name": os.path.basename(s)}]

    line_filter_cli = json.dumps(line_filter)

    # Clean up just in case:
    if os.path.exists(export_fixes):
        os.remove(export_fixes)

    # Removing the files msbuild asked for linting but our ignore file says
    # to igore.
    lc_sources = [s.lower() for s in sources]
    msbuild_cli = list(kwargs)
    msbuild_cli = [c for c in msbuild_cli
                   if not os.path.exists(c) or
                   os.path.normpath(c.lower()) in lc_sources]
    cli = ["clang-tidy", "--export-fixes", export_fixes, "--line-filter",
           line_filter_cli] + msbuild_cli
    print("==== Running clang-tidy with the following arguments:")
    print(cli)

    proc = subprocess.run(cli)

    if proc.returncode != 0:
        print("clang-tidy failed to complete its run.")

    if not os.path.exists(export_fixes):
        print("clang-tidy could not generate any output due failures.")
        return None
