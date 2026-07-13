#!/usr/bin/env sh

pytest -vv test && pytest -vv -c ./test/pytest_config_v2.ini test