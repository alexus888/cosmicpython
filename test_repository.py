# pylint: disable=protected-access
from sqlalchemy import text
import model
import repository


def test_repository_can_save_a_batch(session):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.SqlAlchemyRepository(session)
    repo.add(batch)
    session.commit()

    rows = session.execute(
        text('SELECT reference, sku, _purchased_quantity, eta FROM "batches"')
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]


def insert_order_line(session):
    query = (
        "INSERT INTO order_lines (orderid, sku, qty)"
        ' VALUES ("order1", "GENERIC-SOFA", 12) returning id'
    )
    result = session.execute(text(query))
    return result.fetchone().id


def insert_batch(session, batch_id):
    query = (
        "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
        ' VALUES (:batch_id, "GENERIC-SOFA", 100, null) returning id'
    )
    result = session.execute(text(query), dict(batch_id=batch_id))
    return result.fetchone().id


def insert_allocation(session, orderline_id, batch_id):
    session.execute(
        text(
            "INSERT INTO allocations (orderline_id, batch_id)"
            " VALUES (:orderline_id, :batch_id)"
        ),
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


def test_repository_can_retrieve_a_batch_with_allocations(session):
    # arrange
    ref = "batch1"
    expected = model.Batch(ref, "GENERIC-SOFA", 100, eta=None)

    batch_id = insert_batch(session, ref)
    orderline_id = insert_order_line(session)
    insert_allocation(session, orderline_id, batch_id)

    repo = repository.SqlAlchemyRepository(session)

    # act
    retrieved = repo.get("batch1")

    # assert
    assert retrieved == expected  # Batch.__eq__ only compares reference
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {
        model.OrderLine("order1", "GENERIC-SOFA", 12),
    }
