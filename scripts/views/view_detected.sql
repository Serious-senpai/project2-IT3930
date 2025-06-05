CREATE OR ALTER VIEW view_detected AS
    SELECT
        d.id AS detected_id,
        d.category AS detected_category,
        d.video_url AS detected_video_url,
        vh.vehicle_plate,
        vh.vehicle_violations_count,
        vh.user_id,
        vh.user_fullname,
        vh.user_phone,
        vh.user_permissions,
        vh.user_vehicles_count,
        vh.user_violations_count
    FROM IT3930_Detected d
    INNER JOIN view_vehicles vh ON d.plate = vh.vehicle_plate
    GROUP BY
        d.id,
        d.category,
        d.video_url,
        vh.vehicle_plate,
        vh.vehicle_violations_count,
        vh.user_id,
        vh.user_fullname,
        vh.user_phone,
        vh.user_permissions,
        vh.user_vehicles_count,
        vh.user_violations_count
