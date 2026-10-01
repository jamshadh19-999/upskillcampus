package com.upskill.food.model;

public class DeliveryPerson {
    private int id;
    private int userId;
    private String name;
    private String phone;
    private String status; // AVAILABLE, BUSY

    public DeliveryPerson() {}

    public DeliveryPerson(int id, int userId, String name, String phone, String status) {
        this.id = id;
        this.userId = userId;
        this.name = name;
        this.phone = phone;
        this.status = status;
    }

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public int getUserId() { return userId; }
    public void setUserId(int userId) { this.userId = userId; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
