import pytest
from uuid import UUID
from datetime import datetime
from pydantic import ValidationError
from app.schemas.avaliations import (
    AvaliationCreate,
    AvaliationUpdate,
    AvaliationOut,
    CompanyAvaliationsSummary
)
from app.models.company import CompanyType

# =====================================
# AvaliationCreate
# =====================================
def test_avaliation_create_valid():
    data = {
        "company_uuid": "11111111-1111-1111-1111-111111111111",
        "discard_uuid": "22222222-2222-2222-2222-222222222222",
        "score": 4,
        "comment": "Comentário ok"
    }
    aval = AvaliationCreate(**data)
    assert aval.score == 4
    assert aval.comment == "Comentário ok"

def test_avaliation_create_invalid_score():
    data = {
        "company_uuid": "11111111-1111-1111-1111-111111111111",
        "discard_uuid": "22222222-2222-2222-2222-222222222222",
        "score": 6,  # inválido
    }
    with pytest.raises(ValidationError):
        AvaliationCreate(**data)

def test_avaliation_create_comment_too_long():
    data = {
        "company_uuid": "11111111-1111-1111-1111-111111111111",
        "discard_uuid": "22222222-2222-2222-2222-222222222222",
        "score": 3,
        "comment": "x"*501  # > 500
    }
    with pytest.raises(ValidationError):
        AvaliationCreate(**data)


# =====================================
# AvaliationUpdate
# =====================================
def test_avaliation_update_valid():
    upd = AvaliationUpdate(comment="novo", score=5)
    assert upd.comment == "novo"
    assert upd.score == 5

def test_avaliation_update_only_comment():
    upd = AvaliationUpdate(comment="só comentário")
    assert upd.comment == "só comentário"
    assert upd.score is None

def test_avaliation_update_only_score():
    upd = AvaliationUpdate(score=2)
    assert upd.comment is None
    assert upd.score == 2

def test_avaliation_update_none_fields():
    with pytest.raises(ValidationError):
        AvaliationUpdate()


# =====================================
# AvaliationOut
# =====================================
def test_avaliation_out_from_rating_valid():
    fake_rating = type("FakeRating", (), {})()
    fake_rating.uuid = UUID("11111111-1111-1111-1111-111111111111")
    fake_rating.score = 4
    fake_rating.comment = "ok"
    fake_rating.discard_uuid = UUID("22222222-2222-2222-2222-222222222222")
    fake_rating.company_uuid = UUID("33333333-3333-3333-3333-333333333333")
    fake_rating.company_avaliadora_uuid = UUID("44444444-4444-4444-4444-444444444444")
    fake_rating.created_at = datetime.utcnow()
    fake_rating.updated_at = datetime.utcnow()

    out = AvaliationOut.from_rating(fake_rating)
    assert out.score == 4
    assert out.comment == "ok"
    assert isinstance(out.discard_uuid, UUID)

def test_avaliation_out_invalid_score():
    fake_rating = type("FakeRating", (), {})()
    fake_rating.uuid = UUID("11111111-1111-1111-1111-111111111111")
    fake_rating.score = 6  # inválido
    fake_rating.comment = "ok"
    fake_rating.discard_uuid = UUID("22222222-2222-2222-2222-222222222222")
    fake_rating.company_uuid = UUID("33333333-3333-3333-3333-333333333333")
    fake_rating.company_avaliadora_uuid = UUID("44444444-4444-4444-4444-444444444444")
    fake_rating.created_at = datetime.utcnow()
    fake_rating.updated_at = datetime.utcnow()

    with pytest.raises(ValidationError):
        AvaliationOut.from_rating(fake_rating)


# =====================================
# CompanyAvaliationsSummary
# =====================================
def test_summary_valid():
    summary = CompanyAvaliationsSummary(
        company_uuid="11111111-1111-1111-1111-111111111111",
        company_name="Empresa X",
        company_type=CompanyType.EMPRESA_COLETORA,
        average_rating=4.5,
        total_ratings=10,
        rating_distribution={1:1,2:0,3:2,4:3,5:4}
    )
    assert summary.average_rating == 4.5

def test_summary_invalid_average():
    with pytest.raises(ValidationError):
        CompanyAvaliationsSummary(
            company_uuid="11111111-1111-1111-1111-111111111111",
            company_name="Empresa X",
            company_type=CompanyType.EMPRESA_COLETORA,
            average_rating=6,  # inválido
            total_ratings=10,
            rating_distribution={1:1,2:0,3:2,4:3,5:4}
        )
