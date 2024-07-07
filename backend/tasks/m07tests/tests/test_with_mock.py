import unittest
from unittest.mock import patch, MagicMock
from app import get_and_process_data


class TestApp(unittest.TestCase):

    @patch("app.fetch_data_from_api")
    @patch("app.process_data")
    def test_get_and_process_data(
        self, mock_process_data: MagicMock, mock_fetch_data: MagicMock
    ):
        # Mock функции fetch_data_from_api для возврата "sample response"
        mock_response = {"key": "value"}
        mock_fetch_data.return_value = mock_response

        # Mock функции process_data
        mock_processed_data = {"KEY": "VALUE"}
        mock_process_data.return_value = mock_processed_data

        # вызываем тестируемую функцию
        result = get_and_process_data()

        # Assertions
        mock_fetch_data.assert_called_once()  # убеждаемся, что fetch_data_from_api был вызван
        mock_process_data.assert_called_once_with(
            mock_response
        )  # убеждаемся, что process_data была вызвана с "mocked response"
        self.assertEqual(
            result, mock_processed_data
        )  # убеждаемся, что функция вернула ожидаемые обработанные данные
