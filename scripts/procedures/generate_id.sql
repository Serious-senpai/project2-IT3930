CREATE OR ALTER PROCEDURE generate_id
    @Id BIGINT OUTPUT
AS
BEGIN
    SET NOCOUNT ON

    DECLARE @Epoch DATETIME2
    SELECT @Epoch = value FROM IT3930_ConfigDateTime2 WHERE name = 'epoch'

    DECLARE @Now DATETIME2 = SYSUTCDATETIME()
    DECLARE @TimestampMs BIGINT = DATEDIFF_BIG(MILLISECOND, @Epoch, @Now)
    DECLARE @TailTable TABLE (value BIGINT)

    UPDATE IT3930_ConfigBigInt
    SET value = (value + 1) & 0xFFFF
    OUTPUT DELETED.value INTO @TailTable
    WHERE name = 'id_counter'

    DECLARE @Tail BIGINT = (SELECT value FROM @TailTable)
    SET @Id = (@TimestampMs << 16) | @Tail
END
