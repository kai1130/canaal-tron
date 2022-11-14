CREATE OR REPLACE STREAM "DESTINATION_SQL_STREAM" ("block" INTEGER, 
                                                   avg_pos DECIMAL(4,3),
                                                   avg_neu DECIMAL(4,3),
                                                   avg_neg DECIMAL(4,3),
                                                   total_twt INTEGER);
CREATE OR REPLACE PUMP "STREAM_PUMP" AS 
  INSERT INTO "DESTINATION_SQL_STREAM"
      SELECT STREAM AVG("block"),
                    AVG("pos") as avg_pos,
                    AVG("neu") as avg_neu,
                    AVG("neg") as avg_neg,
                    COUNT(*) as total_twt
      FROM   "SOURCE_SQL_STREAM_001"
      GROUP BY MONOTONIC("block");