_APP_NAME = "ta_cisco_webex_add_on_for_splunk"
_REALM = "__REST_CREDENTIAL__#ta_cisco_webex_add_on_for_splunk#configs/conf-ta_cisco_webex_add_on_for_splunk_account"
_TOKEN_EXPIRES_CHECKPOINT_KEY = "{account_name}_account_token_expired_in"
_REFRESH_TOKEN_ENDPOINT = "https://{base_endpoint}/v1/access_token"
_BASE_URL = "https://{base_endpoint}/v1/"
_MAX_PAGE_SIZE = 100
_MEETINGS_ENDPOINT = "meetings"
_MEETING_PARTICIPANTS_ENDPOINT = "meetingParticipants?meetingId={meeting_id}"
_ORGANIZATIONS_ENDPOINT = "organizations"
_ADMIN_AUDIT_EVENTS_ENDPOINT = "adminAudit/events"
_MEETING_USAGE_REPORTS_ENDPOINT = "meetingReports/usage"
_MEETING_ATTENDEE_REPORTS_ENDPOINT = "meetingReports/attendees?meetingId={meeting_id}"
_LIST_PEOPLE_ENDPOINT = "people"
_GET_MEETING_QUALITIES =  "meeting/qualities"
_GET_DETAILED_CALL_HISTORY = "cdr_feed"

UNAUTHORIZED_STATUS = 401

_RESPONSE_TAG_MAP = {
    _MEETINGS_ENDPOINT: "items",
    _MEETING_PARTICIPANTS_ENDPOINT: "items",
    _ORGANIZATIONS_ENDPOINT: "items",
    _ADMIN_AUDIT_EVENTS_ENDPOINT: "items",
    _MEETING_USAGE_REPORTS_ENDPOINT: "items",
    _MEETING_ATTENDEE_REPORTS_ENDPOINT: "items",
    _LIST_PEOPLE_ENDPOINT: "items",
    _GET_MEETING_QUALITIES: "items",
    _GET_DETAILED_CALL_HISTORY: "items"
}