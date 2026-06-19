from observability.telemetry import telemetry
from observability.telemetry_models import SecurityClassification
from observability.audit_logger import log_audit_action

print('Logging security...')
telemetry.log_security_event(
    classification=SecurityClassification.UNAUTHORIZED_ACCESS,
    event='test_security',
    operation='test',
    metadata={'test': True}
)

print('Logging audit...')
log_audit_action(
    actor='test_user',
    action='test_action',
    reason='test',
    before_state={},
    after_state={'test': True}
)

print('Logging retrieval...')
telemetry.log_retrieval(
    event='test_retrieval',
    operation='test',
    query='hello'
)

print('Done logging.')
