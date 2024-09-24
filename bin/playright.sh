#!/usr/bin/env bash
export SECRET_KEY=thisisatest
playwright install
pytest tests/functional_tests