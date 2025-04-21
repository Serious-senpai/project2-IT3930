CREATE OR ALTER PROCEDURE create_violation
    @Category TINYINT,
    @Plate NVARCHAR(12),
    @FineVnd BIGINT,
    @VideoUrl NVARCHAR(2048)
AS
BEGIN
    SET NOCOUNT ON

    DECLARE @Id BIGINT
    EXECUTE generate_id @Id = @Id OUTPUT

    INSERT INTO Violations (id, category, plate, fine_vnd, video_url)
    VALUES (@Id, @Category, @Plate, @FineVnd, @VideoUrl)
END
