# -*- coding: utf-8 -*-
"""
认证范围39大类数据接口

数据来源: 管理体系认证业务范围分类手册（2016）
包含39个大类、143个中类、325个小类
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List

router = APIRouter(prefix="/certification-scope", tags=["认证范围"])


# ============ 响应模型 ============

class CategoryBrief(BaseModel):
    """大类简要信息"""
    code: str = Field(..., description="大类代码")
    name_cn: str = Field(..., description="大类中文名称")
    name_en: str = Field(..., description="大类英文名称")
    sub_category_count: int = Field(..., description="中类数量")


class MinorCategory(BaseModel):
    """小类信息"""
    code: str = Field(..., description="小类代码")
    name_cn: str = Field(..., description="小类中文名称")
    name_en: str = Field(..., description="小类英文名称")


class SubCategoryDetail(BaseModel):
    """中类详情"""
    code: str = Field(..., description="中类代码")
    name_cn: str = Field(..., description="中类中文名称")
    name_en: str = Field(..., description="中类英文名称")
    minor_categories: List[MinorCategory] = Field(..., description="小类列表")


class CategoryDetail(BaseModel):
    """大类详情"""
    code: str = Field(..., description="大类代码")
    name_cn: str = Field(..., description="大类中文名称")
    name_en: str = Field(..., description="大类英文名称")
    sub_categories: List[SubCategoryDetail] = Field(..., description="中类列表")


class SubCategoryBrief(BaseModel):
    """中类简要信息"""
    code: str = Field(..., description="中类代码")
    name_cn: str = Field(..., description="中类中文名称")
    name_en: str = Field(..., description="中类英文名称")
    minor_category_count: int = Field(..., description="小类数量")


class SearchResult(BaseModel):
    """搜索结果"""
    level: str = Field(..., description="层级: category/sub_category/minor")
    code: str = Field(..., description="代码")
    name_cn: str = Field(..., description="中文名称")
    name_en: str = Field(..., description="英文名称")
    parent_code: Optional[str] = Field(None, description="父级代码")


class IndustryMatchResult(BaseModel):
    """行业匹配结果"""
    industry_code: str = Field(..., description="行业代码")
    matched_categories: List[CategoryBrief] = Field(..., description="匹配的大类列表")


# ============ 认证范围数据 ============

CERTIFICATION_SCOPE_DATA = {
    "categories": [
        {
            "code": "01",
            "name_cn": "农业、林业和渔业",
            "name_en": "Agriculture, forestry and fishing",
            "sub_categories": [
                {
                    "code": "01.01",
                    "name_cn": "非多年生作物的种植",
                    "name_en": "Growing of non-perennial crops",
                    "minor_categories": [
                        {
                            "code": "01.01.01",
                            "name_cn": "谷物（稻米除外），豆科作物和油籽作物的种植",
                            "name_en": "Growing of cereals (except rice), leguminous crops and oil seeds"
                        },
                        {
                            "code": "01.01.02",
                            "name_cn": "稻米的种植",
                            "name_en": "Growing of rice"
                        },
                        {
                            "code": "01.01.03",
                            "name_cn": "蔬菜和瓜类、块根和块茎类作物的种植",
                            "name_en": "Growing of vegetables and melons, roots and tubers"
                        },
                        {
                            "code": "01.01.04",
                            "name_cn": "甘蔗的种植",
                            "name_en": "Growing of sugar cane"
                        },
                        {
                            "code": "01.01.05",
                            "name_cn": "烟草的种植",
                            "name_en": "Growing of tobacco"
                        },
                        {
                            "code": "01.01.06",
                            "name_cn": "纤维作物的种植",
                            "name_en": "Growing of fibre crops"
                        },
                        {
                            "code": "01.01.07",
                            "name_cn": "其他非多年生作物的种植",
                            "name_en": "Growing of other non-perennial crops"
                        }
                    ]
                },
                {
                    "code": "01.02",
                    "name_cn": "多年生作物的种植",
                    "name_en": "Growing of perennial crops",
                    "minor_categories": [
                        {
                            "code": "01.02.01",
                            "name_cn": "葡萄的种植",
                            "name_en": "Growing of grapes"
                        },
                        {
                            "code": "01.02.02",
                            "name_cn": "热带和亚热带水果的种植",
                            "name_en": "Growing of tropical and subtropical fruits"
                        },
                        {
                            "code": "01.02.03",
                            "name_cn": "柑橘类水果的种植",
                            "name_en": "Growing of citrus fruits"
                        },
                        {
                            "code": "01.02.04",
                            "name_cn": "仁果和核果的种植",
                            "name_en": "Growing of pome fruits and stone fruits"
                        },
                        {
                            "code": "01.02.05",
                            "name_cn": "其他乔木和灌木水果及坚果的种植",
                            "name_en": "Growing of other tree and bush fruits and nuts"
                        },
                        {
                            "code": "01.02.06",
                            "name_cn": "油质果实的种植",
                            "name_en": "Growing of oleaginous fruits"
                        },
                        {
                            "code": "01.02.07",
                            "name_cn": "饮料作物的种植",
                            "name_en": "Growing of beverage crops"
                        },
                        {
                            "code": "01.02.08",
                            "name_cn": "香料、芳香植物、药材和制药作物的种植",
                            "name_en": "Growing of spices, aromatic, drug and pharmaceutical crops"
                        },
                        {
                            "code": "01.02.09",
                            "name_cn": "其他多年生作物的种植",
                            "name_en": "Growing of other perennial crops"
                        }
                    ]
                },
                {
                    "code": "01.03",
                    "name_cn": "植物繁殖",
                    "name_en": "Plant propagation",
                    "minor_categories": [
                        {
                            "code": "01.03.00",
                            "name_cn": "植物繁殖",
                            "name_en": "Plant propagation"
                        }
                    ]
                },
                {
                    "code": "01.04",
                    "name_cn": "畜牧生产",
                    "name_en": "Animal production",
                    "minor_categories": [
                        {
                            "code": "01.04.01",
                            "name_cn": "奶牛的饲养",
                            "name_en": "Raising of dairy cattle"
                        },
                        {
                            "code": "01.04.02",
                            "name_cn": "其他牛类和水牛的饲养",
                            "name_en": "Raising of other cattle and buffaloes"
                        },
                        {
                            "code": "01.04.03",
                            "name_cn": "马和其他马科动物的饲养",
                            "name_en": "Raising of horses and other equines"
                        },
                        {
                            "code": "01.04.04",
                            "name_cn": "骆驼和骆驼科动物的饲养",
                            "name_en": "Raising of camels and camelids"
                        },
                        {
                            "code": "01.04.05",
                            "name_cn": "绵羊和山羊的饲养",
                            "name_en": "Raising of sheep and goats"
                        },
                        {
                            "code": "01.04.06",
                            "name_cn": "猪的饲养",
                            "name_en": "Raising of swine/pigs"
                        },
                        {
                            "code": "01.04.07",
                            "name_cn": "家禽的饲养",
                            "name_en": "Raising of poultry"
                        },
                        {
                            "code": "01.04.08",
                            "name_cn": "其他动物的饲养",
                            "name_en": "Raising of other animals"
                        }
                    ]
                },
                {
                    "code": "01.05",
                    "name_cn": "混合农业",
                    "name_en": "Mixed farming",
                    "minor_categories": [
                        {
                            "code": "01.05.00",
                            "name_cn": "混合农业",
                            "name_en": "Mixed farming"
                        }
                    ]
                },
                {
                    "code": "01.06",
                    "name_cn": "农业支持活动和作物收获后的活动",
                    "name_en": "Support activities to agriculture and post-harvest crop activities",
                    "minor_categories": [
                        {
                            "code": "01.06.01",
                            "name_cn": "作物生产的支持活动",
                            "name_en": "Support activities for crop production"
                        },
                        {
                            "code": "01.06.02",
                            "name_cn": "畜牧业的支持活动",
                            "name_en": "Support activities for animal production"
                        },
                        {
                            "code": "01.06.03",
                            "name_cn": "作物收获后的活动",
                            "name_en": "Post-harvest crop activities"
                        },
                        {
                            "code": "01.06.04",
                            "name_cn": "繁育用种子的加工",
                            "name_en": "Seed processing for propagation"
                        }
                    ]
                },
                {
                    "code": "01.07",
                    "name_cn": "狩猎、捕捉及相关服务活动",
                    "name_en": "Hunting, trapping and related service activities",
                    "minor_categories": [
                        {
                            "code": "01.07.00",
                            "name_cn": "狩猎、捕捉及相关服务活动",
                            "name_en": "Hunting, trapping and related service activities"
                        }
                    ]
                },
                {
                    "code": "01.08",
                    "name_cn": "造林和其他林业活动",
                    "name_en": "Silviculture and other forestry activities",
                    "minor_categories": [
                        {
                            "code": "01.08.00",
                            "name_cn": "造林和其他林业活动",
                            "name_en": "Silviculture and other forestry activities"
                        }
                    ]
                },
                {
                    "code": "01.09",
                    "name_cn": "伐木",
                    "name_en": "Logging",
                    "minor_categories": [
                        {
                            "code": "01.09.00",
                            "name_cn": "伐木",
                            "name_en": "Logging"
                        }
                    ]
                },
                {
                    "code": "01.10",
                    "name_cn": "野生非木材产品的采集",
                    "name_en": "Gathering of wild growing non-wood products",
                    "minor_categories": [
                        {
                            "code": "01.10.00",
                            "name_cn": "野生非木材产品的采集",
                            "name_en": "Gathering of wild growing non-wood products"
                        }
                    ]
                },
                {
                    "code": "01.11",
                    "name_cn": "林业支持服务",
                    "name_en": "Support services to forestry",
                    "minor_categories": [
                        {
                            "code": "01.11.00",
                            "name_cn": "林业支持服务",
                            "name_en": "Support services to forestry"
                        }
                    ]
                },
                {
                    "code": "01.12",
                    "name_cn": "渔业",
                    "name_en": "Fishing",
                    "minor_categories": [
                        {
                            "code": "01.12.01",
                            "name_cn": "海洋渔业",
                            "name_en": "Marine fishing"
                        },
                        {
                            "code": "01.12.02",
                            "name_cn": "淡水渔业",
                            "name_en": "Freshwater fishing"
                        }
                    ]
                },
                {
                    "code": "01.13",
                    "name_cn": "水产业",
                    "name_en": "Aquaculture",
                    "minor_categories": [
                        {
                            "code": "01.13.01",
                            "name_cn": "海水养殖",
                            "name_en": "Marine aquaculture"
                        },
                        {
                            "code": "01.13.02",
                            "name_cn": "淡水养殖",
                            "name_en": "Freshwater aquaculture"
                        }
                    ]
                }
            ]
        },
        {
            "code": "02",
            "name_cn": "采矿业和采石业",
            "name_en": "Mining and quarrying",
            "sub_categories": [
                {
                    "code": "02.01",
                    "name_cn": "硬煤的开采",
                    "name_en": "Mining of hard coal",
                    "minor_categories": [
                        {
                            "code": "02.01.00",
                            "name_cn": "硬煤的开采",
                            "name_en": "Mining of hard coal"
                        }
                    ]
                },
                {
                    "code": "02.02",
                    "name_cn": "褐煤的开采",
                    "name_en": "Mining of lignite",
                    "minor_categories": [
                        {
                            "code": "02.02.00",
                            "name_cn": "褐煤的开采",
                            "name_en": "Mining of lignite"
                        }
                    ]
                },
                {
                    "code": "02.03",
                    "name_cn": "原油的开采",
                    "name_en": "Extraction of crude petroleum",
                    "minor_categories": [
                        {
                            "code": "02.03.00",
                            "name_cn": "原油的开采",
                            "name_en": "Extraction of crude petroleum"
                        }
                    ]
                },
                {
                    "code": "02.04",
                    "name_cn": "天然气的开采",
                    "name_en": "Extraction of natural gas",
                    "minor_categories": [
                        {
                            "code": "02.04.00",
                            "name_cn": "天然气的开采",
                            "name_en": "Extraction of natural gas"
                        }
                    ]
                },
                {
                    "code": "02.05",
                    "name_cn": "铁矿石的开采",
                    "name_en": "Mining of iron ores",
                    "minor_categories": [
                        {
                            "code": "02.05.00",
                            "name_cn": "铁矿石的开采",
                            "name_en": "Mining of iron ores"
                        }
                    ]
                },
                {
                    "code": "02.06",
                    "name_cn": "非铁金属矿石的开采",
                    "name_en": "Mining of non-ferrous metal ores",
                    "minor_categories": [
                        {
                            "code": "02.06.01",
                            "name_cn": "铀和钍矿石的开采",
                            "name_en": "Mining of uranium and thorium ores"
                        },
                        {
                            "code": "02.06.02",
                            "name_cn": "其他非铁金属矿石的开采",
                            "name_en": "Mining of other non-ferrous metal ores"
                        }
                    ]
                },
                {
                    "code": "02.07",
                    "name_cn": "石料、沙子和粘土的采掘",
                    "name_en": "Quarrying of stone, sand and clay",
                    "minor_categories": [
                        {
                            "code": "02.07.01",
                            "name_cn": "装饰和建筑用石料、石灰石、石膏、白垩和板岩的开采",
                            "name_en": "Quarrying of ornamental and building stone, limestone, gypsum, chalk and slate"
                        },
                        {
                            "code": "02.07.02",
                            "name_cn": "砾石和砂坑的采挖，粘土和高岭土的开采",
                            "name_en": "Operation of gravel and sand pits; mining of clays and kaolin"
                        }
                    ]
                },
                {
                    "code": "02.08",
                    "name_cn": "未另分类采矿及采石业",
                    "name_en": "Mining and quarrying n.e.c.",
                    "minor_categories": [
                        {
                            "code": "02.08.01",
                            "name_cn": "化学和肥料矿物的开采",
                            "name_en": "Mining of chemical and fertiliser minerals"
                        },
                        {
                            "code": "02.08.02",
                            "name_cn": "泥煤的开采",
                            "name_en": "Extraction of peat"
                        },
                        {
                            "code": "02.08.03",
                            "name_cn": "采盐",
                            "name_en": "Extraction of salt"
                        },
                        {
                            "code": "02.08.04",
                            "name_cn": "其他未另分类的采矿及采石业",
                            "name_en": "Other mining and quarrying n.e.c."
                        }
                    ]
                },
                {
                    "code": "02.09",
                    "name_cn": "对石油和天然气开采的支持活动",
                    "name_en": "Support activities for petroleum and natural gas extraction",
                    "minor_categories": [
                        {
                            "code": "02.09.00",
                            "name_cn": "对石油和天然气开采的支持活动",
                            "name_en": "Support activities for petroleum and natural gas extraction"
                        }
                    ]
                },
                {
                    "code": "02.10",
                    "name_cn": "其他采矿及采石的支持活动",
                    "name_en": "Support activities for other mining and quarrying",
                    "minor_categories": [
                        {
                            "code": "02.10.00",
                            "name_cn": "其他采矿及采石的支持活动",
                            "name_en": "Support activities for other mining and quarrying"
                        }
                    ]
                }
            ]
        },
        {
            "code": "03",
            "name_cn": "食品、饮料和烟草",
            "name_en": "Food products, beverages and tobacco",
            "sub_categories": [
                {
                    "code": "03.01",
                    "name_cn": "肉类的加工与保存以及肉制品的生产",
                    "name_en": "Processing and preserving of meat and production of meat products",
                    "minor_categories": [
                        {
                            "code": "03.01.01",
                            "name_cn": "肉类的加工与保存",
                            "name_en": "Processing and preserving of meat"
                        },
                        {
                            "code": "03.01.02",
                            "name_cn": "禽肉的加工与保存",
                            "name_en": "Processing and preserving of poultry meat"
                        },
                        {
                            "code": "03.01.03",
                            "name_cn": "肉制品和禽肉制品的生产",
                            "name_en": "Production of meat and poultry meat products"
                        }
                    ]
                },
                {
                    "code": "03.02",
                    "name_cn": "鱼类、甲壳类和软体动物的加工及保存",
                    "name_en": "Processing and preserving of fish, crustaceans and molluscs",
                    "minor_categories": [
                        {
                            "code": "03.02.00",
                            "name_cn": "鱼类、甲壳类和软体动物的加工及保存",
                            "name_en": "Processing and preserving of fish, crustaceans and molluscs"
                        }
                    ]
                },
                {
                    "code": "03.03",
                    "name_cn": "水果和蔬菜的加工及保存",
                    "name_en": "Processing and preserving of fruit and vegetables",
                    "minor_categories": [
                        {
                            "code": "03.03.01",
                            "name_cn": "马铃薯的加工及保存",
                            "name_en": "Processing and preserving of potatoes"
                        },
                        {
                            "code": "03.03.02",
                            "name_cn": "水果汁和蔬菜汁的制造",
                            "name_en": "Manufacture of fruit and vegetable juice"
                        },
                        {
                            "code": "03.03.03",
                            "name_cn": "其他水果和蔬菜的加工及保存",
                            "name_en": "Other processing and preserving of fruit and vegetables"
                        }
                    ]
                },
                {
                    "code": "03.04",
                    "name_cn": "植物油、动物油和油脂的制造",
                    "name_en": "Manufacture of vegetable and animal oils and fats",
                    "minor_categories": [
                        {
                            "code": "03.04.01",
                            "name_cn": "油和油脂的制造",
                            "name_en": "Manufacture of oils and fats"
                        },
                        {
                            "code": "03.04.02",
                            "name_cn": "人造黄油及类似食用油脂的制造",
                            "name_en": "Manufacture of margarine and similar edible fats"
                        }
                    ]
                },
                {
                    "code": "03.05",
                    "name_cn": "乳制品的制造",
                    "name_en": "Manufacture of dairy products",
                    "minor_categories": [
                        {
                            "code": "03.05.01",
                            "name_cn": "乳制品厂的运营和奶酪的制造",
                            "name_en": "Operation of dairies and cheese making"
                        },
                        {
                            "code": "03.05.02",
                            "name_cn": "冰淇淋的制造",
                            "name_en": "Manufacture of ice cream"
                        }
                    ]
                },
                {
                    "code": "03.06",
                    "name_cn": "谷物磨粉制品、淀粉及淀粉制品的制造",
                    "name_en": "Manufacture of grain mill products, starches and starch products",
                    "minor_categories": [
                        {
                            "code": "03.06.01",
                            "name_cn": "谷物磨粉制品的制造",
                            "name_en": "Manufacture of grain mill products"
                        },
                        {
                            "code": "03.06.02",
                            "name_cn": "淀粉及淀粉制品的制造",
                            "name_en": "Manufacture of starches and starch products"
                        }
                    ]
                },
                {
                    "code": "03.07",
                    "name_cn": "烘焙食品和谷粉制品的制作",
                    "name_en": "Manufacture of bakery and farinaceous products",
                    "minor_categories": [
                        {
                            "code": "03.07.01",
                            "name_cn": "面包、新鲜糕点和蛋糕的制作",
                            "name_en": "Manufacture of bread; manufacture of fresh pastry goods and cakes"
                        },
                        {
                            "code": "03.07.02",
                            "name_cn": "面包干和饼干的制作，可保存的糕点和蛋糕的制作",
                            "name_en": "Manufacture of rusks and biscuits; manufacture of preserved pastry goods and cakes"
                        },
                        {
                            "code": "03.07.03",
                            "name_cn": "通心粉、面条、蒸粗麦粉和类似谷粉制品的制造",
                            "name_en": "Manufacture of macaroni, noodles, couscous and similar farinaceous products"
                        }
                    ]
                },
                {
                    "code": "03.08",
                    "name_cn": "其他食品的制造",
                    "name_en": "Manufacture of other food products",
                    "minor_categories": [
                        {
                            "code": "03.08.01",
                            "name_cn": "糖的制造",
                            "name_en": "Manufacture of sugar"
                        },
                        {
                            "code": "03.08.02",
                            "name_cn": "可可、巧克力和糖果的制造",
                            "name_en": "Manufacture of cocoa, chocolate and sugar confectionery"
                        },
                        {
                            "code": "03.08.03",
                            "name_cn": "茶叶和咖啡的加工",
                            "name_en": "Processing of tea and coffee"
                        },
                        {
                            "code": "03.08.04",
                            "name_cn": "调味品和调味料的制造",
                            "name_en": "Manufacture of condiments and seasonings"
                        },
                        {
                            "code": "03.08.05",
                            "name_cn": "预制餐食和菜肴的制作",
                            "name_en": "Manufacture of prepared meals and dishes"
                        },
                        {
                            "code": "03.08.06",
                            "name_cn": "均质食物制品和营养食品的制造",
                            "name_en": "Manufacture of homogenised food preparations and dietetic food"
                        },
                        {
                            "code": "03.08.07",
                            "name_cn": "其他未另分类食品的制造",
                            "name_en": "Manufacture of other food products n.e.c."
                        }
                    ]
                },
                {
                    "code": "03.09",
                    "name_cn": "预制动物饲料的制造",
                    "name_en": "Manufacture of prepared animal feeds",
                    "minor_categories": [
                        {
                            "code": "03.09.01",
                            "name_cn": "预制家畜饲料的制造",
                            "name_en": "Manufacture of prepared feeds for farm animals"
                        },
                        {
                            "code": "03.09.02",
                            "name_cn": "预制宠物食品的制造",
                            "name_en": "Manufacture of prepared pet foods"
                        }
                    ]
                },
                {
                    "code": "03.10",
                    "name_cn": "饮料的制造",
                    "name_en": "Manufacture of beverages",
                    "minor_categories": [
                        {
                            "code": "03.10.01",
                            "name_cn": "烈酒的蒸馏、精馏和勾兑",
                            "name_en": "Distilling, rectifying and blending of spirits"
                        },
                        {
                            "code": "03.10.02",
                            "name_cn": "葡萄酒的制造",
                            "name_en": "Manufacture of wine from grape"
                        },
                        {
                            "code": "03.10.03",
                            "name_cn": "苹果酒及其他果酒的制造",
                            "name_en": "Manufacture of cider and other fruit wines"
                        },
                        {
                            "code": "03.10.04",
                            "name_cn": "其他非蒸馏发酵饮料的制造",
                            "name_en": "Manufacture of other non-distilled fermented beverages"
                        },
                        {
                            "code": "03.10.05",
                            "name_cn": "啤酒的制造",
                            "name_en": "Manufacture of beer"
                        },
                        {
                            "code": "03.10.06",
                            "name_cn": "麦芽的制造",
                            "name_en": "Manufacture of malt"
                        },
                        {
                            "code": "03.10.07",
                            "name_cn": "软饮料的制造，矿泉水和其他瓶装水的生产",
                            "name_en": "Manufacture of soft drinks; production of mineral waters and other bottled waters"
                        }
                    ]
                },
                {
                    "code": "03.11",
                    "name_cn": "烟草制品的制造",
                    "name_en": "Manufacture of tobacco products",
                    "minor_categories": [
                        {
                            "code": "03.11.00",
                            "name_cn": "烟草制品的制造",
                            "name_en": "Manufacture of tobacco products"
                        }
                    ]
                }
            ]
        },
        {
            "code": "04",
            "name_cn": "纺织品及纺织制品",
            "name_en": "Textiles and textile products",
            "sub_categories": [
                {
                    "code": "04.01",
                    "name_cn": "纺织用纤维的备制及纺纱",
                    "name_en": "Preparation and spinning of textile fibres",
                    "minor_categories": [
                        {
                            "code": "04.01.00",
                            "name_cn": "纺织用纤维的备制及纺纱",
                            "name_en": "Preparation and spinning of textile fibres"
                        }
                    ]
                },
                {
                    "code": "04.02",
                    "name_cn": "纺织品的织造",
                    "name_en": "Weaving of textiles",
                    "minor_categories": [
                        {
                            "code": "04.02.00",
                            "name_cn": "纺织品的织造",
                            "name_en": "Weaving of textiles"
                        }
                    ]
                },
                {
                    "code": "04.03",
                    "name_cn": "纺织品的整理",
                    "name_en": "Finishing of textiles",
                    "minor_categories": [
                        {
                            "code": "04.03.00",
                            "name_cn": "纺织品的整理",
                            "name_en": "Finishing of textiles"
                        }
                    ]
                },
                {
                    "code": "04.04",
                    "name_cn": "其他纺织品的制造",
                    "name_en": "Manufacture of other textiles",
                    "minor_categories": [
                        {
                            "code": "04.04.01",
                            "name_cn": "针织和钩编织物的制造",
                            "name_en": "Manufacture of knitted and crocheted fabrics"
                        },
                        {
                            "code": "04.04.02",
                            "name_cn": "纺织成品的制造（服装除外）",
                            "name_en": "Manufacture of made-up textile articles, except apparel"
                        },
                        {
                            "code": "04.04.03",
                            "name_cn": "地毯和小地毯的制造",
                            "name_en": "Manufacture of carpets and rugs"
                        },
                        {
                            "code": "04.04.04",
                            "name_cn": "绳、缆、合股线及网状制品的制造",
                            "name_en": "Manufacture of cordage, rope, twine and netting"
                        },
                        {
                            "code": "04.04.05",
                            "name_cn": "无纺布及其制品的制造（服装除外）",
                            "name_en": "Manufacture of non-wovens and articles made from non-wovens, except apparel"
                        },
                        {
                            "code": "04.04.06",
                            "name_cn": "其他技术的和工业用纺织品的制造",
                            "name_en": "Manufacture of other technical and industrial textiles"
                        },
                        {
                            "code": "04.04.07",
                            "name_cn": "其他未另分类纺织品的制造",
                            "name_en": "Manufacture of other textiles n.e.c."
                        }
                    ]
                },
                {
                    "code": "04.05",
                    "name_cn": "服装的制造（毛皮服装除外）",
                    "name_en": "Manufacture of wearing apparel, except fur apparel",
                    "minor_categories": [
                        {
                            "code": "04.05.01",
                            "name_cn": "皮革服装的制造",
                            "name_en": "Manufacture of leather clothes"
                        },
                        {
                            "code": "04.05.02",
                            "name_cn": "工作服的制造",
                            "name_en": "Manufacture of workwear"
                        },
                        {
                            "code": "04.05.03",
                            "name_cn": "其他外衣的制造",
                            "name_en": "Manufacture of other outerwear"
                        },
                        {
                            "code": "04.05.04",
                            "name_cn": "内衣的制造",
                            "name_en": "Manufacture of underwear"
                        },
                        {
                            "code": "04.05.05",
                            "name_cn": "其他服装和配件的制造",
                            "name_en": "Manufacture of other wearing apparel and accessories"
                        }
                    ]
                },
                {
                    "code": "04.06",
                    "name_cn": "毛皮制品的制造",
                    "name_en": "Manufacture of articles of fur",
                    "minor_categories": [
                        {
                            "code": "04.06.00",
                            "name_cn": "毛皮制品的制造",
                            "name_en": "Manufacture of articles of fur"
                        }
                    ]
                },
                {
                    "code": "04.07",
                    "name_cn": "针织及钩编服装的制造",
                    "name_en": "Manufacture of knitted and crocheted apparel",
                    "minor_categories": [
                        {
                            "code": "04.07.01",
                            "name_cn": "针织及钩编袜类的制造",
                            "name_en": "Manufacture of knitted and crocheted hosiery"
                        },
                        {
                            "code": "04.07.02",
                            "name_cn": "其他针织或钩编服装的制造",
                            "name_en": "Manufacture of other knitted and crocheted apparel"
                        }
                    ]
                }
            ]
        },
        {
            "code": "05",
            "name_cn": "皮革及皮革制品",
            "name_en": "Leather and leather products",
            "sub_categories": [
                {
                    "code": "05.01",
                    "name_cn": "皮革的鞣制和整饰，箱包、手袋、马具和挽具的制造，毛皮的整饰和染色",
                    "name_en": "Tanning and dressing of leather; manufacture of luggage, handbags, saddlery and harness; dressing and dyeing of fur",
                    "minor_categories": [
                        {
                            "code": "05.01.01",
                            "name_cn": "皮革的鞣制和整饰，毛皮的整饰与染色",
                            "name_en": "Tanning and dressing of leather; dressing and dyeing of fur"
                        },
                        {
                            "code": "05.01.02",
                            "name_cn": "箱包、手袋及类似品，马具和挽具的制造",
                            "name_en": "Manufacture of luggage, handbags and the like, saddlery and harness"
                        }
                    ]
                },
                {
                    "code": "05.02",
                    "name_cn": "鞋类的制造",
                    "name_en": "Manufacture of footwear",
                    "minor_categories": [
                        {
                            "code": "05.02.00",
                            "name_cn": "鞋类的制造",
                            "name_en": "Manufacture of footwear"
                        }
                    ]
                }
            ]
        },
        {
            "code": "06",
            "name_cn": "木材及木制品",
            "name_en": "Wood and wood products",
            "sub_categories": [
                {
                    "code": "06.01",
                    "name_cn": "木材的锯与刨",
                    "name_en": "Sawmilling and planing of wood",
                    "minor_categories": [
                        {
                            "code": "06.01.00",
                            "name_cn": "木材的锯与刨",
                            "name_en": "Sawmilling and planing of wood"
                        }
                    ]
                },
                {
                    "code": "06.02",
                    "name_cn": "木材、软木、稻草及编织材料制品的制造",
                    "name_en": "Manufacture of products of wood, cork, straw and plaiting materials",
                    "minor_categories": [
                        {
                            "code": "06.02.01",
                            "name_cn": "装饰板和人造板的制造",
                            "name_en": "Manufacture of veneer sheets and wood-based panels"
                        },
                        {
                            "code": "06.02.02",
                            "name_cn": "组装拼花地板的制造",
                            "name_en": "Manufacture of assembled parquet floors"
                        },
                        {
                            "code": "06.02.03",
                            "name_cn": "其他建筑用木工制品和细木工制品的制造",
                            "name_en": "Manufacture of other builders' carpentry and joinery"
                        },
                        {
                            "code": "06.02.04",
                            "name_cn": "木制容器的制造",
                            "name_en": "Manufacture of wooden containers"
                        },
                        {
                            "code": "06.02.05",
                            "name_cn": "其他木制品的制造，软木、稻草及编织材料制品的制造",
                            "name_en": "Manufacture of other products of wood; manufacture of articles of cork, straw and plaiting materials"
                        }
                    ]
                }
            ]
        },
        {
            "code": "07",
            "name_cn": "纸浆、纸及纸制品",
            "name_en": "Pulp, paper and paper products",
            "sub_categories": [
                {
                    "code": "07.01",
                    "name_cn": "纸浆、纸和纸板的制造",
                    "name_en": "Manufacture of pulp, paper and paperboard",
                    "minor_categories": [
                        {
                            "code": "07.01.01",
                            "name_cn": "纸浆的制造",
                            "name_en": "Manufacture of pulp"
                        },
                        {
                            "code": "07.01.02",
                            "name_cn": "纸和纸板的制造",
                            "name_en": "Manufacture of paper and paperboard"
                        }
                    ]
                },
                {
                    "code": "07.02",
                    "name_cn": "纸和纸板制品的制造",
                    "name_en": "Manufacture of articles of paper and paperboard",
                    "minor_categories": [
                        {
                            "code": "07.02.01",
                            "name_cn": "瓦楞纸和瓦楞纸板以及纸和纸板容器的制造",
                            "name_en": "Manufacture of corrugated paper and paperboard and of containers of paper and paperboard"
                        },
                        {
                            "code": "07.02.02",
                            "name_cn": "家用和卫生用品及洗手间用品的制造",
                            "name_en": "Manufacture of household and sanitary goods and of toilet requisites"
                        },
                        {
                            "code": "07.02.03",
                            "name_cn": "纸制文具的制造",
                            "name_en": "Manufacture of paper stationery"
                        },
                        {
                            "code": "07.02.04",
                            "name_cn": "壁纸的制造",
                            "name_en": "Manufacture of wallpaper"
                        },
                        {
                            "code": "07.02.05",
                            "name_cn": "其他纸和纸板制品的制造",
                            "name_en": "Manufacture of other articles of paper and paperboard"
                        }
                    ]
                }
            ]
        },
        {
            "code": "08",
            "name_cn": "出版业",
            "name_en": "Publishing companies",
            "sub_categories": [
                {
                    "code": "08.01",
                    "name_cn": "书籍、期刊的出版和其他出版活动",
                    "name_en": "Publishing of books, periodicals and other publishing activities",
                    "minor_categories": [
                        {
                            "code": "08.01.01",
                            "name_cn": "书籍出版",
                            "name_en": "Book publishing"
                        },
                        {
                            "code": "08.01.02",
                            "name_cn": "号码簿和通讯名录的出版",
                            "name_en": "Publishing of directories and mailing lists"
                        },
                        {
                            "code": "08.01.03",
                            "name_cn": "报纸出版",
                            "name_en": "Publishing of newspapers"
                        },
                        {
                            "code": "08.01.04",
                            "name_cn": "杂志和期刊的出版",
                            "name_en": "Publishing of journals and periodicals"
                        },
                        {
                            "code": "08.01.05",
                            "name_cn": "其他出版活动",
                            "name_en": "Other publishing activities"
                        }
                    ]
                },
                {
                    "code": "08.02",
                    "name_cn": "录音及音乐出版活动",
                    "name_en": "Sound recording and music publishing activities",
                    "minor_categories": [
                        {
                            "code": "08.02.00",
                            "name_cn": "录音及音乐出版活动",
                            "name_en": "Sound recording and music publishing activities"
                        }
                    ]
                }
            ]
        },
        {
            "code": "09",
            "name_cn": "印刷业",
            "name_en": "Printing companies",
            "sub_categories": [
                {
                    "code": "09.01",
                    "name_cn": "印刷及与印刷相关的服务活动",
                    "name_en": "Printing and service activities related to printing",
                    "minor_categories": [
                        {
                            "code": "09.01.01",
                            "name_cn": "报纸的印刷",
                            "name_en": "Printing of newspapers"
                        },
                        {
                            "code": "09.01.02",
                            "name_cn": "其他印刷",
                            "name_en": "Other printing"
                        },
                        {
                            "code": "09.01.03",
                            "name_cn": "印刷前和媒体复制前服务",
                            "name_en": "Pre-press and pre-media services"
                        },
                        {
                            "code": "09.01.04",
                            "name_cn": "装订及相关服务",
                            "name_en": "Binding and related services"
                        }
                    ]
                },
                {
                    "code": "09.02",
                    "name_cn": "记录媒介的复制",
                    "name_en": "Reproduction of recorded media",
                    "minor_categories": [
                        {
                            "code": "09.02.00",
                            "name_cn": "记录媒介的复制",
                            "name_en": "Reproduction of recorded media"
                        }
                    ]
                }
            ]
        },
        {
            "code": "10",
            "name_cn": "焦炭及精炼石油制品的制造",
            "name_en": "Manufacture of coke and refined petroleum products",
            "sub_categories": [
                {
                    "code": "10.01",
                    "name_cn": "焦炉产品的制造",
                    "name_en": "Manufacture of coke oven products",
                    "minor_categories": [
                        {
                            "code": "10.01.00",
                            "name_cn": "焦炉产品的制造",
                            "name_en": "Manufacture of coke oven products"
                        }
                    ]
                },
                {
                    "code": "10.02",
                    "name_cn": "精炼石油制品的制造",
                    "name_en": "Manufacture of refined petroleum products",
                    "minor_categories": [
                        {
                            "code": "10.02.00",
                            "name_cn": "精炼石油制品的制造",
                            "name_en": "Manufacture of refined petroleum products"
                        }
                    ]
                }
            ]
        },
        {
            "code": "11",
            "name_cn": "核燃料",
            "name_en": "Nuclear fuel",
            "sub_categories": [
                {
                    "code": "11.01",
                    "name_cn": "核燃料的加工",
                    "name_en": "Processing of nuclear fuel",
                    "minor_categories": [
                        {
                            "code": "11.01.00",
                            "name_cn": "核燃料的加工",
                            "name_en": "Processing of nuclear fuel"
                        }
                    ]
                }
            ]
        },
        {
            "code": "12",
            "name_cn": "化学品、化学制品及纤维",
            "name_en": "Chemicals, chemical products and fibres",
            "sub_categories": [
                {
                    "code": "12.01",
                    "name_cn": "基础化学品、化肥及含氮化合物、初级形态的塑料和合成橡胶的制造",
                    "name_en": "Manufacture of basic chemicals, fertilisers and nitrogen compounds, plastics and synthetic rubber in primary forms",
                    "minor_categories": [
                        {
                            "code": "12.01.01",
                            "name_cn": "工业用气体的制造",
                            "name_en": "Manufacture of industrial gases"
                        },
                        {
                            "code": "12.01.02",
                            "name_cn": "染料和颜料的制造",
                            "name_en": "Manufacture of dyes and pigments"
                        },
                        {
                            "code": "12.01.03",
                            "name_cn": "其他无机基础化学制品的制造",
                            "name_en": "Manufacture of other inorganic basic chemicals"
                        },
                        {
                            "code": "12.01.04",
                            "name_cn": "其他有机基础化学制品的制造",
                            "name_en": "Manufacture of other organic basic chemicals"
                        },
                        {
                            "code": "12.01.05",
                            "name_cn": "化肥及含氮化合物的制造",
                            "name_en": "Manufacture of fertilisers and nitrogen compounds"
                        },
                        {
                            "code": "12.01.06",
                            "name_cn": "初级形态塑料的制造",
                            "name_en": "Manufacture of plastics in primary forms"
                        },
                        {
                            "code": "12.01.07",
                            "name_cn": "初级形态合成橡胶的制造",
                            "name_en": "Manufacture of synthetic rubber in primary forms"
                        }
                    ]
                },
                {
                    "code": "12.02",
                    "name_cn": "杀虫剂及其他农用化学品的制造",
                    "name_en": "Manufacture of pesticides and other agro-chemical products",
                    "minor_categories": [
                        {
                            "code": "12.02.00",
                            "name_cn": "杀虫剂及其他农用化学品的制造",
                            "name_en": "Manufacture of pesticides and other agro-chemical products"
                        }
                    ]
                },
                {
                    "code": "12.03",
                    "name_cn": "色漆、清漆和类似涂料、印刷油墨及填补剂的制造",
                    "name_en": "Manufacture of paints, varnishes and similar coatings, printing ink and mastics",
                    "minor_categories": [
                        {
                            "code": "12.03.00",
                            "name_cn": "色漆、清漆和类似涂料、印刷油墨及填补剂的制造",
                            "name_en": "Manufacture of paints, varnishes and similar coatings, printing ink and mastics"
                        }
                    ]
                },
                {
                    "code": "12.04",
                    "name_cn": "肥皂及洗涤剂、清洗上光剂、香水及盥洗用品的制造",
                    "name_en": "Manufacture of soap and detergents, cleaning and polishing preparations, perfumes and toilet preparations",
                    "minor_categories": [
                        {
                            "code": "12.04.01",
                            "name_cn": "肥皂及洗涤剂、清洗上光剂的制造",
                            "name_en": "Manufacture of soap and detergents, cleaning and polishing preparations"
                        },
                        {
                            "code": "12.04.02",
                            "name_cn": "香水及盥洗用品的制造",
                            "name_en": "Manufacture of perfumes and toilet preparations"
                        }
                    ]
                },
                {
                    "code": "12.05",
                    "name_cn": "其他化学制品的制造",
                    "name_en": "Manufacture of other chemical products",
                    "minor_categories": [
                        {
                            "code": "12.05.01",
                            "name_cn": "炸药的制造",
                            "name_en": "Manufacture of explosives"
                        },
                        {
                            "code": "12.05.02",
                            "name_cn": "胶粘剂的制造",
                            "name_en": "Manufacture of glues"
                        },
                        {
                            "code": "12.05.03",
                            "name_cn": "精油的制造",
                            "name_en": "Manufacture of essential oils"
                        },
                        {
                            "code": "12.05.04",
                            "name_cn": "其他未另分类化学制品的制造",
                            "name_en": "Manufacture of other chemical products n.e.c."
                        }
                    ]
                },
                {
                    "code": "12.06",
                    "name_cn": "合成纤维的制造",
                    "name_en": "Manufacture of man-made fibres",
                    "minor_categories": [
                        {
                            "code": "12.06.00",
                            "name_cn": "合成纤维的制造",
                            "name_en": "Manufacture of man-made fibres"
                        }
                    ]
                }
            ]
        },
        {
            "code": "13",
            "name_cn": "药品",
            "name_en": "Pharmaceuticals",
            "sub_categories": [
                {
                    "code": "13.01",
                    "name_cn": "基础药物制品的制造",
                    "name_en": "Manufacture of basic pharmaceutical products",
                    "minor_categories": [
                        {
                            "code": "13.01.00",
                            "name_cn": "基础药物制品的制造",
                            "name_en": "Manufacture of basic pharmaceutical products"
                        }
                    ]
                },
                {
                    "code": "13.02",
                    "name_cn": "药物制剂的制造",
                    "name_en": "Manufacture of pharmaceutical preparations",
                    "minor_categories": [
                        {
                            "code": "13.02.00",
                            "name_cn": "药物制剂的制造",
                            "name_en": "Manufacture of pharmaceutical preparations"
                        }
                    ]
                }
            ]
        },
        {
            "code": "14",
            "name_cn": "橡胶和塑料制品",
            "name_en": "Rubber and plastic products",
            "sub_categories": [
                {
                    "code": "14.01",
                    "name_cn": "橡胶制品的制造",
                    "name_en": "Manufacture of rubber products",
                    "minor_categories": [
                        {
                            "code": "14.01.01",
                            "name_cn": "橡胶轮胎和内胎的制造，橡胶轮胎翻新和再造",
                            "name_en": "Manufacture of rubber tyres and tubes; retreading and rebuilding of rubber tyres"
                        },
                        {
                            "code": "14.01.02",
                            "name_cn": "其他橡胶制品的制造",
                            "name_en": "Manufacture of other rubber products"
                        }
                    ]
                },
                {
                    "code": "14.02",
                    "name_cn": "塑料制品的制造",
                    "name_en": "Manufacture of plastics products",
                    "minor_categories": [
                        {
                            "code": "14.02.01",
                            "name_cn": "塑料板、塑料片、塑料管及塑料壳体的制造",
                            "name_en": "Manufacture of plastic plates, sheets, tubes and profiles"
                        },
                        {
                            "code": "14.02.02",
                            "name_cn": "塑料包装产品的制造",
                            "name_en": "Manufacture of plastic packing goods"
                        },
                        {
                            "code": "14.02.03",
                            "name_cn": "建筑用塑料制品的制造",
                            "name_en": "Manufacture of builders' ware of plastic"
                        },
                        {
                            "code": "14.02.04",
                            "name_cn": "其他塑料制品的制造",
                            "name_en": "Manufacture of other plastic products"
                        }
                    ]
                }
            ]
        },
        {
            "code": "15",
            "name_cn": "非金属矿物制品",
            "name_en": "Non-metallic mineral products",
            "sub_categories": [
                {
                    "code": "15.01",
                    "name_cn": "玻璃及玻璃制品的制造",
                    "name_en": "Manufacture of glass and glass products",
                    "minor_categories": [
                        {
                            "code": "15.01.01",
                            "name_cn": "平板玻璃的制造",
                            "name_en": "Manufacture of flat glass"
                        },
                        {
                            "code": "15.01.02",
                            "name_cn": "平板玻璃的成形和加工",
                            "name_en": "Shaping and processing of flat glass"
                        },
                        {
                            "code": "15.01.03",
                            "name_cn": "凹形玻璃的制造",
                            "name_en": "Manufacture of hollow glass"
                        },
                        {
                            "code": "15.01.04",
                            "name_cn": "玻璃纤维的制造",
                            "name_en": "Manufacture of glass fibres"
                        },
                        {
                            "code": "15.01.05",
                            "name_cn": "含专业用玻璃器具在内的其他玻璃制品的制造及加工",
                            "name_en": "Manufacture and processing of other glass, including technical glassware"
                        }
                    ]
                },
                {
                    "code": "15.02",
                    "name_cn": "耐火制品的制造",
                    "name_en": "Manufacture of refractory products",
                    "minor_categories": [
                        {
                            "code": "15.02.00",
                            "name_cn": "耐火制品的制造",
                            "name_en": "Manufacture of refractory products"
                        }
                    ]
                },
                {
                    "code": "15.03",
                    "name_cn": "粘土建筑材料的制造",
                    "name_en": "Manufacture of clay building materials",
                    "minor_categories": [
                        {
                            "code": "15.03.01",
                            "name_cn": "陶瓷砖和陶瓷板的制造",
                            "name_en": "Manufacture of ceramic tiles and flags"
                        },
                        {
                            "code": "15.03.02",
                            "name_cn": "粘土烧制砖、瓦及建筑制品的制造",
                            "name_en": "Manufacture of bricks, tiles and construction products, in baked clay"
                        }
                    ]
                },
                {
                    "code": "15.04",
                    "name_cn": "其他瓷器和陶瓷制品的制造",
                    "name_en": "Manufacture of other porcelain and ceramic products",
                    "minor_categories": [
                        {
                            "code": "15.04.01",
                            "name_cn": "家用及装饰用陶瓷制品的制造",
                            "name_en": "Manufacture of ceramic household and ornamental articles"
                        },
                        {
                            "code": "15.04.02",
                            "name_cn": "卫生陶瓷洁具的制造",
                            "name_en": "Manufacture of ceramic sanitary fixtures"
                        },
                        {
                            "code": "15.04.03",
                            "name_cn": "绝缘陶瓷及配件的制造",
                            "name_en": "Manufacture of ceramic insulators and insulating fittings"
                        },
                        {
                            "code": "15.04.04",
                            "name_cn": "其他专业陶瓷制品的制造",
                            "name_en": "Manufacture of other technical ceramic products"
                        },
                        {
                            "code": "15.04.05",
                            "name_cn": "其他陶瓷制品的制造",
                            "name_en": "Manufacture of other ceramic products"
                        }
                    ]
                },
                {
                    "code": "15.05",
                    "name_cn": "石材切割、成形及精加工",
                    "name_en": "Cutting, shaping and finishing of stone",
                    "minor_categories": [
                        {
                            "code": "15.05.00",
                            "name_cn": "石材切割、成形及精加工",
                            "name_en": "Cutting, shaping and finishing of stone"
                        }
                    ]
                },
                {
                    "code": "15.06",
                    "name_cn": "磨料制品及未另分类的非金属矿物制品的制造",
                    "name_en": "Manufacture of abrasive products and non-metallic mineral products n.e.c.",
                    "minor_categories": [
                        {
                            "code": "15.06.01",
                            "name_cn": "磨料制品的生产",
                            "name_en": "Production of abrasive products"
                        },
                        {
                            "code": "15.06.02",
                            "name_cn": "其他未另分类的非金属矿物制品的制造",
                            "name_en": "Manufacture of other non-metallic mineral products n.e.c."
                        }
                    ]
                }
            ]
        },
        {
            "code": "16",
            "name_cn": "混凝土、水泥、石灰、石膏及其他",
            "name_en": "Concrete, cement, lime, plaster etc",
            "sub_categories": [
                {
                    "code": "16.01",
                    "name_cn": "水泥、石灰和石膏的制造",
                    "name_en": "Manufacture of cement, lime and plaster",
                    "minor_categories": [
                        {
                            "code": "16.01.01",
                            "name_cn": "水泥的制造",
                            "name_en": "Manufacture of cement"
                        },
                        {
                            "code": "16.01.02",
                            "name_cn": "石灰和石膏的制造",
                            "name_en": "Manufacture of lime and plaster"
                        }
                    ]
                },
                {
                    "code": "16.02",
                    "name_cn": "混凝土、水泥及石膏制品的制造",
                    "name_en": "Manufacture of articles of concrete, cement and plaster",
                    "minor_categories": [
                        {
                            "code": "16.02.01",
                            "name_cn": "建筑用混凝土制品的制造",
                            "name_en": "Manufacture of concrete products for construction purposes"
                        },
                        {
                            "code": "16.02.02",
                            "name_cn": "建筑用石膏制品的制造",
                            "name_en": "Manufacture of plaster products for construction purposes"
                        },
                        {
                            "code": "16.02.03",
                            "name_cn": "预拌混凝土的制造",
                            "name_en": "Manufacture of ready-mixed concrete"
                        },
                        {
                            "code": "16.02.04",
                            "name_cn": "砂浆的制造",
                            "name_en": "Manufacture of mortars"
                        },
                        {
                            "code": "16.02.05",
                            "name_cn": "纤维水泥的制造",
                            "name_en": "Manufacture of fibre cement"
                        },
                        {
                            "code": "16.02.06",
                            "name_cn": "其他混凝土、石膏和水泥制品的制造",
                            "name_en": "Manufacture of other articles of concrete, plaster and cement"
                        }
                    ]
                }
            ]
        },
        {
            "code": "17",
            "name_cn": "基础金属及金属制品",
            "name_en": "Basic metals and fabricated metal products",
            "sub_categories": [
                {
                    "code": "17.01",
                    "name_cn": "生铁、粗钢及铁合金的制造",
                    "name_en": "Manufacture of basic iron and steel and of ferro-alloys",
                    "minor_categories": [
                        {
                            "code": "17.01.00",
                            "name_cn": "生铁、粗钢及铁合金的制造",
                            "name_en": "Manufacture of basic iron and steel and of ferro-alloys"
                        }
                    ]
                },
                {
                    "code": "17.02",
                    "name_cn": "钢管、空心异型钢材及相关配件的制造",
                    "name_en": "Manufacture of tubes, pipes, hollow profiles and related fittings, of steel",
                    "minor_categories": [
                        {
                            "code": "17.02.00",
                            "name_cn": "钢管、空心异型钢材及相关配件的制造",
                            "name_en": "Manufacture of tubes, pipes, hollow profiles and related fittings, of steel"
                        }
                    ]
                },
                {
                    "code": "17.03",
                    "name_cn": "其他的钢初加工品的制造",
                    "name_en": "Manufacture of other products of first processing of steel",
                    "minor_categories": [
                        {
                            "code": "17.03.01",
                            "name_cn": "冷拔棒材",
                            "name_en": "Cold drawing of bars"
                        },
                        {
                            "code": "17.03.02",
                            "name_cn": "窄带冷轧",
                            "name_en": "Cold rolling of narrow strip"
                        },
                        {
                            "code": "17.03.03",
                            "name_cn": "冷成形或折叠",
                            "name_en": "Cold forming or folding"
                        },
                        {
                            "code": "17.03.04",
                            "name_cn": "线材冷拔",
                            "name_en": "Cold drawing of wire"
                        }
                    ]
                },
                {
                    "code": "17.04",
                    "name_cn": "基础贵金属和其他非铁金属的制造",
                    "name_en": "Manufacture of basic precious and other non-ferrous metals",
                    "minor_categories": [
                        {
                            "code": "17.04.01",
                            "name_cn": "贵金属的生产",
                            "name_en": "Precious metals production"
                        },
                        {
                            "code": "17.04.02",
                            "name_cn": "铝的生产",
                            "name_en": "Aluminium production"
                        },
                        {
                            "code": "17.04.03",
                            "name_cn": "铅、锌和锡的生产",
                            "name_en": "Lead, zinc and tin production"
                        },
                        {
                            "code": "17.04.04",
                            "name_cn": "铜的生产",
                            "name_en": "Copper production"
                        },
                        {
                            "code": "17.04.05",
                            "name_cn": "其他非铁金属的生产",
                            "name_en": "Other non-ferrous metal production"
                        }
                    ]
                },
                {
                    "code": "17.05",
                    "name_cn": "金属的铸造",
                    "name_en": "Casting of metals",
                    "minor_categories": [
                        {
                            "code": "17.05.01",
                            "name_cn": "铁的铸造",
                            "name_en": "Casting of iron"
                        },
                        {
                            "code": "17.05.02",
                            "name_cn": "钢的铸造",
                            "name_en": "Casting of steel"
                        },
                        {
                            "code": "17.05.03",
                            "name_cn": "轻金属的铸造",
                            "name_en": "Casting of light metals"
                        },
                        {
                            "code": "17.05.04",
                            "name_cn": "其他非铁金属的铸造",
                            "name_en": "Casting of other non-ferrous metals"
                        }
                    ]
                },
                {
                    "code": "17.06",
                    "name_cn": "结构用金属制品的制造",
                    "name_en": "Manufacture of structural metal products",
                    "minor_categories": [
                        {
                            "code": "17.06.01",
                            "name_cn": "金属结构物及结构件的制造",
                            "name_en": "Manufacture of metal structures and parts of structures"
                        },
                        {
                            "code": "17.06.02",
                            "name_cn": "金属门窗的制造",
                            "name_en": "Manufacture of doors and windows of metal"
                        }
                    ]
                },
                {
                    "code": "17.07",
                    "name_cn": "金属箱、槽及容器的制造",
                    "name_en": "Manufacture of tanks, reservoirs and containers of metal",
                    "minor_categories": [
                        {
                            "code": "17.07.01",
                            "name_cn": "集中供暖散热器和锅炉的制造",
                            "name_en": "Manufacture of central heating radiators and boilers"
                        },
                        {
                            "code": "17.07.02",
                            "name_cn": "其他金属箱、槽及容器的制造",
                            "name_en": "Manufacture of other tanks, reservoirs and containers of metal"
                        }
                    ]
                },
                {
                    "code": "17.08",
                    "name_cn": "蒸汽发生器的制造（集中供暖热水锅炉除外）",
                    "name_en": "Manufacture of steam generators, except central heating hot water boilers",
                    "minor_categories": [
                        {
                            "code": "17.08.00",
                            "name_cn": "蒸汽发生器的制造（集中供暖热水锅炉除外）",
                            "name_en": "Manufacture of steam generators, except central heating hot water boilers"
                        }
                    ]
                },
                {
                    "code": "17.09",
                    "name_cn": "金属锻造、挤压、冲压和滚压成型，粉末冶金",
                    "name_en": "Forging, pressing, stamping and roll-forming of metal; powder metallurgy",
                    "minor_categories": [
                        {
                            "code": "17.09.00",
                            "name_cn": "金属锻造、挤压、冲压和滚压成型，粉末冶金",
                            "name_en": "Forging, pressing, stamping and roll-forming of metal; powder metallurgy"
                        }
                    ]
                },
                {
                    "code": "17.10",
                    "name_cn": "金属的处理和涂覆，机加工",
                    "name_en": "Treatment and coating of metals; machining",
                    "minor_categories": [
                        {
                            "code": "17.10.01",
                            "name_cn": "金属的处理和涂覆",
                            "name_en": "Treatment and coating of metals"
                        },
                        {
                            "code": "17.10.02",
                            "name_cn": "机加工",
                            "name_en": "Machining"
                        }
                    ]
                },
                {
                    "code": "17.11",
                    "name_cn": "刃具、工具及一般五金器具的制造",
                    "name_en": "Manufacture of cutlery, tools and general hardware",
                    "minor_categories": [
                        {
                            "code": "17.11.01",
                            "name_cn": "刃具的制造",
                            "name_en": "Manufacture of cutlery"
                        },
                        {
                            "code": "17.11.02",
                            "name_cn": "锁和铰链的制造",
                            "name_en": "Manufacture of locks and hinges"
                        },
                        {
                            "code": "17.11.03",
                            "name_cn": "工具的制造",
                            "name_en": "Manufacture of tools"
                        }
                    ]
                },
                {
                    "code": "17.12",
                    "name_cn": "其他金属加工制品的制造",
                    "name_en": "Manufacture of other fabricated metal products",
                    "minor_categories": [
                        {
                            "code": "17.12.01",
                            "name_cn": "钢桶及类似容器的制造",
                            "name_en": "Manufacture of steel drums and similar containers"
                        },
                        {
                            "code": "17.12.02",
                            "name_cn": "轻金属包装物的制造",
                            "name_en": "Manufacture of light metal packaging"
                        },
                        {
                            "code": "17.12.03",
                            "name_cn": "金属丝制品、链条和弹簧的制造",
                            "name_en": "Manufacture of wire products, chain and springs"
                        },
                        {
                            "code": "17.12.04",
                            "name_cn": "紧固件和螺杆机械产品的制造",
                            "name_en": "Manufacture of fasteners and screw machine products"
                        },
                        {
                            "code": "17.12.05",
                            "name_cn": "其他未另分类的金属制品的制造",
                            "name_en": "Manufacture of other fabricated metal products n.e.c."
                        }
                    ]
                },
                {
                    "code": "17.13",
                    "name_cn": "金属加工制品的维修",
                    "name_en": "Repair of fabricated metal products",
                    "minor_categories": [
                        {
                            "code": "17.13.00",
                            "name_cn": "金属加工制品的维修",
                            "name_en": "Repair of fabricated metal products"
                        }
                    ]
                }
            ]
        },
        {
            "code": "18",
            "name_cn": "机械及设备",
            "name_en": "Machinery and equipment",
            "sub_categories": [
                {
                    "code": "18.01",
                    "name_cn": "通用机械的制造",
                    "name_en": "Manufacture of general-purpose machinery",
                    "minor_categories": [
                        {
                            "code": "18.01.01",
                            "name_cn": "发动机和涡轮机的制造（飞机、汽车和摩托车发动机除外）",
                            "name_en": "Manufacture of engines and turbines, except aircraft, vehicle and cycle engines"
                        },
                        {
                            "code": "18.01.02",
                            "name_cn": "液压设备的制造",
                            "name_en": "Manufacture of fluid power equipment"
                        },
                        {
                            "code": "18.01.03",
                            "name_cn": "其他泵和压缩机的制造",
                            "name_en": "Manufacture of other pumps and compressors"
                        },
                        {
                            "code": "18.01.04",
                            "name_cn": "其他龙头和阀门的制造",
                            "name_en": "Manufacture of other taps and valves"
                        },
                        {
                            "code": "18.01.05",
                            "name_cn": "轴承、齿轮、传动及驱动部件的制造",
                            "name_en": "Manufacture of bearings, gears, gearing and driving elements"
                        }
                    ]
                },
                {
                    "code": "18.02",
                    "name_cn": "其他通用机械的制造",
                    "name_en": "Manufacture of other general-purpose machinery",
                    "minor_categories": [
                        {
                            "code": "18.02.01",
                            "name_cn": "烘箱、熔炉和熔炉燃烧器的制造",
                            "name_en": "Manufacture of ovens, furnaces and furnace burners"
                        },
                        {
                            "code": "18.02.02",
                            "name_cn": "起重和搬运设备的制造",
                            "name_en": "Manufacture of lifting and handling equipment"
                        },
                        {
                            "code": "18.02.03",
                            "name_cn": "办公机械和设备的制造（计算机及外部设备除外）",
                            "name_en": "Manufacture of office machinery and equipment (except computers and peripheral equipment)"
                        },
                        {
                            "code": "18.02.04",
                            "name_cn": "动力驱动手工工具的制造",
                            "name_en": "Manufacture of power-driven hand tools"
                        },
                        {
                            "code": "18.02.05",
                            "name_cn": "非家用制冷及通风设备的制造",
                            "name_en": "Manufacture of non-domestic cooling and ventilation equipment"
                        },
                        {
                            "code": "18.02.06",
                            "name_cn": "其他未另分类的通用机械的制造",
                            "name_en": "Manufacture of other general-purpose machinery n.e.c."
                        }
                    ]
                },
                {
                    "code": "18.03",
                    "name_cn": "农业和林业机械的制造",
                    "name_en": "Manufacture of agricultural and forestry machinery",
                    "minor_categories": [
                        {
                            "code": "18.03.00",
                            "name_cn": "农业和林业机械的制造",
                            "name_en": "Manufacture of agricultural and forestry machinery"
                        }
                    ]
                },
                {
                    "code": "18.04",
                    "name_cn": "金属成型机械及机床的制造",
                    "name_en": "Manufacture of metal forming machinery and machine tools",
                    "minor_categories": [
                        {
                            "code": "18.04.01",
                            "name_cn": "金属成型机械的制造",
                            "name_en": "Manufacture of metal forming machinery"
                        },
                        {
                            "code": "18.04.02",
                            "name_cn": "其他机床的制造",
                            "name_en": "Manufacture of other machine tools"
                        }
                    ]
                },
                {
                    "code": "18.05",
                    "name_cn": "其他专用机械的制造",
                    "name_en": "Manufacture of other special-purpose machinery",
                    "minor_categories": [
                        {
                            "code": "18.05.01",
                            "name_cn": "冶金机械的制造",
                            "name_en": "Manufacture of machinery for metallurgy"
                        },
                        {
                            "code": "18.05.02",
                            "name_cn": "采矿、采石和建筑机械的制造",
                            "name_en": "Manufacture of machinery for mining, quarrying and construction"
                        },
                        {
                            "code": "18.05.03",
                            "name_cn": "食品、饮料和烟草加工机械的制造",
                            "name_en": "Manufacture of machinery for food, beverage and tobacco processing"
                        },
                        {
                            "code": "18.05.04",
                            "name_cn": "纺织、服装和皮革制品生产机械的制造",
                            "name_en": "Manufacture of machinery for textile, apparel and leather production"
                        },
                        {
                            "code": "18.05.05",
                            "name_cn": "纸和纸制品生产机械的制造",
                            "name_en": "Manufacture of machinery for paper and paperboard production"
                        },
                        {
                            "code": "18.05.06",
                            "name_cn": "塑料和橡胶机械的制造",
                            "name_en": "Manufacture of plastics and rubber machinery"
                        },
                        {
                            "code": "18.05.07",
                            "name_cn": "其他未另分类的专用机械的制造",
                            "name_en": "Manufacture of other special-purpose machinery n.e.c."
                        }
                    ]
                },
                {
                    "code": "18.06",
                    "name_cn": "武器和弹药的制造",
                    "name_en": "Manufacture of weapons and ammunition",
                    "minor_categories": [
                        {
                            "code": "18.06.00",
                            "name_cn": "武器和弹药的制造",
                            "name_en": "Manufacture of weapons and ammunition"
                        }
                    ]
                },
                {
                    "code": "18.07",
                    "name_cn": "军用战车的制造",
                    "name_en": "Manufacture of military fighting vehicles",
                    "minor_categories": [
                        {
                            "code": "18.07.00",
                            "name_cn": "军用战车的制造",
                            "name_en": "Manufacture of military fighting vehicles"
                        }
                    ]
                },
                {
                    "code": "18.08",
                    "name_cn": "机械的修理",
                    "name_en": "Repair of machinery",
                    "minor_categories": [
                        {
                            "code": "18.08.00",
                            "name_cn": "机械的修理",
                            "name_en": "Repair of machinery"
                        }
                    ]
                },
                {
                    "code": "18.09",
                    "name_cn": "工业机械及设备的安装",
                    "name_en": "Installation of industrial machinery and equipment",
                    "minor_categories": [
                        {
                            "code": "18.09.00",
                            "name_cn": "工业机械及设备的安装",
                            "name_en": "Installation of industrial machinery and equipment"
                        }
                    ]
                }
            ]
        },
        {
            "code": "19",
            "name_cn": "电和光学设备",
            "name_en": "Electrical and optical equipment",
            "sub_categories": [
                {
                    "code": "19.01",
                    "name_cn": "电子元器件和线路板的制造",
                    "name_en": "Manufacture of electronic components and boards",
                    "minor_categories": [
                        {
                            "code": "19.01.01",
                            "name_cn": "电子元器件的制造",
                            "name_en": "Manufacture of electronic components"
                        },
                        {
                            "code": "19.01.02",
                            "name_cn": "加载电子板的制造",
                            "name_en": "Manufacture of loaded electronic boards"
                        }
                    ]
                },
                {
                    "code": "19.02",
                    "name_cn": "计算机及其外部设备的制造",
                    "name_en": "Manufacture of computers and peripheral equipment",
                    "minor_categories": [
                        {
                            "code": "19.02.00",
                            "name_cn": "计算机及其外部设备的制造",
                            "name_en": "Manufacture of computers and peripheral equipment"
                        }
                    ]
                },
                {
                    "code": "19.03",
                    "name_cn": "通信设备的制造",
                    "name_en": "Manufacture of communication equipment",
                    "minor_categories": [
                        {
                            "code": "19.03.00",
                            "name_cn": "通信设备的制造",
                            "name_en": "Manufacture of communication equipment"
                        }
                    ]
                },
                {
                    "code": "19.04",
                    "name_cn": "消费类电子产品的制造",
                    "name_en": "Manufacture of consumer electronics",
                    "minor_categories": [
                        {
                            "code": "19.04.00",
                            "name_cn": "消费类电子产品的制造",
                            "name_en": "Manufacture of consumer electronics"
                        }
                    ]
                },
                {
                    "code": "19.05",
                    "name_cn": "测量、检测和导航仪器及装置的制造，钟表的制造",
                    "name_en": "Manufacture of instruments and appliances for measuring, testing and navigation, watches and clocks",
                    "minor_categories": [
                        {
                            "code": "19.05.01",
                            "name_cn": "测量、检测和导航仪器及装置的制造",
                            "name_en": "Manufacture of instruments and appliances for measuring, testing and navigation"
                        },
                        {
                            "code": "19.05.02",
                            "name_cn": "钟表的制造",
                            "name_en": "Manufacture of watches and clocks"
                        }
                    ]
                },
                {
                    "code": "19.06",
                    "name_cn": "放射、电子医学及电子治疗设备的制造",
                    "name_en": "Manufacture of irradiation, electromedical and electrotherapeutic equipment",
                    "minor_categories": [
                        {
                            "code": "19.06.00",
                            "name_cn": "放射、电子医学及电子治疗设备的制造",
                            "name_en": "Manufacture of irradiation, electromedical and electrotherapeutic equipment"
                        }
                    ]
                },
                {
                    "code": "19.07",
                    "name_cn": "光学仪器及摄影器材的制造",
                    "name_en": "Manufacture of optical instruments and photographic equipment",
                    "minor_categories": [
                        {
                            "code": "19.07.00",
                            "name_cn": "光学仪器及摄影器材的制造",
                            "name_en": "Manufacture of optical instruments and photographic equipment"
                        }
                    ]
                },
                {
                    "code": "19.08",
                    "name_cn": "磁性及光学媒体的制造",
                    "name_en": "Manufacture of magnetic and optical media",
                    "minor_categories": [
                        {
                            "code": "19.08.00",
                            "name_cn": "磁性及光学媒体的制造",
                            "name_en": "Manufacture of magnetic and optical media"
                        }
                    ]
                },
                {
                    "code": "19.09",
                    "name_cn": "电动机、发电机、变压器、配电及控制装置的制造",
                    "name_en": "Manufacture of electric motors, generators, transformers and electricity distribution and control apparatus",
                    "minor_categories": [
                        {
                            "code": "19.09.01",
                            "name_cn": "电动机、发电机及变压器的制造",
                            "name_en": "Manufacture of electric motors, generators and transformers"
                        },
                        {
                            "code": "19.09.02",
                            "name_cn": "配电及控制装置的制造",
                            "name_en": "Manufacture of electricity distribution and control apparatus"
                        }
                    ]
                },
                {
                    "code": "19.10",
                    "name_cn": "电池和蓄电池的制造",
                    "name_en": "Manufacture of batteries and accumulators",
                    "minor_categories": [
                        {
                            "code": "19.10.00",
                            "name_cn": "电池和蓄电池的制造",
                            "name_en": "Manufacture of batteries and accumulators"
                        }
                    ]
                },
                {
                    "code": "19.11",
                    "name_cn": "配线及配线装置的制造",
                    "name_en": "Manufacture of wiring and wiring devices",
                    "minor_categories": [
                        {
                            "code": "19.11.01",
                            "name_cn": "光缆的制造",
                            "name_en": "Manufacture of fibre optic cables"
                        },
                        {
                            "code": "19.11.02",
                            "name_cn": "其他电线电缆的制造",
                            "name_en": "Manufacture of other electronic and electric wires and cables"
                        },
                        {
                            "code": "19.11.03",
                            "name_cn": "配线装置的制造",
                            "name_en": "Manufacture of wiring devices"
                        }
                    ]
                },
                {
                    "code": "19.12",
                    "name_cn": "电气照明设备的制造",
                    "name_en": "Manufacture of electric lighting equipment",
                    "minor_categories": [
                        {
                            "code": "19.12.00",
                            "name_cn": "电气照明设备的制造",
                            "name_en": "Manufacture of electric lighting equipment"
                        }
                    ]
                },
                {
                    "code": "19.13",
                    "name_cn": "家用器具的制造",
                    "name_en": "Manufacture of domestic appliances",
                    "minor_categories": [
                        {
                            "code": "19.13.01",
                            "name_cn": "家用电器的制造",
                            "name_en": "Manufacture of electric domestic appliances"
                        },
                        {
                            "code": "19.13.02",
                            "name_cn": "家用非电器具的制造",
                            "name_en": "Manufacture of non-electric domestic appliances"
                        }
                    ]
                },
                {
                    "code": "19.14",
                    "name_cn": "其他电气设备的制造",
                    "name_en": "Manufacture of other electrical equipment",
                    "minor_categories": [
                        {
                            "code": "19.14.00",
                            "name_cn": "其他电气设备的制造",
                            "name_en": "Manufacture of other electrical equipment"
                        }
                    ]
                },
                {
                    "code": "19.15",
                    "name_cn": "电子和光学设备的修理",
                    "name_en": "Repair of electronic and optical equipment",
                    "minor_categories": [
                        {
                            "code": "19.15.00",
                            "name_cn": "电子和光学设备的修理",
                            "name_en": "Repair of electronic and optical equipment"
                        }
                    ]
                },
                {
                    "code": "19.16",
                    "name_cn": "电气设备的修理",
                    "name_en": "Repair of electrical equipment",
                    "minor_categories": [
                        {
                            "code": "19.16.00",
                            "name_cn": "电气设备的修理",
                            "name_en": "Repair of electrical equipment"
                        }
                    ]
                },
                {
                    "code": "19.17",
                    "name_cn": "计算机和通信设备的修理",
                    "name_en": "Repair of computers and communication equipment",
                    "minor_categories": [
                        {
                            "code": "19.17.01",
                            "name_cn": "计算机及外部设备的修理",
                            "name_en": "Repair of computers and peripheral equipment"
                        },
                        {
                            "code": "19.17.02",
                            "name_cn": "通信设备的修理",
                            "name_en": "Repair of communication equipment"
                        }
                    ]
                }
            ]
        },
        {
            "code": "20",
            "name_cn": "造船业",
            "name_en": "Shipbuilding",
            "sub_categories": [
                {
                    "code": "20.01",
                    "name_cn": "船舶的建造",
                    "name_en": "Building of ships and boats",
                    "minor_categories": [
                        {
                            "code": "20.01.01",
                            "name_cn": "船舶及浮式结构物的建造",
                            "name_en": "Building of ships and floating structures"
                        },
                        {
                            "code": "20.01.02",
                            "name_cn": "娱乐及运动用船只的制造",
                            "name_en": "Building of pleasure and sporting boats"
                        }
                    ]
                },
                {
                    "code": "20.02",
                    "name_cn": "船舶的维修和保养",
                    "name_en": "Repair and maintenance of ships and boats",
                    "minor_categories": [
                        {
                            "code": "20.02.00",
                            "name_cn": "船舶的维修和保养",
                            "name_en": "Repair and maintenance of ships and boats"
                        }
                    ]
                }
            ]
        },
        {
            "code": "21",
            "name_cn": "航空航天",
            "name_en": "Aerospace",
            "sub_categories": [
                {
                    "code": "21.01",
                    "name_cn": "航空和航天器及相关机械的制造",
                    "name_en": "Manufacture of air and spacecraft and related machinery",
                    "minor_categories": [
                        {
                            "code": "21.01.00",
                            "name_cn": "航空和航天器及相关机械的制造",
                            "name_en": "Manufacture of air and spacecraft and related machinery"
                        }
                    ]
                },
                {
                    "code": "21.02",
                    "name_cn": "航空和航天器的修理和维护",
                    "name_en": "Repair and maintenance of aircraft and spacecraft",
                    "minor_categories": [
                        {
                            "code": "21.02.00",
                            "name_cn": "航空和航天器的修理和维护",
                            "name_en": "Repair and maintenance of aircraft and spacecraft"
                        }
                    ]
                }
            ]
        },
        {
            "code": "22",
            "name_cn": "其他运输设备",
            "name_en": "Other transport equipment",
            "sub_categories": [
                {
                    "code": "22.01",
                    "name_cn": "汽车的制造",
                    "name_en": "Manufacture of motor vehicles",
                    "minor_categories": [
                        {
                            "code": "22.01.00",
                            "name_cn": "汽车的制造",
                            "name_en": "Manufacture of motor vehicles"
                        }
                    ]
                },
                {
                    "code": "22.02",
                    "name_cn": "汽车车体（车身）的制造，挂车和半挂车的制造",
                    "name_en": "Manufacture of bodies (coachwork) for motor vehicles; manufacture of trailers and semitrailers",
                    "minor_categories": [
                        {
                            "code": "22.02.00",
                            "name_cn": "汽车车体（车身）的制造，挂车和半挂车的制造",
                            "name_en": "Manufacture of bodies (coachwork) for motor vehicles; manufacture of trailers and semitrailers"
                        }
                    ]
                },
                {
                    "code": "22.03",
                    "name_cn": "汽车零部件及配件的制造",
                    "name_en": "Manufacture of parts and accessories for motor vehicles",
                    "minor_categories": [
                        {
                            "code": "22.03.01",
                            "name_cn": "汽车用电气和电子设备的制造",
                            "name_en": "Manufacture of electrical and electronic equipment for motor vehicles"
                        },
                        {
                            "code": "22.03.02",
                            "name_cn": "汽车其他零部件及配件的制造",
                            "name_en": "Manufacture of other parts and accessories for motor vehicles"
                        }
                    ]
                },
                {
                    "code": "22.04",
                    "name_cn": "铁路机车和车厢的制造",
                    "name_en": "Manufacture of railway locomotives and rolling stock",
                    "minor_categories": [
                        {
                            "code": "22.04.00",
                            "name_cn": "铁路机车和车厢的制造",
                            "name_en": "Manufacture of railway locomotives and rolling stock"
                        }
                    ]
                },
                {
                    "code": "22.05",
                    "name_cn": "未另分类的运输设备的制造",
                    "name_en": "Manufacture of transport equipment n.e.c.",
                    "minor_categories": [
                        {
                            "code": "22.05.01",
                            "name_cn": "摩托车的制造",
                            "name_en": "Manufacture of motorcycles"
                        },
                        {
                            "code": "22.05.02",
                            "name_cn": "自行车和残疾人座车的制造",
                            "name_en": "Manufacture of bicycles and invalid carriages"
                        },
                        {
                            "code": "22.05.03",
                            "name_cn": "其他未另分类的运输设备的制造",
                            "name_en": "Manufacture of other transport equipment n.e.c."
                        }
                    ]
                },
                {
                    "code": "22.06",
                    "name_cn": "其他运输设备的修理及保养",
                    "name_en": "Repair and maintenance of other transport equipment",
                    "minor_categories": [
                        {
                            "code": "22.06.00",
                            "name_cn": "其他运输设备的修理及保养",
                            "name_en": "Repair and maintenance of other transport equipment"
                        }
                    ]
                }
            ]
        },
        {
            "code": "23",
            "name_cn": "其他未另分类制造业",
            "name_en": "Manufacturing not elsewhere classified",
            "sub_categories": [
                {
                    "code": "23.01",
                    "name_cn": "家具的制造",
                    "name_en": "Manufacture of furniture",
                    "minor_categories": [
                        {
                            "code": "23.01.01",
                            "name_cn": "办公及店用家具的制造",
                            "name_en": "Manufacture of office and shop furniture"
                        },
                        {
                            "code": "23.01.02",
                            "name_cn": "厨房家具的制造",
                            "name_en": "Manufacture of kitchen furniture"
                        },
                        {
                            "code": "23.01.03",
                            "name_cn": "床垫的制造",
                            "name_en": "Manufacture of mattresses"
                        },
                        {
                            "code": "23.01.04",
                            "name_cn": "其他家具的制造",
                            "name_en": "Manufacture of other furniture"
                        }
                    ]
                },
                {
                    "code": "23.02",
                    "name_cn": "珠宝首饰及相关物品的制造",
                    "name_en": "Manufacture of jewellery, bijouterie and related articles",
                    "minor_categories": [
                        {
                            "code": "23.02.01",
                            "name_cn": "硬币的压制",
                            "name_en": "Striking of coins"
                        },
                        {
                            "code": "23.02.02",
                            "name_cn": "珠宝首饰及相关物品的制造",
                            "name_en": "Manufacture of jewellery and related articles"
                        },
                        {
                            "code": "23.02.03",
                            "name_cn": "仿真首饰及相关物品的制造",
                            "name_en": "Manufacture of imitation jewellery and related articles"
                        }
                    ]
                },
                {
                    "code": "23.03",
                    "name_cn": "乐器的制造",
                    "name_en": "Manufacture of musical instruments",
                    "minor_categories": [
                        {
                            "code": "23.03.00",
                            "name_cn": "乐器的制造",
                            "name_en": "Manufacture of musical instruments"
                        }
                    ]
                },
                {
                    "code": "23.04",
                    "name_cn": "体育用品的制造",
                    "name_en": "Manufacture of sports goods",
                    "minor_categories": [
                        {
                            "code": "23.04.00",
                            "name_cn": "体育用品的制造",
                            "name_en": "Manufacture of sports goods"
                        }
                    ]
                },
                {
                    "code": "23.05",
                    "name_cn": "游戏用品及玩具的制造",
                    "name_en": "Manufacture of games and toys",
                    "minor_categories": [
                        {
                            "code": "23.05.00",
                            "name_cn": "游戏用品及玩具的制造",
                            "name_en": "Manufacture of games and toys"
                        }
                    ]
                },
                {
                    "code": "23.06",
                    "name_cn": "医疗及牙科器械和用品的制造",
                    "name_en": "Manufacture of medical and dental instruments and supplies",
                    "minor_categories": [
                        {
                            "code": "23.06.00",
                            "name_cn": "医疗及牙科器械和用品的制造",
                            "name_en": "Manufacture of medical and dental instruments and supplies"
                        }
                    ]
                },
                {
                    "code": "23.07",
                    "name_cn": "未另分类的制造业",
                    "name_en": "Manufacturing n.e.c.",
                    "minor_categories": [
                        {
                            "code": "23.07.01",
                            "name_cn": "扫帚和刷子的制造",
                            "name_en": "Manufacture of brooms and brushes"
                        },
                        {
                            "code": "23.07.02",
                            "name_cn": "其他未另分类的制造业",
                            "name_en": "Other manufacturing n.e.c."
                        }
                    ]
                },
                {
                    "code": "23.08",
                    "name_cn": "其他设备的修理",
                    "name_en": "Repair of other equipment",
                    "minor_categories": [
                        {
                            "code": "23.08.00",
                            "name_cn": "其他设备的修理",
                            "name_en": "Repair of other equipment"
                        }
                    ]
                }
            ]
        },
        {
            "code": "24",
            "name_cn": "回收业",
            "name_en": "Recycling",
            "sub_categories": [
                {
                    "code": "24.01",
                    "name_cn": "材料回收",
                    "name_en": "Materials recovery",
                    "minor_categories": [
                        {
                            "code": "24.01.01",
                            "name_cn": "残骸拆除",
                            "name_en": "Dismantling of wrecks"
                        },
                        {
                            "code": "24.01.02",
                            "name_cn": "材料的分类回收",
                            "name_en": "Recovery of sorted materials"
                        }
                    ]
                }
            ]
        },
        {
            "code": "25",
            "name_cn": "供电业",
            "name_en": "Electricity supply",
            "sub_categories": [
                {
                    "code": "25.01",
                    "name_cn": "发电、输电和配电",
                    "name_en": "Electric power generation, transmission and distribution",
                    "minor_categories": [
                        {
                            "code": "25.01.01",
                            "name_cn": "发电",
                            "name_en": "Production of electricity"
                        },
                        {
                            "code": "25.01.02",
                            "name_cn": "电力传输",
                            "name_en": "Transmission of electricity"
                        },
                        {
                            "code": "25.01.03",
                            "name_cn": "配电",
                            "name_en": "Distribution of electricity"
                        },
                        {
                            "code": "25.01.04",
                            "name_cn": "售电",
                            "name_en": "Trade of electricity"
                        }
                    ]
                }
            ]
        },
        {
            "code": "26",
            "name_cn": "供气业",
            "name_en": "Gas supply",
            "sub_categories": [
                {
                    "code": "26.01",
                    "name_cn": "燃气的生产，燃气通过管道的配送",
                    "name_en": "Manufacture of gas; distribution of gaseous fuels through mains",
                    "minor_categories": [
                        {
                            "code": "26.01.01",
                            "name_cn": "燃气的生产",
                            "name_en": "Manufacture of gas"
                        },
                        {
                            "code": "26.01.02",
                            "name_cn": "燃气的管道分配",
                            "name_en": "Distribution of gaseous fuels through mains"
                        },
                        {
                            "code": "26.01.03",
                            "name_cn": "通过管道售气",
                            "name_en": "Trade of gas through mains"
                        }
                    ]
                }
            ]
        },
        {
            "code": "27",
            "name_cn": "供水业",
            "name_en": "Water supply",
            "sub_categories": [
                {
                    "code": "27.01",
                    "name_cn": "蒸汽和空调的供应",
                    "name_en": "Steam and air conditioning supply",
                    "minor_categories": [
                        {
                            "code": "27.01.00",
                            "name_cn": "蒸汽和空调的供应",
                            "name_en": "Steam and air conditioning supply"
                        }
                    ]
                },
                {
                    "code": "27.02",
                    "name_cn": "集水、处理和供水",
                    "name_en": "Water collection, treatment and supply",
                    "minor_categories": [
                        {
                            "code": "27.02.00",
                            "name_cn": "集水、处理和供水",
                            "name_en": "Water collection, treatment and supply"
                        }
                    ]
                }
            ]
        },
        {
            "code": "28",
            "name_cn": "建设业",
            "name_en": "Construction",
            "sub_categories": [
                {
                    "code": "28.01",
                    "name_cn": "建设项目的开发",
                    "name_en": "Development of building projects",
                    "minor_categories": [
                        {
                            "code": "28.01.00",
                            "name_cn": "建设项目的开发",
                            "name_en": "Development of building projects"
                        }
                    ]
                },
                {
                    "code": "28.02",
                    "name_cn": "住宅及非住宅建筑的建设",
                    "name_en": "Construction of residential and non-residential buildings",
                    "minor_categories": [
                        {
                            "code": "28.02.00",
                            "name_cn": "住宅及非住宅建筑的建设",
                            "name_en": "Construction of residential and non-residential buildings"
                        }
                    ]
                },
                {
                    "code": "28.03",
                    "name_cn": "道路和铁路的建设",
                    "name_en": "Construction of roads and railways",
                    "minor_categories": [
                        {
                            "code": "28.03.01",
                            "name_cn": "道路和高速公路的建设",
                            "name_en": "Construction of roads and motorways"
                        },
                        {
                            "code": "28.03.02",
                            "name_cn": "铁路和地下铁路的建设",
                            "name_en": "Construction of railways and underground railways"
                        },
                        {
                            "code": "28.03.03",
                            "name_cn": "桥梁和隧道的建设",
                            "name_en": "Construction of bridges and tunnels"
                        }
                    ]
                },
                {
                    "code": "28.04",
                    "name_cn": "公用设施项目的建设",
                    "name_en": "Construction of utility projects",
                    "minor_categories": [
                        {
                            "code": "28.04.01",
                            "name_cn": "流体输送用公用设施项目的建设",
                            "name_en": "Construction of utility projects for fluids"
                        },
                        {
                            "code": "28.04.02",
                            "name_cn": "电力和电信用公用设施项目的建设",
                            "name_en": "Construction of utility projects for electricity and telecommunications"
                        }
                    ]
                },
                {
                    "code": "28.05",
                    "name_cn": "其他土木工程项目的建设",
                    "name_en": "Construction of other civil engineering projects",
                    "minor_categories": [
                        {
                            "code": "28.05.01",
                            "name_cn": "水利工程的建设",
                            "name_en": "Construction of water projects"
                        },
                        {
                            "code": "28.05.02",
                            "name_cn": "其他未另分类的土木工程项目的建设",
                            "name_en": "Construction of other civil engineering projects n.e.c."
                        }
                    ]
                },
                {
                    "code": "28.06",
                    "name_cn": "拆除及场地准备",
                    "name_en": "Demolition and site preparation",
                    "minor_categories": [
                        {
                            "code": "28.06.01",
                            "name_cn": "拆除",
                            "name_en": "Demolition"
                        },
                        {
                            "code": "28.06.02",
                            "name_cn": "场地准备",
                            "name_en": "Site preparation"
                        },
                        {
                            "code": "28.06.03",
                            "name_cn": "钻孔和钻探测试",
                            "name_en": "Test drilling and boring"
                        }
                    ]
                },
                {
                    "code": "28.07",
                    "name_cn": "电气、管道和其他建筑安装活动",
                    "name_en": "Electrical, plumbing and other construction installation activities",
                    "minor_categories": [
                        {
                            "code": "28.07.01",
                            "name_cn": "电气安装",
                            "name_en": "Electrical installation"
                        },
                        {
                            "code": "28.07.02",
                            "name_cn": "管道、供暖和空调系统的安装",
                            "name_en": "Plumbing, heat and air-conditioning installation"
                        },
                        {
                            "code": "28.07.03",
                            "name_cn": "其他建筑安装",
                            "name_en": "Other construction installation"
                        }
                    ]
                },
                {
                    "code": "28.08",
                    "name_cn": "建筑装修和装饰",
                    "name_en": "Building completion and finishing",
                    "minor_categories": [
                        {
                            "code": "28.08.01",
                            "name_cn": "抹灰",
                            "name_en": "Plastering"
                        },
                        {
                            "code": "28.08.02",
                            "name_cn": "木工安装",
                            "name_en": "Joinery installation"
                        },
                        {
                            "code": "28.08.03",
                            "name_cn": "地面和墙壁覆盖",
                            "name_en": "Floor and wall covering"
                        },
                        {
                            "code": "28.08.04",
                            "name_cn": "涂装和玻璃安装",
                            "name_en": "Painting and glazing"
                        },
                        {
                            "code": "28.08.05",
                            "name_cn": "其他建筑装修和装饰",
                            "name_en": "Other building completion and finishing"
                        }
                    ]
                },
                {
                    "code": "28.09",
                    "name_cn": "其他专业建筑活动",
                    "name_en": "Other specialised construction activities",
                    "minor_categories": [
                        {
                            "code": "28.09.01",
                            "name_cn": "屋顶工程",
                            "name_en": "Roofing activities"
                        },
                        {
                            "code": "28.09.02",
                            "name_cn": "其他未另分类的专业建筑活动",
                            "name_en": "Other specialised construction activities n.e.c."
                        }
                    ]
                }
            ]
        },
        {
            "code": "29",
            "name_cn": "批发和零售业；汽车、摩托、个人及家庭用品修理业",
            "name_en": "Wholesale and retail trade; Repair of motor vehicles, motorcycles and personal and household goods",
            "sub_categories": [
            ]
        },
        {
            "code": "30",
            "name_cn": "宾馆及餐馆",
            "name_en": "Hotels and restaurants",
            "sub_categories": [
            ]
        },
        {
            "code": "31",
            "name_cn": "运输、仓储和通信业",
            "name_en": "Transport, storage and communication",
            "sub_categories": [
            ]
        },
        {
            "code": "32",
            "name_cn": "金融中介、房地产和租赁",
            "name_en": "Financial intermediation; real estate; renting",
            "sub_categories": [
            ]
        },
        {
            "code": "33",
            "name_cn": "信息技术",
            "name_en": "Information technology",
            "sub_categories": [
            ]
        },
        {
            "code": "34",
            "name_cn": "工程服务",
            "name_en": "Engineering services",
            "sub_categories": [
            ]
        },
        {
            "code": "35",
            "name_cn": "其他服务",
            "name_en": "Other services",
            "sub_categories": [
            ]
        },
        {
            "code": "36",
            "name_cn": "公共行政管理",
            "name_en": "Public administration",
            "sub_categories": [
            ]
        },
        {
            "code": "37",
            "name_cn": "教育",
            "name_en": "Education",
            "sub_categories": [
            ]
        },
        {
            "code": "38",
            "name_cn": "健康和社会工作",
            "name_en": "Health and social work",
            "sub_categories": [
            ]
        },
        {
            "code": "39",
            "name_cn": "其他社会服务",
            "name_en": "Other social services",
            "sub_categories": [
            ]
        }
    ]
}


# ============ 行业-认证范围映射 ============

INDUSTRY_SCOPE_MAPPING = {
    "system_integration": ["33"],  # 信息技术
    "software_development": ["33"],  # 信息技术
    "construction": ["28"],  # 建设业
    "steel_structure": ["28", "17"],  # 建设业 + 基础金属及金属制品
    "archive_digitalization": ["33", "35"],  # 信息技术 + 其他服务
    "intelligent_manufacturing": ["17", "18"],  # 基础金属及金属制品 + 机械及设备
    "food_production": ["03"],  # 食品、饮料和烟草
    "electromanical": ["18"],  # 机械及设备
    "intelligent_tech": ["33"],  # 信息技术
    "property_management": ["35", "39"],  # 其他服务 + 其他社会服务
    "labor_dispatch": ["35"],  # 其他服务
}


# ============ 辅助函数 ============

def _get_category_by_code(code: str):
    """根据大类代码获取分类数据"""
    for cat in CERTIFICATION_SCOPE_DATA["categories"]:
        if cat["code"] == code:
            return cat
    return None


def _build_category_index():
    """构建大类代码索引"""
    index = {}
    for cat in CERTIFICATION_SCOPE_DATA["categories"]:
        index[cat["code"]] = cat
    return index


CATEGORY_INDEX = _build_category_index()


# ============ API接口 ============

@router.get("/categories", response_model=List[CategoryBrief], summary="获取39大类列表")
async def get_categories():
    """获取认证范围39大类列表

    返回每个大类的代码、中英文名称及中类数量。
    """
    result = []
    for cat in CERTIFICATION_SCOPE_DATA["categories"]:
        result.append(CategoryBrief(
            code=cat["code"],
            name_cn=cat["name_cn"],
            name_en=cat["name_en"],
            sub_category_count=len(cat["sub_categories"])
        ))
    return result


@router.get("/category/{code}", response_model=CategoryDetail, summary="获取大类详情")
async def get_category_detail(code: str):
    """获取大类详情（含中类和小类）

    参数:
        code: 大类代码，格式为 "01", "02", ... "39"
    """
    cat = _get_category_by_code(code)
    if not cat:
        raise HTTPException(status_code=404, detail=f"未找到大类代码: {code}")

    sub_details = []
    for sub in cat["sub_categories"]:
        minors = [
            MinorCategory(code=m["code"], name_cn=m["name_cn"], name_en=m["name_en"])
            for m in sub["minor_categories"]
        ]
        sub_details.append(SubCategoryDetail(
            code=sub["code"],
            name_cn=sub["name_cn"],
            name_en=sub["name_en"],
            minor_categories=minors
        ))

    return CategoryDetail(
        code=cat["code"],
        name_cn=cat["name_cn"],
        name_en=cat["name_en"],
        sub_categories=sub_details
    )


@router.get("/search", response_model=List[SearchResult], summary="搜索认证范围")
async def search_scope(
    keyword: str = Query(..., description="搜索关键词"),
    level: str = Query("all", description="搜索层级: all/category/sub_category/minor"),
):
    """搜索认证范围（支持中英文搜索）

    参数:
        keyword: 搜索关键词，支持中文名称或英文名称
        level: 搜索层级过滤
            - all: 搜索所有层级
            - category: 仅搜索大类
            - sub_category: 仅搜索中类
            - minor: 仅搜索小类
    """
    keyword_lower = keyword.lower()
    results = []

    for cat in CERTIFICATION_SCOPE_DATA["categories"]:
        # 搜索大类
        if level in ("all", "category"):
            if (keyword_lower in cat["name_cn"].lower() or
                keyword_lower in cat["name_en"].lower() or
                keyword_lower in cat["code"]):
                results.append(SearchResult(
                    level="category",
                    code=cat["code"],
                    name_cn=cat["name_cn"],
                    name_en=cat["name_en"],
                    parent_code=None
                ))

        # 搜索中类
        if level in ("all", "sub_category"):
            for sub in cat["sub_categories"]:
                if (keyword_lower in sub["name_cn"].lower() or
                    keyword_lower in sub["name_en"].lower() or
                    keyword_lower in sub["code"]):
                    results.append(SearchResult(
                        level="sub_category",
                        code=sub["code"],
                        name_cn=sub["name_cn"],
                        name_en=sub["name_en"],
                        parent_code=cat["code"]
                    ))

        # 搜索小类
        if level in ("all", "minor"):
            for sub in cat["sub_categories"]:
                for minor in sub["minor_categories"]:
                    if (keyword_lower in minor["name_cn"].lower() or
                        keyword_lower in minor["name_en"].lower() or
                        keyword_lower in minor["code"]):
                        results.append(SearchResult(
                            level="minor",
                            code=minor["code"],
                            name_cn=minor["name_cn"],
                            name_en=minor["name_en"],
                            parent_code=sub["code"]
                        ))

    return results


@router.get("/tree", summary="获取完整分类树")
async def get_full_tree():
    """获取完整的39大类分类树（含所有中类和小类）

    返回完整的层级结构数据，包含39个大类、143个中类和325个小类。
    """
    return CERTIFICATION_SCOPE_DATA


@router.get("/match-industry", response_model=IndustryMatchResult, summary="根据行业代码匹配认证范围")
async def match_industry(
    industry_code: str = Query(..., description="行业代码"),
):
    """根据行业代码匹配推荐的认证范围大类

    参数:
        industry_code: 行业代码，如 system_integration, construction 等

    支持的行业代码:
        - system_integration: 系统集成
        - software_development: 软件开发
        - construction: 建设业
        - steel_structure: 钢结构
        - archive_digitalization: 档案数字化
        - intelligent_manufacturing: 智能制造
        - food_production: 食品生产
        - electromanical: 机电
        - intelligent_tech: 智能科技
        - property_management: 物业管理
        - labor_dispatch: 劳务派遣
    """
    matched_codes = INDUSTRY_SCOPE_MAPPING.get(industry_code)
    if not matched_codes:
        raise HTTPException(
            status_code=404,
            detail=f"未找到行业代码: {industry_code}，支持的行业代码: {list(INDUSTRY_SCOPE_MAPPING.keys())}"
        )

    matched_categories = []
    for code in matched_codes:
        cat = _get_category_by_code(code)
        if cat:
            matched_categories.append(CategoryBrief(
                code=cat["code"],
                name_cn=cat["name_cn"],
                name_en=cat["name_en"],
                sub_category_count=len(cat["sub_categories"])
            ))

    return IndustryMatchResult(
        industry_code=industry_code,
        matched_categories=matched_categories
    )
