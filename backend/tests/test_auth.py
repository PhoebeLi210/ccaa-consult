#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 认证API测试
"""

import pytest
from fastapi.testclient import TestClient

# 需要在测试环境初始化数据库
from app.main import app
from app.core.database import init_db

client = TestClient(app)


class TestAuth:
    """认证API测试"""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """每个测试前初始化数据库"""
        init_db()

    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_register(self):
        """测试用户注册"""
        response = client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "password": "testpass123",
            "email": "test@example.com",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    def test_register_duplicate_username(self):
        """测试重复用户名注册"""
        # 先注册一个用户
        client.post("/api/v1/auth/register", json={
            "username": "duptest",
            "password": "testpass123",
        })
        # 再注册同名用户
        response = client.post("/api/v1/auth/register", json={
            "username": "duptest",
            "password": "testpass123",
        })
        assert response.status_code == 400
        assert "已被注册" in response.json()["detail"]

    def test_login(self):
        """测试用户登录"""
        # 先注册
        client.post("/api/v1/auth/register", json={
            "username": "logintest",
            "password": "testpass123",
        })
        # 再登录
        response = client.post("/api/v1/auth/login", data={
            "username": "logintest",
            "password": "testpass123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        """测试错误密码登录"""
        # 先注册
        client.post("/api/v1/auth/register", json={
            "username": "wrongpasstest",
            "password": "testpass123",
        })
        # 用错误密码登录
        response = client.post("/api/v1/auth/login", data={
            "username": "wrongpasstest",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_get_me_without_token(self):
        """测试未登录获取用户信息"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_get_me_with_token(self):
        """测试登录后获取用户信息"""
        # 注册并登录
        client.post("/api/v1/auth/register", json={
            "username": "metest",
            "password": "testpass123",
        })
        login_resp = client.post("/api/v1/auth/login", data={
            "username": "metest",
            "password": "testpass123",
        })
        token = login_resp.json()["access_token"]

        # 获取用户信息
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "metest"
