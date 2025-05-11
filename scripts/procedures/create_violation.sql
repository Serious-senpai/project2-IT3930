CREATE OR ALTER PROCEDURE create_violation
    @CreatorId BIGINT,
    @Category TINYINT,
    @Plate VARCHAR(12),
    @FineVnd BIGINT,
    @VideoUrl NVARCHAR(2048)
AS
BEGIN
    SET NOCOUNT ON

    DECLARE @Id BIGINT
    EXECUTE generate_id @Id = @Id OUTPUT

    INSERT INTO IT3930_Violations (id, creator_id, category, plate, fine_vnd, video_url)
    OUTPUT INSERTED.id
    VALUES (@Id, @CreatorId, @Category, @Plate, @FineVnd, @VideoUrl)
END
