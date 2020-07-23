from copy import deepcopy

import pytest
import jsonpath_rw
import itertools

from mongoengine_migrate.actions import DropField
from mongoengine_migrate.exceptions import SchemaError


class TestDropFieldInDocument:
    def test_forward__should_drop_field(self, load_fixture, test_db, dump_db):
        schema = load_fixture('schema1').get_schema()
        expect = dict(dump_db())
        parser = jsonpath_rw.parse('schema1_doc1[*]')
        for rec in parser.find(expect):
            if 'doc1_str' in rec.value:
                del rec.value['doc1_str']

        action = DropField('Schema1Doc1', 'doc1_str')
        action.prepare(test_db, schema)

        action.run_forward()

        assert expect == dict(dump_db())

    def test_backward__if_default_is_not_set__should_do_nothing(
            self, load_fixture, test_db, dump_db
    ):
        schema = load_fixture('schema1').get_schema()
        dump = dict(dump_db())

        action = DropField('Schema1Doc1', 'doc1_str')
        action.prepare(test_db, schema)

        action.run_backward()

        assert dump == dict(dump_db())

    def test_backward__if_required_and_default_is_set__should_create_field_and_set_a_value(
            self, load_fixture, test_db, dump_db
    ):
        schema = load_fixture('schema1').get_schema()
        default = 'test!'
        schema['Schema1Doc1']['test_field'] = {
            'unique_with': None,
            'null': False,
            'choices': None,
            'default': default,
            'sparse': False,
            'unique': False,
            'required': True,
            'db_field': 'test_field',
            'primary_key': False,
            'type_key': 'StringField',
            'max_length': None,
            'regex': None,
            'min_length': None
        }
        dump = dict(dump_db())
        expect = deepcopy(dump)
        parser = jsonpath_rw.parse('schema1_doc1[*]')
        for rec in parser.find(expect):
            rec.value['test_field'] = default

        action = DropField('Schema1Doc1', 'test_field')
        action.prepare(test_db, schema)

        action.run_backward()
        # print(expect)
        # print('----')
        # print(dict(dump_db()))
        assert expect == dict(dump_db())

    def test_backward__if_required_and_default_is_set_and_field_in_db__should_not_touch_field(
            self, load_fixture, test_db, dump_db
    ):
        schema = load_fixture('schema1').get_schema()
        default = 'test!'
        schema['Schema1Doc1']['test_field'] = {
            'unique_with': None,
            'null': False,
            'choices': None,
            'default': default,
            'sparse': False,
            'unique': False,
            'required': True,
            'db_field': 'test_field',
            'primary_key': False,
            'type_key': 'StringField',
            'max_length': None,
            'regex': None,
            'min_length': None
        }
        ids = set()
        for doc in test_db['schema1_doc1'].find({}, limit=2):
            test_db['schema1_doc1'].update_one({'_id': doc['_id']},
                                               {'$set': {'test_field': 'old_value'}})
            ids.add(doc['_id'])

        action = DropField('Schema1Doc1', 'test_field')
        action.prepare(test_db, schema)

        action.run_backward()

        assert all(d['test_field'] == 'old_value'
                   for d in test_db['schema1_doc1'].find()
                   if d['_id'] in ids)

    def test_prepare__if_such_document_is_not_in_schema__should_raise_error(self,
                                                                            load_fixture,
                                                                            test_db):
        schema = load_fixture('schema1').get_schema()
        del schema['Schema1Doc1']

        action = DropField('Schema1Doc1', 'doc1_str')

        with pytest.raises(SchemaError):
            action.prepare(test_db, schema)

    def test_prepare__if_such_field_in_document_is_not_in_schema__should_raise_error(self,
                                                                                     load_fixture,
                                                                                     test_db):
        schema = load_fixture('schema1').get_schema()

        action = DropField('Schema1Doc1', 'unknown_field')

        with pytest.raises(SchemaError):
            action.prepare(test_db, schema)


class TestCreateFieldEmbedded:
    def test_backward__if_default_is_not_set__should_do_nothing(
            self, load_fixture, test_db, dump_db
    ):
        schema = load_fixture('schema1').get_schema()
        dump = dict(dump_db())

        action = DropField('~Schema1EmbDoc1', 'embdoc1_str')
        action.prepare(test_db, schema)

        action.run_backward()

        assert dump == dict(dump_db())

    def test_backward__if_required_and_default_is_set__should_create_field_and_set_a_value(
            self, load_fixture, test_db, dump_db
    ):
        schema = load_fixture('schema1').get_schema()
        default = 'test!'
        schema['~Schema1EmbDoc1']['test_field'] = {
            'unique_with': None,
            'null': False,
            'choices': None,
            'default': default,
            'sparse': False,
            'unique': False,
            'required': True,
            'db_field': 'test_field',
            'primary_key': False,
            'type_key': 'StringField',
            'max_length': None,
            'regex': None,
            'min_length': None
        }
        dump = dict(dump_db())
        expect = deepcopy(dump)
        parsers = load_fixture('schema1').get_embdoc1_jsonpath_parsers()
        for rec in itertools.chain.from_iterable(p.find(expect) for p in parsers):
            rec.value['test_field'] = default

        action = DropField('~Schema1EmbDoc1', 'test_field')
        action.prepare(test_db, schema)

        action.run_backward()

        assert expect == dict(dump_db())

    def test_forward__should_drop_field(self, load_fixture, test_db, dump_db):
        schema = load_fixture('schema1').get_schema()
        dump = dict(dump_db())
        expect = deepcopy(dump)
        parsers = load_fixture('schema1').get_embdoc1_jsonpath_parsers()
        for rec in itertools.chain.from_iterable(p.find(expect) for p in parsers):
            if 'embdoc1_str' in rec.value:
                del rec.value['embdoc1_str']

        action = DropField('~Schema1EmbDoc1', 'embdoc1_str')
        action.prepare(test_db, schema)

        action.run_forward()

        assert expect == dict(dump_db())