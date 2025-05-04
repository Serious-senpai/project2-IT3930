CREATE OR ALTER VIEW view_users AS
    SELECT
        u.id as user_id,
        u.fullname as user_fullname,
        u.phone as user_phone,
        u.permissions as user_permissions,
        COUNT(vh.plate) AS user_vehicles_count,
        COUNT(vl.id) AS user_violations_count
    FROM IT3930_Users u
    LEFT JOIN IT3930_Vehicles vh ON u.id = vh.user_id
    LEFT JOIN IT3930_Violations vl ON vh.plate IS NOT DISTINCT FROM vl.plate  /* vh.plate may be NULL */
    GROUP BY u.id, u.fullname, u.phone, u.permissions
