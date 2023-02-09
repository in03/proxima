import pytest
from shortuuid import uuid

from proxima.app import checks
from proxima.celery import launch_workers


@pytest.fixture
def test_launch_workers():
    return launch_workers.new_worker(f"test-{uuid}")


def test_check_workers():
    workers = checks.WorkerCheck
    assert len(workers) > 1
    assert workers.all_are_compatible != None
    assert workers.none_are_compatible != None
