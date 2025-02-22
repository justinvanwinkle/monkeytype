# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import pytest

from .test_tracing import TraceCollector


@pytest.fixture
def collector() -> TraceCollector:
    return TraceCollector()
