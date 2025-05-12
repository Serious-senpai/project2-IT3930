CREATE OR ALTER PROCEDURE create_vehicle
    @Plate VARCHAR(12),
    @UserId BIGINT
AS
    INSERT INTO IT3930_Vehicles (plate, user_id)
    VALUES (@Plate, @UserId)
