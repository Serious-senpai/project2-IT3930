CREATE OR ALTER VIEW view_refutations AS
    SELECT
        r.id AS refutation_id,
        r.message AS refutation_message,
        r.response AS refutation_response,
        u.user_id AS author_id,
        u.user_fullname AS author_fullname,
        u.user_phone AS author_phone,
        u.user_permissions AS author_permissions,
        u.user_vehicles_count AS author_vehicles_count,
        u.user_violations_count AS author_violations_count,
        vl.violation_id,
        vl.creator_id,
        vl.creator_fullname,
        vl.creator_phone,
        vl.creator_permissions,
        vl.creator_vehicles_count,
        vl.creator_violations_count,
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
        vl.user_violations_count
    FROM IT3930_Refutations r
    INNER JOIN view_users u ON u.user_id = r.user_id
    INNER JOIN view_violations vl ON vl.violation_id = r.violation_id
