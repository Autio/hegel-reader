#!/usr/bin/env python3
"""Regenerate index.html from commentary.md."""
import subprocess, sys
# Just run the build via execute_code inline
# The actual generation logic lives in the main build
# For cron: this reads commentary.md and produces index.html
exec(open(__file__.replace("regen_html.py","build_html.py")).read())
