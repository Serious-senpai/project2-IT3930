CREATE OR ALTER VIEW view_violations AS
    SELECT
        vl.id AS violation_id,
        vl.category AS violation_category,
        vl.fine_vnd AS violation_fine_vnd,
        vl.video_url AS violation_video_url,
        COUNT(r.id) AS violation_refutations_count,
        vh.vehicle_plate,
        vh.vehicle_violations_count,
        vh.user_id,
        vh.user_fullname,
        vh.user_phone,
        vh.user_permissions,
        vh.user_vehicles_count,
        vh.user_violations_count
    FROM IT3930_Violations vl
    INNER JOIN view_vehicles vh ON vl.plate = vh.vehicle_plate
    LEFT JOIN IT3930_Refutations r ON vl.id = r.violation_id
    GROUP BY
        vl.id,
        vl.category,
        vl.fine_vnd,
        vl.video_url,
        vh.vehicle_plate,
        vh.vehicle_violations_count,
        vh.user_id,
        vh.user_fullname,
        vh.user_phone,
        vh.user_permissions,
        vh.user_vehicles_count,
        vh.user_violations_count
