from usb_operator.policy import SafetyPolicy
def test_read_only_action_is_automatic():
 d=SafetyPolicy().evaluate("read"); assert d.allowed and not d.requires_approval
def test_relay_requires_approval():
 d=SafetyPolicy().evaluate("relay_set"); assert d.allowed and d.requires_approval
def test_unknown_action_is_denied(): assert not SafetyPolicy().evaluate("arbitrary_shell").allowed
def test_critical_action_is_blocked():
 d=SafetyPolicy().evaluate("bypass_interlock"); assert not d.allowed and d.risk=="critical"
