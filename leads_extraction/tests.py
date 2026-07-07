from unittest.mock import Mock, patch

from django.test import SimpleTestCase
import requests

from .utils import LeadSalesAPIError, _request_with_retries


class LeadSalesRequestRetryTests(SimpleTestCase):
    @patch("leads_extraction.utils.time.sleep", return_value=None)
    @patch("leads_extraction.utils.requests.request")
    def test_retries_rate_limited_requests_before_returning_response(
        self,
        request_mock,
        sleep_mock,
    ):
        rate_limited_response = Mock(status_code=429, headers={"Retry-After": "1"})
        rate_limited_response.raise_for_status.side_effect = requests.HTTPError(
            "Too Many Requests"
        )

        success_response = Mock(status_code=200, headers={})
        success_response.raise_for_status.return_value = None

        request_mock.side_effect = [rate_limited_response, success_response]

        response = _request_with_retries("get", "https://example.com/leads")

        self.assertEqual(response, success_response)
        self.assertEqual(request_mock.call_count, 2)
        sleep_mock.assert_called_once_with(1.0)

    @patch("leads_extraction.utils.time.sleep", return_value=None)
    @patch("leads_extraction.utils.requests.request")
    def test_raises_after_repeated_rate_limits(self, request_mock, sleep_mock):
        rate_limited_response = Mock(status_code=429, headers={})
        rate_limited_response.raise_for_status.side_effect = requests.HTTPError(
            "Too Many Requests"
        )
        request_mock.return_value = rate_limited_response

        with self.assertRaises(LeadSalesAPIError):
            _request_with_retries("get", "https://example.com/leads")

        self.assertEqual(request_mock.call_count, 6)
        self.assertEqual(sleep_mock.call_count, 5)
