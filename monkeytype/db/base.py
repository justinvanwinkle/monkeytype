# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.
from abc import ABCMeta
from abc import abstractmethod
from typing import Iterable
from typing import List
from typing import Optional

from monkeytype.tracing import CallTrace
from monkeytype.tracing import CallTraceLogger


class CallTraceThunk(metaclass=ABCMeta):
    """A deferred computation that produces a CallTrace or raises an error."""

    @abstractmethod
    def to_trace(self) -> CallTrace:
        """Produces the CallTrace."""
        pass


class CallTraceStore(metaclass=ABCMeta):
    """
    An interface that all concrete calltrace storage backends must implement.
    """

    @abstractmethod
    def add(self, traces: Iterable[CallTrace]) -> None:
        """Store the supplied call traces in the backing store"""
        pass

    @abstractmethod
    def filter(
        self,
        module: str,
        qualname_prefix: Optional[str] = None,
        limit: int = 2000,
    ) -> List[CallTraceThunk]:
        """
        Query the backing store for any traces that match the supplied query.

        By returning a list of thunks we let the caller get a partial result in
          the event that decoding one or more call traces fails.
        """
        pass

    @classmethod
    def make_store(cls, connection_string: str) -> "CallTraceStore":
        """Create a new store instance.

        This is a factory function that is intended to be used by the CLI.
        """
        msg = (
            f"Your CallTraceStore ({cls.__module__}.{cls.__name__}) "
            "does not implement make_store()"
        )
        raise NotImplementedError(msg)

    def list_modules(self) -> List[str]:
        """List of traced modules from the backing store"""
        msg = (
            "Your CallTraceStore"
            f" ({self.__class__.__module__}.{self.__class__.__name__}) does"
            " not implement list_modules()"
        )
        raise NotImplementedError(msg)


class CallTraceStoreLogger(CallTraceLogger):
    """A CallTraceLogger that stores logged traces in a CallTraceStore."""

    def __init__(self, store: CallTraceStore) -> None:
        self.store = store
        self.traces: List[CallTrace] = []

    def log(self, trace: CallTrace) -> None:
        if trace.func.__module__ != "__main__":
            self.traces.append(trace)

    def flush(self) -> None:
        self.store.add(self.traces)
        self.traces = []
