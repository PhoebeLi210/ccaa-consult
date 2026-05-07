import React from 'react';
import { Tag, Badge } from 'antd';
import { CheckCircleFilled, ClockCircleFilled, EditFilled } from '@ant-design/icons';

/** 确认状态类型 */
type ConfirmStatus = 'confirmed' | 'pending' | 'draft';

/** 确认状态徽标属性 */
interface ConfirmBadgeProps {
  /** 确认状态 */
  status: ConfirmStatus;
  /** 是否显示文字，默认true */
  showText?: boolean;
}

/** 状态配置映射 */
const statusConfig: Record<
  ConfirmStatus,
  { color: string; text: string; icon: React.ReactNode }
> = {
  confirmed: {
    color: 'success',
    text: '已确认',
    icon: <CheckCircleFilled />,
  },
  pending: {
    color: 'warning',
    text: '待确认',
    icon: <ClockCircleFilled />,
  },
  draft: {
    color: 'default',
    text: '草稿',
    icon: <EditFilled />,
  },
};

/**
 * 确认状态徽标组件
 * 以Tag或Badge形式展示文档的确认状态
 * 三种状态：已确认(green)、待确认(orange)、草稿(gray)
 */
const ConfirmBadge: React.FC<ConfirmBadgeProps> = ({
  status,
  showText = true,
}) => {
  const config = statusConfig[status] || statusConfig.draft;

  return (
    <Tag
      color={config.color}
      icon={config.icon}
      style={{ fontSize: 11, padding: '0 6px', margin: 0 }}
    >
      {showText && config.text}
    </Tag>
  );
};

export default ConfirmBadge;
