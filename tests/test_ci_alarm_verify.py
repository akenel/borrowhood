def test_ci_alarm_intentional_failure():
    """TEMPORARY (#147): verifying the CI -> Telegram alarm chain end-to-end.
    This commit is reverted immediately after the alert is confirmed."""
    assert False, "CI alarm chain verification -- ignore, reverted in the next commit."
