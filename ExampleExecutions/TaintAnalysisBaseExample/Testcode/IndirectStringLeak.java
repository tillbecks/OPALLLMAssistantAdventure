package testcode;

public class IndirectStringLeak {
    public static String getMessage() {
        return "This is a leaked message.";
    }

    public static void main(String[] args) {
        String message = getMessage();
        Level1 level1 = new Level1(message);
        level1.passToLevel2();
    }


    // The leak method
    public static void leak(String message) {
        String x = message;
        System.out.println(x);
        String y = x;
        System.out.println("Leaked message: " + y);
    }
} 