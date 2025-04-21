CREATE OR ALTER VIEW refutations_view AS
    SELECT
        r.id AS r_id,
        r.message AS r_message,
        r.response AS r_response,
        v.v_id,
        v.v_category,
        v.v_plate,
        v.v_fine_vnd,
        v.v_refutations_count,
        v.v_transaction_id
    FROM Refutations r
    INNER JOIN violations_view v ON r.violation_id = v.v_id
