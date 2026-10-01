package com.upskill.food.dao;

import com.upskill.food.model.Restaurant;
import com.upskill.food.util.DBUtil;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class RestaurantDAO {

    public int createRestaurant(Restaurant r) throws SQLException {
        String sql = "INSERT INTO restaurants (owner_id, name, cuisine, address, description) VALUES (?, ?, ?, ?, ?)";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            ps.setInt(1, r.getOwnerId());
            ps.setString(2, r.getName());
            ps.setString(3, r.getCuisine());
            ps.setString(4, r.getAddress());
            ps.setString(5, r.getDescription());
            ps.executeUpdate();
            try (ResultSet rs = ps.getGeneratedKeys()) {
                if (rs.next()) return rs.getInt(1);
            }
        }
        return -1;
    }

    public List<Restaurant> getAllRestaurants() throws SQLException {
        List<Restaurant> list = new ArrayList<>();
        String sql = "SELECT * FROM restaurants ORDER BY name";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) list.add(mapRow(rs));
        }
        return list;
    }

    public Restaurant getById(int id) throws SQLException {
        String sql = "SELECT * FROM restaurants WHERE id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) return mapRow(rs);
            }
        }
        return null;
    }

    public Restaurant getByOwnerId(int ownerId) throws SQLException {
        String sql = "SELECT * FROM restaurants WHERE owner_id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, ownerId);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) return mapRow(rs);
            }
        }
        return null;
    }

    private Restaurant mapRow(ResultSet rs) throws SQLException {
        return new Restaurant(
                rs.getInt("id"),
                rs.getInt("owner_id"),
                rs.getString("name"),
                rs.getString("cuisine"),
                rs.getString("address"),
                rs.getString("description")
        );
    }
}
