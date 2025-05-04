CREATE OR ALTER VIEW view_vehicles AS
    SELECT
        vh.plate AS vehicle_plate,
        COUNT(vl.id) AS vehicle_violations_count,
        u.user_id,
        u.user_fullname,
        u.user_phone,
        u.user_permissions,
        u.user_vehicles_count,
        u.user_violations_count
    FROM IT3930_Vehicles vh
    INNER JOIN view_users u ON vh.user_id = u.user_id
    LEFT JOIN IT3930_Violations vl ON vh.plate = vl.plate
    GROUP BY
        vh.plate,
        u.user_id,
        u.user_fullname,
        u.user_phone,
        u.user_permissions,
        u.user_vehicles_count,
        u.user_violations_count
