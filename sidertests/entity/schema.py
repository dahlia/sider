import pickle
import datetime
from attest import Tests, assert_hook, raises
from ..env import get_session, key
from sider.entity.schema import Field, Schema, ConstantFunction
from sider.entity.exceptions import KeyFieldError
from sider.types import UnicodeString, Date, TZDateTime
from sider.datetime import utcnow


tests = Tests()


@tests.test
def field_key():
    field = Field(Date, key=True)
    assert isinstance(field.value_type, Date)
    assert field.required
    assert field.unique
    assert field.key
    with raises(TypeError):
        Field(Date, unique=False, key=True)
    with raises(TypeError):
        Field(Date, required=False, key=True)


@tests.test
def field_default():
    field = Field(Date, default=utcnow)
    assert abs(utcnow() - field.default()) < datetime.timedelta(minutes=1)
    field2 = Field(UnicodeString, default=u'default string')
    assert field2.default() == u'default string'


def make_schema():
    return Schema(
        login=Field(UnicodeString, required=True, key=True),
        name=Field(UnicodeString, required=True),
        url=Field(UnicodeString, unique=True),
        dob=Field(Date),
        created_at=Field(TZDateTime, required=True, default=utcnow)
    )


@tests.test
def schema_fields():
    user_schema = make_schema()
    assert len(user_schema.fields) == 5
    assert isinstance(user_schema.fields['login'], Field)
    assert isinstance(user_schema.fields['login'].value_type, UnicodeString)
    assert user_schema.fields['login'].required
    assert user_schema.fields['login'].key
    assert user_schema.fields['login'].unique
    assert isinstance(user_schema.fields['name'], Field)
    assert isinstance(user_schema.fields['name'].value_type, UnicodeString)
    assert user_schema.fields['name'].required
    assert not user_schema.fields['name'].key
    assert not user_schema.fields['name'].unique
    assert isinstance(user_schema.fields['url'], Field)
    assert isinstance(user_schema.fields['url'].value_type, UnicodeString)
    assert not user_schema.fields['url'].required
    assert not user_schema.fields['url'].key
    assert user_schema.fields['url'].unique


@tests.test
def schema_key_field():
    user_schema = make_schema()
    assert user_schema.key_field_name == 'login'
    assert user_schema.key_field is user_schema.fields['login']
    with raises(KeyFieldError):
        Schema(
            a=Field(UnicodeString, key=True),
            b=Field(UnicodeString, key=True)
        )
    with raises(KeyFieldError):
        Schema(
            a=Field(UnicodeString),
            b=Field(UnicodeString)
        )


@tests.test
def constant_func():
    cf = ConstantFunction(1234)
    assert cf() == 1234

