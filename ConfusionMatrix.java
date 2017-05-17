/**
 * Created by samhsu on 5/13/17.
 */

import java.io.*;
import java.util.*;

public class ConfusionMatrix {
    public ConfusionMatrix() {}

    public static void main(String args[]) throws IOException {
        FileReader trueIn = null;
        FileReader approxIn = null;

        File file = new File("out.txt");
        file.createNewFile();
        FileWriter writer = new FileWriter(file);

        HashMap<String, Integer> map = new HashMap();
        int count;

        try {
            trueIn = new FileReader("true.txt");
            approxIn = new FileReader("approx.txt");

            int c1, c2;
            while (((c1 = trueIn.read()) != -1) && ((c2 = approxIn.read()) != -1)) {
                if (map.containsKey(c1 + "," + c2)) {
                    count = map.get(c1 + "," + c2);
                    map.put(c1 + "," + c2, count + 1);
                }
                else {
                    map.put(c1 + "," + c2, 1);
                }
            }
        }
        finally {
            trueIn.close();
            approxIn.close();
        }

        Set keys = map.keySet();
        int val;
        Object[] keysArray = keys.toArray();

        for (int i = 0; i < keys.size(); i++) {
            val = map.get((String)keysArray[i]);
            writer.write(keysArray[i] + "," + Integer.toString(val) + "\n");
        }

        writer.close();
    }
}
