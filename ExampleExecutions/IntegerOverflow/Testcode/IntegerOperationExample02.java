import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;

public class IntegerOperationExample02 {

    public void scenario1() throws Throwable {
        byte data;
        if (true) {
            data = -1;
            BufferedReader readerBuffered = null;
            InputStreamReader readerInputStream = null;
            try {
                readerInputStream = new InputStreamReader(System.in, "UTF-8");
                readerBuffered = new BufferedReader(readerInputStream);
                String stringNumber = readerBuffered.readLine();
                if (stringNumber != null) {
                    data = Byte.parseByte(stringNumber.trim());
                }
            } catch (IOException exceptIO) {
                Logger.getLogger(IntegerOperationExample02.class.getName()).log(Level.WARNING, "Error reading stream", exceptIO);
            } catch (NumberFormatException exceptNumberFormat) {
                Logger.getLogger(IntegerOperationExample02.class.getName()).log(Level.WARNING, "Error parsing number", exceptNumberFormat);
            } finally {
                try {
                    if (readerBuffered != null) {
                        readerBuffered.close();
                    }
                } catch (IOException exceptIO) {
                    Logger.getLogger(IntegerOperationExample02.class.getName()).log(Level.WARNING, "Error closing BufferedReader", exceptIO);
                } finally {
                    try {
                        if (readerInputStream != null) {
                            readerInputStream.close();
                        }
                    } catch (IOException exceptIO) {
                        Logger.getLogger(IntegerOperationExample02.class.getName()).log(Level.WARNING, "Error closing InputStreamReader", exceptIO);
                    }
                }
            }
        } else {
            data = 0;
        }

        if (true) {
            byte result = (byte)(data + 1);
            System.out.println("result: " + result);
        }
    }

    private void scenario2() throws Throwable {
        byte data;
        if (false) {
            data = 0;
        } else {
            data = 2;
        }

        if (true) {
            byte result = (byte)(data + 1);
            System.out.println("result: " + result);
        }
    }

    private void scenario3() throws Throwable {
        byte data;
        if (true) {
            data = 2;
        } else {
            data = 0;
        }

        if (true) {
            byte result = (byte)(data + 1);
            System.out.println("result: " + result);
        }
    }

    private void scenario4() throws Throwable {
        byte data;
        if (true) {
            data = -1;
            BufferedReader readerBuffered = null;
            InputStreamReader readerInputStream = null;
            try {
                readerInputStream = new InputStreamReader(System.in, "UTF-8");
                readerBuffered = new BufferedReader(readerInputStream);
                String stringNumber = readerBuffered.readLine();
                if (stringNumber != null) {
                    data = Byte.parseByte(stringNumber.trim());
                }
            } catch (IOException exceptIO) {
                Logger.getLogger(IntegerOperationExample02.class.getName()).log(Level.WARNING, "Error reading stream", exceptIO);
            } catch (NumberFormatException exceptNumberFormat) {
                Logger.getLogger(IntegerOperationExample02.class.getName()).log(Level.WARNING, "Error parsing number", exceptNumberFormat);
            } finally {
                try {
                    if (readerBuffered != null) {
                        readerBuffered.close();
                    }
                } catch (IOException exceptIO) {
                    Logger.getLogger(IntegerOperationExample02.class.getName()).log(Level.WARNING, "Error closing BufferedReader", exceptIO);
                } finally {
                    try {
                        if (readerInputStream != null) {
                            readerInputStream.close();
                        }
                    } catch (IOException exceptIO) {
                        Logger.getLogger(IntegerOperationExample02.class.getName()).log(Level.WARNING, "Error closing InputStreamReader", exceptIO);
                    }
                }
            }
        } else {
            data = 0;
        }

        if (false) {
            System.out.println("Fixed string");
        } else {
            if (data < Byte.MAX_VALUE) {
                byte result = (byte)(data + 1);
                System.out.println("result: " + result);
            } else {
                System.out.println("data value is too large to perform addition.");
            }
        }
    }

    private void scenario5() throws Throwable {
        byte data;
        if (true) {
            data = -1;
            BufferedReader readerBuffered = null;
            InputStreamReader readerInputStream = null;
            try {
                readerInputStream = new InputStreamReader(System.in, "UTF-8");
                readerBuffered = new BufferedReader(readerInputStream);
                String stringNumber = readerBuffered.readLine();
                if (stringNumber != null) {
                    data = Byte.parseByte(stringNumber.trim());
                }
            } catch (IOException exceptIO) {
                Logger.getLogger(IntegerOperationExample02.class.getName()).log(Level.WARNING, "Error reading stream", exceptIO);
            } catch (NumberFormatException exceptNumberFormat) {
                Logger.getLogger(IntegerOperationExample02.class.getName()).log(Level.WARNING, "Error parsing number", exceptNumberFormat);
            } finally {
                try {
                    if (readerBuffered != null) {
                        readerBuffered.close();
                    }
                } catch (IOException exceptIO) {
                    Logger.getLogger(IntegerOperationExample02.class.getName()).log(Level.WARNING, "Error closing BufferedReader", exceptIO);
                } finally {
                    try {
                        if (readerInputStream != null) {
                            readerInputStream.close();
                        }
                    } catch (IOException exceptIO) {
                        Logger.getLogger(IntegerOperationExample02.class.getName()).log(Level.WARNING, "Error closing InputStreamReader", exceptIO);
                    }
                }
            }
        } else {
            data = 0;
        }

        if (true) {
            if (data < Byte.MAX_VALUE) {
                byte result = (byte)(data + 1);
                System.out.println("result: " + result);
            } else {
                System.out.println("data value is too large to perform addition.");
            }
        }
    }

    public void runScenarios() throws Throwable {
        scenario2();
        scenario3();
        scenario4();
        scenario5();
    }

    public static void main(String[] args) throws Throwable {
        IntegerOperationExample02 example = new IntegerOperationExample02();
        example.runScenarios();
        example.scenario1();
    }
}
