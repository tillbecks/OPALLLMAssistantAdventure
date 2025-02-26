import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;

public class GenericExecutor2 {
    private static final Logger LOGGER = Logger.getLogger(GenericExecutor2.class.getName());

    public void method2() throws Throwable {
        String fixedValue = "default_directory";
        
        String baseCommand;
        if (System.getProperty("os.name").toLowerCase().contains("win")) {
            baseCommand = "cmd.exe /c dir ";
        } else {
            baseCommand = "/bin/ls ";
        }

        /* Safe execution with predefined input */
        try {
            Process process = Runtime.getRuntime().exec(baseCommand + fixedValue);
            process.waitFor();
        } catch (IOException | InterruptedException e) {
            LOGGER.log(Level.WARNING, "Error executing command", e);
        }
    }

    public static void main(String[] args) throws Throwable {
        GenericExecutor2 instance = new GenericExecutor2();
        instance.method2();
    }
}
