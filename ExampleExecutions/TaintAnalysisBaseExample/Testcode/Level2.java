package testcode;

public class Level2 {
    private String message;

    public Level2(String message) {
        this.message = message;
    }

    public void passToLevel3() {
        Level3 level3 = new Level3(message);
        level3.passToLeak();
    }
} 