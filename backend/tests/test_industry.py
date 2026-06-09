#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智质通·咨询版 - 行业配置API测试
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import init_db

client = TestClient(app)


class TestIndustry:
    """行业配置API测试"""

    @pytest.fixture(autouse=True)
    def setup_db(self):
        """每个测试前初始化数据库"""
        init_db()

    def test_list_industries(self):
        """测试获取行业列表"""
        response = client.get("/api/v1/industry/list")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_industry_detail(self):
        """测试获取行业详情"""
        response = client.get("/api/v1/industry/property_management")
        assert response.status_code == 200
        data = response.json()
        assert "industry_code" in data
        assert "industry_name" in data
        assert "special_files" in data

    def test_get_industry_features(self):
        """测试获取行业特征"""
        response = client.get("/api/v1/industry/property_management/check-features")
        assert response.status_code == 200
        data = response.json()
        assert "industry_code" in data
        assert "emergency_plans" in data
        assert isinstance(data["emergency_plans"], list)

    def test_get_emergency_plans(self):
        """测试获取行业应急预案"""
        response = client.get("/api/v1/industry/property_management/emergency-plans")
        assert response.status_code == 200
        data = response.json()
        assert "emergency_plans" in data
        assert isinstance(data["emergency_plans"], list)

    def test_get_nonexistent_industry(self):
        """测试获取不存在的行业"""
        response = client.get("/api/v1/industry/nonexistent")
        assert response.status_code == 404
