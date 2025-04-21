CREATE OR ALTER VIEW violations_view AS
    SELECT
        v.id AS v_id,
        v.category AS v_category,
        v.plate AS v_plate,
        v.fine_vnd AS v_fine_vnd,
        v.video_url AS v_video_url,
        COUNT(r.id) AS v_refutations_count, -- COUNT() ignores NULLs
        t.id AS v_transaction_id
    FROM Violations v
    LEFT JOIN Refutations r ON v.id = r.violation_id
    LEFT JOIN Transactions t ON v.id = t.violation_id
    GROUP BY v.id, v.category, v.plate, v.fine_vnd, v.video_url, t.id;
