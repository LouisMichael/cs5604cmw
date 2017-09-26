raw_data = LOAD '/user/cs5604f17_cmw/html.csv' USING PigStorage(',') AS (
           url:chararray,
           html:chararray
);

-- To dump the data from PIG Storage to stdout
/* dump raw_data; */

-- Use HBase storage handler to map data from PIG to HBase
--NOTE: In this case, custno (first unique column) will be considered as row key.

STORE raw_data INTO 'hbase://cmwf17-test' USING org.apache.pig.backend.hadoop.hbase.HBaseStorage(
'webpage:url
 webpage:html'
);
