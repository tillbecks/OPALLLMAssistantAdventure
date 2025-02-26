import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;

public class GenericExecutor1 {
    private static final Logger LOGGER = Logger.getLogger(GenericExecutor1.class.getName());

    public void method1() throws Throwable {
        String inputData;
        
        /* Read environment variable */
        inputData = System.getenv("INPUT_VAR");

        String baseCommand;
        if (System.getProperty("os.name").toLowerCase().contains("win")) {
            baseCommand = "cmd.exe /c dir ";
        } else {
            baseCommand = "/bin/ls ";
        }

        /* Potential risk: command execution */
        try {
            Process process = Runtime.getRuntime().exec(baseCommand + inputData);
            process.waitFor();
        } catch (IOException | InterruptedException e) {
            LOGGER.log(Level.WARNING, "Error executing command", e);
        }
    }

    public static void main(String[] args) throws Throwable {
        GenericExecutor1 instance = new GenericExecutor1();
        instance.method1();
    }
}
