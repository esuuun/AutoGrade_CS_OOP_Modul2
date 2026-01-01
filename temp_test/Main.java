import java.util.Scanner;

public class Main {

    enum VehicleType {
        CAR,
        MOTORCYCLE,
        TRUCK
    }


    static class Vehicle {
        private String brand;
        private int year;
        private VehicleType type;
        private double price;

        public Vehicle(String brand, int year, VehicleType type, double price) {
            this.brand = brand;
            this.year = year;
            this.type = type;
            this.price = price;
        }

        public String getBrand() {
            return brand;
        }

        public int getYear() {
            return year;
        }

        public VehicleType getType() {
            return type;
        }

        public double getPrice() {
            return price;
        }

        public void showDetails() {
            System.out.println("Brand: " + brand);
            System.out.println("Year: " + year);
            System.out.println("Type: " + type);
            System.out.println("Price: $" + price);
        }
    }


    static class Customer {
        private String name;
        private Vehicle vehicle;

        public Customer(String name, Vehicle vehicle) {
            this.name = name;
            this.vehicle = vehicle;
        }

        public double getTotalPrice() {
            return vehicle.getPrice();
        }

        public void showDetails() {
            System.out.println("Customer Name: " + name);
            vehicle.showDetails();
            System.out.println("Total Price: $" + getTotalPrice());
            System.out.println();
        }
    }


    public static void main(String[] args) {

        Vehicle vehicleSupraBapak = new Vehicle("Honda Supra", 1998, VehicleType.MOTORCYCLE, 3000.0);
        Vehicle vehicleKalcer = new Vehicle("VW Beetle", 1998, VehicleType.CAR, 200000.0);
        Vehicle vehicleGuede = new Vehicle("Isuzu Giga", 2011, VehicleType.TRUCK, 300000.0);


        Scanner scanner = new Scanner(System.in);


        System.out.println("Enter customer names:");
        System.out.print("Enter customer 1 name: ");
        String name1 = scanner.nextLine();
        System.out.print("Enter customer 2 name: ");
        String name2 = scanner.nextLine();
        System.out.print("Enter customer 3 name: ");
        String name3 = scanner.nextLine();


        Customer customer1 = new Customer(name1, vehicleSupraBapak);
        Customer customer2 = new Customer(name2, vehicleKalcer);
        Customer customer3 = new Customer(name3, vehicleGuede);


        System.out.println("\n====== Customer Service ======");
        System.out.println("Customer 1:");
        customer1.showDetails();
        System.out.println("Customer 2:");
        customer2.showDetails();
        System.out.println("Customer 3:");
        customer3.showDetails();

        scanner.close();
    }
}
