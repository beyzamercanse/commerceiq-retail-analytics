"""Check the dashboard startup permission policy."""

from commerceiq.deployment_check import permissions_ok


def test_accepts_readonly_account():
    assert permissions_ok("commerceiq_dashboard", True, False, False)


def test_rejects_owner_or_writer_account():
    assert not permissions_ok("postgres", True, True, True)
    assert not permissions_ok("commerceiq_dashboard", True, True, False)
    assert not permissions_ok("commerceiq_dashboard", True, False, True)


def test_rejects_missing_grant():
    assert not permissions_ok("commerceiq_dashboard", False, False, False)
