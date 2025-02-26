package testcode;

public class Level3 {
    private String message;

    public Level3(String message) {
        this.message = message;
    }

    public void passToLeak() {
        IndirectStringLeak.leak(message);
    }
} 