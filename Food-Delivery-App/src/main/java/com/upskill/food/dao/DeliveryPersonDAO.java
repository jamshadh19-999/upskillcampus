package com.upskill.food.dao;

import com.upskill.food.model.DeliveryPerson;
import com.upskill.food.util.DBUtil;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class DeliveryPersonDAO {

    public int createDeliveryPerson(DeliveryPerson dp) throws SQLException {
        String sql = "INSERT INTO delivery_persons (user_id, name, phone, status) VALUES (?, ?, ?, ?)";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            ps.setInt(1, dp.getUserId());
            ps.setString(2, dp.getName());
            ps.setString(3, dp.getPhone());
            ps.setString(4, dp.getStatus());
            ps.executeUpdate();
            try (ResultSet rs = ps.getGeneratedKeys()) {
                if (rs.next()) return rs.getInt(1);
            }
        }
        return -1;
    }

    public List<DeliveryPerson> getAvailable() throws SQLException {
        List<DeliveryPerson> list = new ArrayList<>();
        String sql = "SELECT * FROM delivery_persons WHERE status = 'AVAILABLE' ORDER BY name";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) list.add(mapRow(rs));
        }
        return list;
    }

    public DeliveryPerson getByUserId(int userId) throws SQLException {
        String sql = "SELECT * FROM delivery_persons WHERE user_id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, userId);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) return mapRow(rs);
            }
        }
        return null;
    }

    public DeliveryPerson getById(int id) throws SQLException {
        String sql = "SELECT * FROM delivery_persons WHERE id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) return mapRow(rs);
            }
        }
        return null;
    }

    public void updateStatus(int id, String status) throws SQLException {
        String sql = "UPDATE delivery_persons SET status = ? WHERE id = ?";
        try (Connection conn = DBUtil.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, status);
            ps.setInt(2, id);
            ps.executeUpdate();
        }
    }

    private DeliveryPerson mapRow(ResultSet rs) throws SQLException {
        return new DeliveryPerson(
                rs.getInt("id"),
                rs.getInt("user_id"),
                rs.getString("name"),
                rs.getString("phone"),
                rs.getString("status")
        );
    }
}
