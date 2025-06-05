CREATE OR ALTER PROCEDURE create_detected
    @Category TINYINT,
    @Plate VARCHAR(12),
    @VideoUrl NVARCHAR(2048)
AS
BEGIN
    SET NOCOUNT ON

    DECLARE @Id BIGINT
    EXECUTE generate_id @Id = @Id OUTPUT

    INSERT INTO IT3930_Detected (id, category, plate, video_url)
    OUTPUT INSERTED.id
    VALUES (@Id, @Category, @Plate, @VideoUrl)
END
