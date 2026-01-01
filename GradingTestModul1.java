import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;

public class GradingTestModul1 {

    @Test
    @DisplayName("1. Test VehicleType Enum")
    void testVehicleTypeEnum() {
        try {
            Class<?> enumClass = Class.forName("VehicleType");
            assertTrue(enumClass.isEnum(), "VehicleType should be an enum");
            
            Object[] constants = enumClass.getEnumConstants();
            assertNotNull(constants, "Enum constants should not be null");
            
            boolean hasCar = false, hasMotorcycle = false, hasTruck = false;
            for (Object c : constants) {
                String name = c.toString();
                if (name.equalsIgnoreCase("Car")) hasCar = true;
                if (name.equalsIgnoreCase("Motorcycle")) hasMotorcycle = true;
                if (name.equalsIgnoreCase("Truck")) hasTruck = true;
            }
            
            assertTrue(hasCar, "Enum should contain 'Car'");
            assertTrue(hasMotorcycle, "Enum should contain 'Motorcycle'");
            assertTrue(hasTruck, "Enum should contain 'Truck'");
            
        } catch (ClassNotFoundException e) {
            fail("VehicleType enum not found");
        }
    }

    @Test
    @DisplayName("2. Test Vehicle Class Structure & Constructor")
    void testVehicleClass() {
        try {
            Class<?> vehicleClass = Class.forName("Vehicle");
            Class<?> enumClass = Class.forName("VehicleType");
            
            // Check fields existence (ignoring access modifiers for now, though UML implies package-private or private)
            assertFieldExists(vehicleClass, "brand");
            assertFieldExists(vehicleClass, "year");
            assertFieldExists(vehicleClass, "type");
            assertFieldExists(vehicleClass, "price");
            
            // Check Constructor
            // Vehicle(String, int, VehicleType, float)
            Constructor<?> constructor = null;
            try {
                constructor = vehicleClass.getConstructor(String.class, int.class, enumClass, float.class);
            } catch (NoSuchMethodException e) {
                // Try double for price just in case
                try {
                    constructor = vehicleClass.getConstructor(String.class, int.class, enumClass, double.class);
                } catch (NoSuchMethodException ex) {
                    fail("Vehicle constructor not found. Expected: (String, int, VehicleType, float)");
                }
            }
            
            assertNotNull(constructor, "Vehicle constructor missing");
            
            // Instantiate
            Object enumVal = enumClass.getEnumConstants()[0];
            Object vehicle = constructor.newInstance("Honda", 2020, enumVal, 1000.0f);
            assertNotNull(vehicle);
            
        } catch (ClassNotFoundException e) {
            fail("Vehicle class not found");
        } catch (Exception e) {
            fail("Vehicle test failed: " + e.getMessage());
        }
    }

    @Test
    @DisplayName("3. Test Customer Class & Logic")
    void testCustomerClass() {
        Class<?> customerClass = null;
        try {
            customerClass = Class.forName("Customer");
        } catch (ClassNotFoundException e) {
            try {
                customerClass = Class.forName("Costumer"); // Handle typo in UML
            } catch (ClassNotFoundException ex) {
                fail("Customer (or Costumer) class not found");
            }
        }

        try {
            Class<?> vehicleClass = Class.forName("Vehicle");
            Class<?> enumClass = Class.forName("VehicleType");
            
            // Check fields
            assertFieldExists(customerClass, "name");
            assertFieldExists(customerClass, "vehicle");
            
            // Constructor: Customer(String, Vehicle)
            Constructor<?> constructor = customerClass.getConstructor(String.class, vehicleClass);
            
            // Create Vehicle
            Object enumVal = enumClass.getEnumConstants()[0];
            Constructor<?> vConst = null;
            try {
                vConst = vehicleClass.getConstructor(String.class, int.class, enumClass, float.class);
            } catch(NoSuchMethodException e) {
                vConst = vehicleClass.getConstructor(String.class, int.class, enumClass, double.class);
            }
            
            Object vehicle = vConst.newInstance("Honda", 2020, enumVal, 5000.0f);
            
            // Create Customer
            Object customer = constructor.newInstance("Budi", vehicle);
            
            // Test getTotalPrice
            Method getTotalPrice = customerClass.getMethod("getTotalPrice");
            Object price = getTotalPrice.invoke(customer);
            
            // Return type is double in UML
            assertTrue(price instanceof Double || price instanceof Float, "getTotalPrice should return double or float");
            assertEquals(5000.0, ((Number)price).doubleValue(), 0.01, "getTotalPrice logic incorrect");
            
        } catch (Exception e) {
            fail("Customer test failed: " + e.getMessage());
        }
    }
    
    private void assertFieldExists(Class<?> clazz, String fieldName) {
        try {
            clazz.getDeclaredField(fieldName);
        } catch (NoSuchFieldException e) {
            fail("Field '" + fieldName + "' missing in " + clazz.getSimpleName());
        }
    }
}
