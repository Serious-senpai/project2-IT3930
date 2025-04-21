CREATE OR ALTER PROCEDURE create_violation
    @Category TINYINT,
    @Plate VARCHAR(12),
    @Fine_vnd BIGINT
AS
BEGIN
    SET NOCOUNT ON

    DECLARE @Id BIGINT
    EXECUTE generate_id @Id = @Id OUTPUT

    INSERT INTO Violations (id, category, plate, fine_vnd)
    VALUES (@Id, @Category, @Plate, @Fine_vnd)
END
