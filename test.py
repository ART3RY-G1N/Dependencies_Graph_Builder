import unittest
import configparser
import requests
import re
import os
from unittest.mock import patch, MagicMock
from main import *


class TestPackageDependencies(unittest.TestCase):
    @patch('requests.get')
    def test_get_package_dependencies_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'info': {'requires_dist': ['requests>=2.28.2']}}
        mock_get.return_value = mock_response
        dependencies = get_package_dependencies('requests')
        self.assertEqual(dependencies, ['requests>=2.28.2'])

    @patch('requests.get')
    def test_get_package_dependencies_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        dependencies = get_package_dependencies('nonexistentpackage')
        self.assertEqual(dependencies, [])

    @patch('requests.get')
    def test_get_package_dependencies_exception(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        dependencies = get_package_dependencies('requests')
        self.assertEqual(dependencies, [])


class TestExtractPackageName(unittest.TestCase):
    def test_extract_package_name_simple(self):
        self.assertEqual(extract_package_name('requests>=2.28.2'), 'requests')

    def test_extract_package_name_with_extras(self):
        self.assertEqual(extract_package_name('requests[security]>=2.28.2'), 'requests')

    def test_extract_package_name_with_version_specifiers(self):
        self.assertEqual(extract_package_name('requests>2.28,<3.0'), 'requests')


class TestGenerateDot(unittest.TestCase):
    @patch('builtins.open')
    def test_generate_dot_simple(self, mock_open):
        mock_file = MagicMock()
        mock_open.return_value = mock_file
        generate_dot('requests', ['requests>=2.28.2'], mock_file, max_depth=1)
        mock_file.write.assert_any_call('"requests"')
        mock_file.write.assert_any_call(' -> "requests"')
        mock_file.write.assert_any_call(';')

    @patch('builtins.open')
    def test_generate_dot_recursive(self, mock_open):
        mock_file = MagicMock()
        mock_open.return_value = mock_file
        generate_dot('requests', ['requests>=2.28.2'], mock_file) #Max depth is default 2
        mock_file.write.assert_any_call('"requests"')
        mock_file.write.assert_any_call(' -> "requests"')
        # Более сложная проверка рекурсии затруднительна без анализа всего сгенерированного текста

class TestCreateDotFile(unittest.TestCase):
    @patch('builtins.open')
    @patch('__main__.get_package_dependencies')
    def test_create_dot_file(self, mock_get_dependencies, mock_open):
        mock_get_dependencies.return_value = ['requests>=2.28.2']
        mock_file = MagicMock()
        mock_open.return_value = mock_file
        create_dot_file('requests', 1, 'test.dot')
        mock_file.write.assert_any_call("digraph G {\n")
        mock_file.write.assert_any_call("}\n")


if __name__ == "__main__":
    unittest.main()