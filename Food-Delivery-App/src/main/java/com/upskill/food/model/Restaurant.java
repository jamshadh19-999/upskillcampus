package com.upskill.food.model;

public class Restaurant {
    private int id;
    private int ownerId;
    private String name;
    private String cuisine;
    private String address;
    private String description;

    public Restaurant() {}

    public Restaurant(int id, int ownerId, String name, String cuisine, String address, String description) {
        this.id = id;
        this.ownerId = ownerId;
        this.name = name;
        this.cuisine = cuisine;
        this.address = address;
        this.description = description;
    }

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public int getOwnerId() { return ownerId; }
    public void setOwnerId(int ownerId) { this.ownerId = ownerId; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getCuisine() { return cuisine; }
    public void setCuisine(String cuisine) { this.cuisine = cuisine; }

    public String getAddress() { return address; }
    public void setAddress(String address) { this.address = address; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
}
