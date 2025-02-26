package testcode;

public class Level1 {
    private String message;

    public Level1(String message) {
        this.message = message;
    }

    public void passToLevel2() {
        Level2 level2 = new Level2(message);
        level2.passToLevel3();
    }
} 