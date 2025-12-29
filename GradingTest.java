import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.UUID;
import java.time.LocalDateTime;

// We use reflection to load classes to avoid compilation errors in the test runner 
// if the student's code is broken or missing classes.
// However, for the test to run, the student's classes must be on the classpath.

public class GradingTest {

    private static final String PLAYER_CLASS = "Model.Player";
    private static final String SCORE_CLASS = "Model.Score";

    @Test
    @DisplayName("1. Test Player Creation")
    void testPlayerCreation() {
        try {
            Class<?> playerClass = Class.forName(PLAYER_CLASS);
            // Constructor(String)
            try {
                Object player = playerClass.getConstructor(String.class).newInstance("TestUser");
                assertNotNull(player, "Player instance should be created");
                
                // Check fields
                checkField(player, "username", "TestUser");
                checkField(player, "totalCoins", 0);
                checkField(player, "totalDistance", 0);
                // Check UUID is not null
                Field idField = getField(playerClass, "playerId", "playerID");
                idField.setAccessible(true);
                assertNotNull(idField.get(player), "Player ID should be generated");
                
            } catch (Exception e) {
                // If constructor fails (e.g. UUID.fromString("TestUser"))
                fail("Player constructor failed: " + e.getCause());
            }
        } catch (ClassNotFoundException e) {
            fail("Model.Player class not found");
        }
    }

    @Test
    @DisplayName("2. Test Player Update High Score")
    void testPlayerUpdateHighScore() {
        try {
            Class<?> playerClass = Class.forName(PLAYER_CLASS);
            Object player = playerClass.getConstructor(String.class).newInstance("TestUser"); // Might fail if constructor is broken
            
            Method updateMethod = playerClass.getMethod("updateHighScore", int.class);
            
            // Update to 100
            updateMethod.invoke(player, 100);
            checkField(player, "highscore", 100, "highScore"); // Check 'highscore' or 'highScore'
            
            // Update to 50 (should stay 100)
            updateMethod.invoke(player, 50);
            checkField(player, "highscore", 100, "highScore");
            
            // Update to 200
            updateMethod.invoke(player, 200);
            checkField(player, "highscore", 200, "highScore");
            
        } catch (Exception e) {
             // If constructor failed earlier, this test will also fail, which is expected.
             // We catch generic Exception to handle Reflection exceptions.
             if (e.getCause() != null) {
                 fail("Test failed with exception: " + e.getCause().getMessage());
             } else {
                 fail("Test failed: " + e.getMessage());
             }
        }
    }

    @Test
    @DisplayName("3. Test Player Add Coins and Distance")
    void testPlayerAddCoinsAndDistance() {
        try {
            Class<?> playerClass = Class.forName(PLAYER_CLASS);
            Object player = playerClass.getConstructor(String.class).newInstance("TestUser");
            
            Method addCoins = playerClass.getMethod("addCoins", int.class);
            Method addDistance = playerClass.getMethod("addDistance", int.class);
            
            addCoins.invoke(player, 50);
            checkField(player, "totalCoins", 50);
            
            addCoins.invoke(player, 25);
            checkField(player, "totalCoins", 75);
            
            addDistance.invoke(player, 1000);
            checkField(player, "totalDistance", 1000);
            
        } catch (Exception e) {
            fail("Test failed: " + e.getMessage());
        }
    }

    @Test
    @DisplayName("4. Test Score Creation and Getters")
    void testScoreCreation() {
        try {
            Class<?> scoreClass = Class.forName(SCORE_CLASS);
            UUID pid = UUID.randomUUID();
            
            // Constructor(UUID, int, int, int)
            Object score = scoreClass.getConstructor(UUID.class, int.class, int.class, int.class)
                            .newInstance(pid, 1000, 50, 200);
            
            // Check getters
            Method getValue = scoreClass.getMethod("getValue");
            Method getCoins = scoreClass.getMethod("getCoinsCollected");
            Method getDistance = scoreClass.getMethod("getDistance");
            
            assertEquals(1000, getValue.invoke(score), "getValue should return 1000");
            assertEquals(50, getCoins.invoke(score), "getCoinsCollected should return 50");
            assertEquals(200, getDistance.invoke(score), "getDistance should return 200");
            
        } catch (ClassNotFoundException e) {
            fail("Model.Score class not found");
        } catch (NoSuchMethodException e) {
            fail("Constructor or methods missing in Score: " + e.getMessage());
        } catch (Exception e) {
            fail("Score test failed: " + e.getCause());
        }
    }

    // Helper methods
    private void checkField(Object obj, String fieldName, Object expectedValue, String... altNames) throws Exception {
        Field field = getField(obj.getClass(), fieldName, altNames);
        field.setAccessible(true);
        Object actual = field.get(obj);
        assertEquals(expectedValue, actual, "Field " + field.getName() + " mismatch");
    }

    private Field getField(Class<?> clazz, String name, String... altNames) throws NoSuchFieldException {
        try {
            return clazz.getDeclaredField(name);
        } catch (NoSuchFieldException e) {
            for (String alt : altNames) {
                try {
                    return clazz.getDeclaredField(alt);
                } catch (NoSuchFieldException ex) {
                    // continue
                }
            }
            throw e;
        }
    }
}
