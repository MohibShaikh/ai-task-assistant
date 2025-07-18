# Security Monitor
import logging

logger = logging.getLogger('security_monitor')

def log_security_event(event_type, details, user_id=None, ip_address=None):
    try:
        logger.warning(f'SECURITY EVENT: {event_type} - {details}')
    except Exception as e:
        logger.error(f'Failed to log security event: {e}')

def log_failed_login(username, ip_address):
    log_security_event('failed_login', f'Failed login for: {username}', username, ip_address)

def log_successful_login(username, ip_address):
    log_security_event('successful_login', f'Successful login for: {username}', username, ip_address)
