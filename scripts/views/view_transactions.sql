CREATE OR ALTER VIEW view_transactions AS
    SELECT
        t.id AS transaction_id,
        vl.violation_id,
        vl.violation_category,
        vl.violation_fine_vnd,
        vl.violation_video_url,
        vl.violation_refutations_count,
        vl.vehicle_plate,
        vl.vehicle_violations_count,
        vl.user_id,
        vl.user_fullname,
        vl.user_phone,
        vl.user_permissions,
        vl.user_vehicles_count,
        vl.user_violations_count,
        u.user_id AS payer_id,
        u.user_fullname AS payer_fullname,
        u.user_phone AS payer_phone,
        u.user_permissions AS payer_permissions,
        u.user_vehicles_count AS payer_vehicles_count,
        u.user_violations_count AS payer_violations_count
    FROM IT3930_Transactions t
    INNER JOIN view_violations vl ON t.violation_id = vl.violation_id
    INNER JOIN view_users u on t.user_id = u.user_id
