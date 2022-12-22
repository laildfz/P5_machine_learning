DECLARE
@start_date DATE
DECLARE
@end_date DATE

SET @start_date = '2019-01-01'
SET @end_date   = '2022-11-01'

SELECT p.Id,
       p.CreationDate,
       p.Title,
       p.Body,
       p.Tags,
       p.ViewCount,
       p.CommentCount,
       p.AnswerCount,
       p.Score
FROM Posts as p
         LEFT JOIN PostTypes as t ON p.PostTypeId = t.Id
WHERE p.CreationDate between @start_date and @end_date
  AND t.Name = 'Question'
  AND p.ViewCount > 20
  AND p.CommentCount > 5
  AND p.AnswerCount > 0
  AND p.Score > 5
  AND LEN(Tags) - LEN(REPLACE(Tags, '<','')) > 2