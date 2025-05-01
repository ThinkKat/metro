import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine

from repositories.metro_repository.postgresql_metro_repository import PostgresqlMetroRepository

class TestPostgresqlMetroRepository(unittest.TestCase):

    @patch("repositories.metro_repository.postgresql_metro_repository.create_engine")
    def setUp(self, mock_create_engine):
        self.mock_engine = MagicMock()
        mock_create_engine.return_value = self.mock_engine
        self.repository = PostgresqlMetroRepository()
        self.repository.create_engine("postgresql://test_db_url")

    def tearDown(self):
        self.repository.dispose()

    @patch("repositories.metro_repository.postgresql_metro_repository.Session")
    def test_find_stations_searchbar(self, mock_session):
        mock_session_instance = mock_session.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.keys.return_value = ["line_id", "line_color", "line_name", "station_public_code", "station_name"]
        mock_response.fetchall.return_value = [
            (1, "red", "Line 1", "S001", "Station 1"),
            (2, "blue", "Line 2", "S002", "Station 2"),
        ]
        mock_session_instance.execute.return_value = mock_response

        result = self.repository.find_stations_searchbar()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].line_id, 1)
        self.assertEqual(result[0].line_color, "red")
        self.assertEqual(result[0].station_name, "Station 1")

    @patch("repositories.metro_repository.postgresql_metro_repository.Session")
    def test_find_station_info(self, mock_session):
        mock_session_instance = mock_session.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.keys.return_value = ["station_id", "station_name", "station_public_code"]
        mock_response.fetchone.return_value = (1, "Station 1", "S001")
        mock_session_instance.execute.return_value = mock_response

        result = self.repository.find_station_info("S001")

        self.assertEqual(result["station_id"], 1)
        self.assertEqual(result["station_name"], "Station 1")
        self.assertEqual(result["station_public_code"], "S001")

    @patch("repositories.metro_repository.postgresql_metro_repository.Session")
    def test_find_line_info(self, mock_session):
        mock_session_instance = mock_session.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.keys.return_value = ["line_id", "line_name", "line_color"]
        mock_response.fetchone.return_value = (1, "Line 1", "red")
        mock_session_instance.execute.return_value = mock_response

        result = self.repository.find_line_info(1)

        self.assertEqual(result["line_id"], 1)
        self.assertEqual(result["line_name"], "Line 1")
        self.assertEqual(result["line_color"], "red")

    @patch("repositories.metro_repository.postgresql_metro_repository.Session")
    def test_find_adjacent_stations(self, mock_session):
        mock_session_instance = mock_session.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.keys.return_value = ["station_id", "direction", "up_down"]
        mock_response.fetchall.return_value = [
            (1, "north", "up"),
            (2, "south", "down"),
        ]
        mock_session_instance.execute.return_value = mock_response

        result = self.repository.find_adjacent_stations("S001")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["direction"], "north")
        self.assertEqual(result[1]["up_down"], "down")

    @patch("repositories.metro_repository.postgresql_metro_repository.Session")
    def test_find_transfer_lines(self, mock_session):
        mock_session_instance = mock_session.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.keys.return_value = ["line_id", "line_name", "line_color", "station_public_code"]
        mock_response.fetchall.return_value = [
            (1, "Line 1", "red", "S001"),
            (2, "Line 2", "blue", "S002"),
        ]
        mock_session_instance.execute.return_value = mock_response

        result = self.repository.find_transfer_lines("S001")

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["line_name"], "Line 1")
        self.assertEqual(result[1]["line_color"], "blue")

if __name__ == "__main__":
    unittest.main()
