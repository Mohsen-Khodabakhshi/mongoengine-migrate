from copy import deepcopy

import pytest

from mongoengine_migrate.actions import AlterDocument
from mongoengine_migrate.exceptions import SchemaError


class TestAlterDocument:
    def test_forward__on_new_collection_specified__should_rename_collection(self,
                                                                            load_fixture,
                                                                            test_db,
                                                                            dump_db):
        schema = load_fixture('schema1').get_schema()
        dump = dict(dump_db())

        action = AlterDocument('Schema1Doc1', collection='new_name1')
        action.prepare(test_db, schema)
        expect = deepcopy(dump)
        expect['new_name1'] = expect.pop('schema1_doc1')

        action.run_forward()

        assert expect == dict(dump_db())

    def test_forward__on_unexistance_collection_specified__should_do_nothing(self,
                                                                             load_fixture,
                                                                             test_db,
                                                                             dump_db):
        schema = load_fixture('schema1').get_schema()
        schema['Schema1Doc1'].parameters['collection'] = 'unknown_collection'
        dump = dict(dump_db())

        action = AlterDocument('Schema1Doc1', collection='new_name1')
        action.prepare(test_db, schema)

        action.run_forward()

        assert dump == dict(dump_db())

    def test_backward__on_new_collection_specified__should_rename_collection_back(self,
                                                                                  load_fixture,
                                                                                  test_db,
                                                                                  dump_db):
        schema = load_fixture('schema1').get_schema()
        test_db['schema1_doc1'].rename('new_name1')
        dump = dict(dump_db())

        action = AlterDocument('Schema1Doc1', collection='new_name1')
        action.prepare(test_db, schema)
        expect = deepcopy(dump)
        expect['schema1_doc1'] = expect.pop('new_name1')

        action.run_backward()

        assert expect == dict(dump_db())

    def test_backward__on_unexistance_collection_specified__should_do_nothing(self,
                                                                              load_fixture,
                                                                              test_db,
                                                                              dump_db):
        schema = load_fixture('schema1').get_schema()
        test_db['schema1_doc1'].rename('unknown_collection')
        dump = dict(dump_db())

        action = AlterDocument('Schema1Doc1', collection='new_name1')
        action.prepare(test_db, schema)

        action.run_backward()

        assert dump == dict(dump_db())

    def test_prepare__if_such_document_is_not_in_schema__should_raise_error(self,
                                                                            load_fixture,
                                                                            test_db):
        schema = load_fixture('schema1').get_schema()
        del schema['Schema1Doc1']

        action = AlterDocument('Schema1Doc1')

        with pytest.raises(SchemaError):
            action.prepare(test_db, schema)