CREATE OR ALTER VIEW view_refutations AS
    SELECT
        r.id AS refutation_id,
        r.message AS refutation_message,
        r.response AS refutation_response,
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
        vl.user_violations_count
    FROM IT3930_Refutations r
    INNER JOIN view_violations vl ON vl.violation_id = r.violation_id
