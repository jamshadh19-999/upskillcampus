package com.upskill.food.dao;

import com.upskill.food.model.FoodItem;
import com.upskill.food.util.DBUtil;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class FoodItemDAO {

    public int createFoodItem(FoodItem item) throws SQLException {
        String sql = "INSERT INTO food_items (restaurant_id, name, description, price, available, image_url) VALUES (?, ?, ?, ?, ?, ?)";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            ps.setInt(1, item.getRestaurantId());
            ps.setString(2, item.getName());
            ps.setString(3, item.getDescription());
            ps.setBigDecimal(4, item.getPrice());
            ps.setBoolean(5, item.isAvailable());
            ps.setString(6, item.getImageUrl());
            ps.executeUpdate();
            try (ResultSet rs = ps.getGeneratedKeys()) {
                if (rs.next()) return rs.getInt(1);
            }
        }
        return -1;
    }

    public void updateFoodItem(FoodItem item) throws SQLException {
        String sql = "UPDATE food_items SET name=?, description=?, price=?, available=? WHERE id=?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, item.getName());
            ps.setString(2, item.getDescription());
            ps.setBigDecimal(3, item.getPrice());
            ps.setBoolean(4, item.isAvailable());
            ps.setInt(5, item.getId());
            ps.executeUpdate();
        }
    }

    public void deleteFoodItem(int id) throws SQLException {
        String sql = "DELETE FROM food_items WHERE id=?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, id);
            ps.executeUpdate();
        }
    }

    public List<FoodItem> getByRestaurant(int restaurantId) throws SQLException {
        List<FoodItem> list = new ArrayList<>();
        String sql = "SELECT * FROM food_items WHERE restaurant_id = ? ORDER BY name";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, restaurantId);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) list.add(mapRow(rs));
            }
        }
        return list;
    }

    public FoodItem getById(int id) throws SQLException {
        String sql = "SELECT * FROM food_items WHERE id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) return mapRow(rs);
            }
        }
        return null;
    }

    private FoodItem mapRow(ResultSet rs) throws SQLException {
        FoodItem item = new FoodItem(
                rs.getInt("id"),
                rs.getInt("restaurant_id"),
                rs.getString("name"),
                rs.getString("description"),
                rs.getBigDecimal("price"),
                rs.getBoolean("available")
        );
        item.setImageUrl(rs.getString("image_url"));
        return item;
    }
}
