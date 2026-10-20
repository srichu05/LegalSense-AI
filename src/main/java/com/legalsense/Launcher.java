package com.legalsense;

/**
 * Standard launcher to start the JavaFX application from the classpath
 * without module path restrictions under modern JDKs (Java 11+ / Java 21).
 */
public class Launcher {

    public static void main(String[] args) {
        LegalSenseApp.main(args);
    }
}
