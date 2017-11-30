import java.io.IOException;
import org.apache.hadoop.hbase.client.ResultScanner;
import org.apache.hadoop.conf.Configuration;

import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.util.Bytes;

public class RetriveData{

   public static void main(String[] args) throws IOException, Exception{
   
      // Instantiating Configuration class
      Configuration config = HBaseConfiguration.create();

      // Instantiating HTable class
      HTable table = new HTable(config, "getar-cs5604f17");

      // Instantiating Get class
      Scan s = new Scan();

      s.addColumn(Bytes.toBytes("clean-tweet"),Bytes.toBytes("long-url"));
      s.addColumn(Bytes.toBytes("tweet"),Bytes.toBytes("collection-id"));
      s.addColumn(Bytes.toBytes("tweet"),Bytes.toBytes("collection-name"));
      s.addColumn(Bytes.toBytes("tweet"),Bytes.toBytes("tweet-id"));
      ResultScanner scanner = table.getScanner(s);

      // Reading values from scan result
      for (Result result = scanner.next(); result != null; result = scanner.next()){
         System.out.println("Found row : " + result);
      }
      //closing the scanner
      scanner.close();
   }
}