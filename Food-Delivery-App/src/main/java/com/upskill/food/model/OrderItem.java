package com.upskill.food.model;

import java.math.BigDecimal;

public class OrderItem {
    private int id;
    private int orderId;
    private int foodItemId;
    private String foodName;
    private int quantity;
    private BigDecimal price;

    public OrderItem() {}

    public OrderItem(int foodItemId, String foodName, int quantity, BigDecimal price) {
        this.foodItemId = foodItemId;
        this.foodName = foodName;
        this.quantity = quantity;
        this.price = price;
    }

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public int getOrderId() { return orderId; }
    public void setOrderId(int orderId) { this.orderId = orderId; }

    public int getFoodItemId() { return foodItemId; }
    public void setFoodItemId(int foodItemId) { this.foodItemId = foodItemId; }

    public String getFoodName() { return foodName; }
    public void setFoodName(String foodName) { this.foodName = foodName; }

    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }

    public BigDecimal getPrice() { return price; }
    public void setPrice(BigDecimal price) { this.price = price; }

    public BigDecimal getSubtotal() { return price.multiply(BigDecimal.valueOf(quantity)); }
}
