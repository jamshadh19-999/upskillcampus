package com.upskill.food.listener;

import com.upskill.food.util.DBUtil;

import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;
import javax.servlet.annotation.WebListener;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.sql.Connection;
import java.sql.Statement;

@WebListener
public class AppInitListener implements ServletContextListener {

    @Override
    public void contextInitialized(ServletContextEvent sce) {
        try (Connection conn = DBUtil.getConnection();
             Statement stmt = conn.createStatement()) {

            InputStream is = getClass().getClassLoader().getResourceAsStream("schema.sql");
            if (is == null) {
                throw new RuntimeException("schema.sql not found on classpath");
            }

            StringBuilder sql = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(is))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    sql.append(line).append("\n");
                }
            }

            // H2 supports running multiple ; separated statements one at a time
            for (String statement : sql.toString().split(";")) {
                if (!statement.trim().isEmpty()) {
                    stmt.execute(statement);
                }
            }

            System.out.println("[AppInitListener] Database schema ready.");
        } catch (Exception e) {
            throw new RuntimeException("Failed to initialize database schema", e);
        }
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
        // no-op
    }
}
