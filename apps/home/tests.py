# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.test import TestCase
from apps.home.controllers.base import BaseController
from apps.home.factories.configuration import ConfigurationFactory
from apps.home.store.dynamodb import DynamoAdapter
from apps.home.entities.features import Feature

from apps.home.factories.session import Boto3SessionFactory

# Create your tests here.
class BaseControllerTests(TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._session = Boto3SessionFactory.get_or_create()
        self._document_adapter = DynamoAdapter(session=self._session)
        self._configuration = ConfigurationFactory.get_or_create(session=self._session, document_adapter=self._document_adapter, environment="tests")

    def test_generate_table(self):
        controller = BaseController(session=self._session, document_adapter=self._document_adapter, configuration=self._configuration, data_klass=Feature)
        assert controller
        data = [{
                "origin": "fg_client_unit_group_test",
                "name": "day",
                "updated_at": "1645631141",
                "created_at": "1645631145",
                "dag": "",
                "source": "",
                "type": "int",
                "desc": "particao: dia"
                },
                {
                "origin": "fg_client_unit_group_test",
                "name": "day",
                "updated_at": "1645631141",
                "created_at": "1645631145",
                "dag": "",
                "source": "",
                "type": "int",
                "desc": "particao: dia"
                },
                {
                "origin": "fg_client_unit_group_test",
                "name": "day",
                "updated_at": "1645631141",
                "created_at": "1645631145",
                "dag": "",
                "source": "",
                "type": "int",
                "desc": "particao: dia"
                }]
        rendered_table = controller.render_table(data) 
        assert len(rendered_table.rows) == 3 
        assert len(rendered_table.base_columns) == 8
